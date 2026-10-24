package com.revertpay.ledger;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.account.OwnerType;
import com.revertpay.escrow.EscrowRepository;
import com.revertpay.escrow.EscrowService;
import com.revertpay.escrow.EscrowStatus;
import com.revertpay.escrow.EscrowTransaction;
import com.revertpay.security.JwtService;
import com.revertpay.user.Role;
import com.revertpay.user.User;
import com.revertpay.user.UserRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class EscrowConcurrentReleaseTest {

    @Autowired
    private EscrowService escrowService;

    @Autowired
    private EscrowRepository escrowRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private LedgerEntryRepository ledgerEntryRepository;

    @Autowired
    private LedgerService ledgerService;

    @Autowired
    private PlatformTransactionManager transactionManager;

    @Test
    void concurrentReleaseShouldNotDuplicateLedgerEntries() throws Exception {

        long unique = System.nanoTime();
        long referenceId = Math.abs(unique);

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        TestData data = transactions.execute(status -> {

            User buyer = new User(
                    "Test Buyer " + unique,
                    "buyer" + unique + "@example.com",
                    "test-password"
            );
            buyer.setRole(Role.BUYER);
            buyer = userRepository.saveAndFlush(buyer);

            User seller = new User(
                    "Test Seller " + unique,
                    "seller" + unique + "@example.com",
                    "test-password"
            );
            seller.setRole(Role.SELLER);
            seller = userRepository.saveAndFlush(seller);

            accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.USER,
                            seller.getId(),
                            "ACC" + seller.getId()
                    )
            );
            BigDecimal transferAmount = new BigDecimal("100.00");

            Account buyerAccount = accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.USER,
                            buyer.getId(),
                            "ACC" + buyer.getId()
                    )
            );

            ledgerService.doCredit(
                    buyerAccount,
                    transferAmount,
                    referenceId + 1
            );

            Account holding = accountRepository
                    .findByAccountNumber("ESCROW_HOLDING")
                    .orElseThrow(() -> new IllegalStateException(
                            "ESCROW_HOLDING account must already exist"
                    ));

            ledgerService.transfer(
                    buyerAccount,
                    holding,
                    transferAmount,
                    referenceId + 2
            );


            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Concurrent release test");
            escrow.setAmount(transferAmount);
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now());
            escrow.setShippedAt(LocalDateTime.now());
            escrow.setIdempotencyKey("concurrent-" + unique);
            escrow.setRequestHash("concurrent-test-" + unique);

            escrow = escrowRepository.saveAndFlush(escrow);

            return new TestData(
                    buyer.getId(),
                    escrow.getId()
            );
        });

        assertNotNull(data);

        User buyer = userRepository.findById(data.buyerId())
                .orElseThrow();

        String buyerToken = jwtService.generateToken(buyer);

        int requestCount = 50;
        ExecutorService executor =
                Executors.newFixedThreadPool(requestCount);

        CountDownLatch ready = new CountDownLatch(requestCount);
        CountDownLatch start = new CountDownLatch(1);

        Callable<Boolean> release = () -> {
            ready.countDown();

            if (!start.await(10, TimeUnit.SECONDS)) {
                throw new TimeoutException("Concurrent start timed out");
            }

            try {
                escrowService.confirmEscrow(
                        data.escrowId(),
                        buyerToken
                );
                return true;
            } catch (RuntimeException ex) {
                return false;
            }
        };

        try {
            List<Future<Boolean>> futures = new ArrayList<>();

            for (int i = 0; i < requestCount; i++) {
                futures.add(executor.submit(release));
            }

            assertTrue(
                    ready.await(10, TimeUnit.SECONDS),
                    "All release attempts should be ready"
            );

            start.countDown();

            int successes = 0;

            for (Future<Boolean> future : futures) {
                if (future.get(60, TimeUnit.SECONDS)) {
                    successes++;
                }
            }

            assertEquals(
                    1,
                    successes,
                    "Exactly one release attempt should succeed"
            );

        } finally {
            start.countDown();
            executor.shutdown();

            assertTrue(
                    executor.awaitTermination(60, TimeUnit.SECONDS),
                    "All worker threads should finish"
            );
        }

        EscrowTransaction finalEscrow =
                escrowRepository.findById(data.escrowId())
                        .orElseThrow();

        assertEquals(EscrowStatus.RELEASED, finalEscrow.getStatus());

        List<LedgerEntry> entries = ledgerEntryRepository.findAll()
                .stream()
                .filter(entry ->
                        entry.getReference_id() == data.escrowId())
                .toList();

        assertEquals(
                2,
                entries.size(),
                "Exactly one debit and one credit should be recorded"
        );

        assertEquals(
                1,
                entries.stream()
                        .filter(entry -> entry.getType() == Type.DEBIT)
                        .count()
        );

        assertEquals(
                1,
                entries.stream()
                        .filter(entry -> entry.getType() == Type.CREDIT)
                        .count()
        );
    }

    private record TestData(
            Long buyerId,
            Long escrowId
    ) {}
}

