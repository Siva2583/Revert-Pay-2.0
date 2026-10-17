package com.revertpay.ledger;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.account.OwnerType;
import com.revertpay.escrow.EscrowRepository;
import com.revertpay.escrow.EscrowService;
import com.revertpay.escrow.EscrowStatus;
import com.revertpay.escrow.EscrowTransaction;
import com.revertpay.user.Role;
import com.revertpay.user.User;
import com.revertpay.user.UserRepository;
import com.revertpay.security.JwtService;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.transaction.PlatformTransactionManager;

import java.math.BigDecimal;
import java.time.LocalDateTime;
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
    private PlatformTransactionManager transactionManager;

    @Test
    void concurrentReleaseShouldNotDuplicateLedgerEntries() throws Exception {

        long unique = System.nanoTime();

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        // Arrange: create buyer, seller, accounts, and escrow.
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

            Account sellerAccount = accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.USER,
                            seller.getId(),
                            "ACC" + seller.getId()
                    )
            );

            Account escrowAccount = accountRepository
                    .findByAccountNumber("ESCROW_HOLDING")
                    .orElseThrow(() -> new IllegalStateException(
                            "ESCROW_HOLDING account must already exist"
                    ));

            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Concurrent release test");
            escrow.setAmount(new BigDecimal("100.00"));
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now());
            escrow.setShippedAt(LocalDateTime.now());
            escrow.setIdempotencyKey("concurrent-" + unique);
            escrow.setRequestHash("concurrent-test-" + unique);

            escrow = escrowRepository.saveAndFlush(escrow);

            return new TestData(
                    buyer.getId(),
                    seller.getId(),
                    escrow.getId()
            );
        });

        assertNotNull(data);

        String buyerToken = jwtService.generateToken(
                userRepository.findById(data.buyerId()).orElseThrow()
        );

        long entriesBefore = ledgerEntryRepository.count();

//        ExecutorService executor = Executors.newFixedThreadPool(2);
//        CountDownLatch ready = new CountDownLatch(2);
//        CountDownLatch start = new CountDownLatch(1);
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
                escrowService.confirmEscrow(data.escrowId(), buyerToken);
                return true;
            } catch (RuntimeException ex) {
                return false;
            }
        };

        try {
            List<Future<Boolean>> futures = new java.util.ArrayList<>();

            for (int i = 0; i < requestCount; i++) {
                futures.add(executor.submit(release));
            }

            assertTrue(
                    ready.await(10, TimeUnit.SECONDS),
                    "All 50 release attempts should be ready"
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
                    "Exactly one of the 50 release attempts should succeed"
            );

        } finally {
            start.countDown();
            executor.shutdown();

            assertTrue(
                    executor.awaitTermination(60, TimeUnit.SECONDS),
                    "All worker threads should finish"
            );
        }

        // Verify final persisted state.
        EscrowTransaction finalEscrow =
                escrowRepository.findById(data.escrowId()).orElseThrow();

        assertEquals(EscrowStatus.RELEASED, finalEscrow.getStatus());

        List<LedgerEntry> entries = ledgerEntryRepository.findAll()
                .stream()
                .filter(entry -> entry.getReference_id() == data.escrowId())
                .toList();

//        assertEquals(
//                2,
//                entries.size(),
//                "Exactly one debit and one credit should be recorded for this escrow"
//        );

        assertEquals(
                2,
                entries.size(),
                "Exactly one debit and one credit should be recorded"
        );


    }

    private record TestData(
            Long buyerId,
            Long sellerId,
            Long escrowId
    ) {}
}