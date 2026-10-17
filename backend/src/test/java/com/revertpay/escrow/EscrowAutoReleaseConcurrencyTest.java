package com.revertpay.escrow;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.account.OwnerType;
import com.revertpay.ledger.LedgerEntry;
import com.revertpay.ledger.LedgerEntryRepository;
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
import java.util.List;
import java.util.concurrent.*;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class EscrowAutoReleaseConcurrencyTest {

    @Autowired
    private EscrowService escrowService;

    @Autowired
    private EscrowRepository escrowRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private LedgerEntryRepository ledgerEntryRepository;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private PlatformTransactionManager transactionManager;

    @Test
    void buyerConfirmationAndAutoReleaseShouldNotDuplicatePayment()
            throws Exception {

        long unique = System.nanoTime();

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        Long[] ids = transactions.execute(status -> {

            User buyer = new User(
                    "Race Buyer " + unique,
                    "racebuyer" + unique + "@example.com",
                    "test-password"
            );
            buyer.setRole(Role.BUYER);
            buyer = userRepository.saveAndFlush(buyer);

            User seller = new User(
                    "Race Seller " + unique,
                    "raceseller" + unique + "@example.com",
                    "test-password"
            );
            seller.setRole(Role.SELLER);
            seller = userRepository.saveAndFlush(seller);

            accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.USER,
                            buyer.getId(),
                            "ACC" + buyer.getId()
                    )
            );

            accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.USER,
                            seller.getId(),
                            "ACC" + seller.getId()
                    )
            );

            // Ensure the system escrow account exists.
            accountRepository.findByAccountNumber("ESCROW_HOLDING")
                    .orElseThrow(() -> new IllegalStateException(
                            "ESCROW_HOLDING account must already exist"
                    ));

            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Buyer vs automatic release race");
            escrow.setAmount(new BigDecimal("100.00"));
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now().minusMinutes(10));
            escrow.setShippedAt(LocalDateTime.now().minusMinutes(10));

            // Make automatic release eligible immediately.
            escrow.setAutoReleaseAt(LocalDateTime.now().minusMinutes(5));

            escrow.setIdempotencyKey("release-race-" + unique);
            escrow.setRequestHash("release-race-test-" + unique);

            escrow = escrowRepository.saveAndFlush(escrow);

            return new Long[]{
                    buyer.getId(),
                    escrow.getId()
            };
        });

        assertNotNull(ids);

        Long buyerId = ids[0];
        Long escrowId = ids[1];

        String buyerToken = jwtService.generateToken(
                userRepository.findById(buyerId).orElseThrow()
        );

        ExecutorService executor = Executors.newFixedThreadPool(2);
        CountDownLatch ready = new CountDownLatch(2);
        CountDownLatch start = new CountDownLatch(1);

        Callable<Boolean> buyerConfirmation = () -> {
            ready.countDown();

            if (!start.await(10, TimeUnit.SECONDS)) {
                throw new TimeoutException("Start timed out");
            }

            try {
                escrowService.confirmEscrow(escrowId, buyerToken);
                return true;
            } catch (RuntimeException ex) {
                return false;
            }
        };

        Callable<Boolean> automaticRelease = () -> {
            ready.countDown();

            if (!start.await(10, TimeUnit.SECONDS)) {
                throw new TimeoutException("Start timed out");
            }

            try {
                escrowService.autoReleaseEscrow(escrowId);
                return true;
            } catch (RuntimeException ex) {
                return false;
            }
        };

        try {
            Future<Boolean> buyerFuture =
                    executor.submit(buyerConfirmation);

            Future<Boolean> automaticFuture =
                    executor.submit(automaticRelease);

            assertTrue(
                    ready.await(10, TimeUnit.SECONDS),
                    "Both operations should be ready"
            );

            start.countDown();

            // The automatic-release method may return normally if it
            // discovers that the buyer already released the escrow.
            buyerFuture.get(30, TimeUnit.SECONDS);
            automaticFuture.get(30, TimeUnit.SECONDS);

        } finally {
            start.countDown();
            executor.shutdown();

            assertTrue(
                    executor.awaitTermination(30, TimeUnit.SECONDS),
                    "Both operations should finish"
            );
        }

        EscrowTransaction finalEscrow =
                escrowRepository.findById(escrowId).orElseThrow();

        assertEquals(
                EscrowStatus.RELEASED,
                finalEscrow.getStatus(),
                "The escrow should finish as RELEASED"
        );

        List<LedgerEntry> entries = ledgerEntryRepository.findAll()
                .stream()
                .filter(entry ->
                        entry.getReference_id() == escrowId)
                .toList();

        assertEquals(
                2,
                entries.size(),
                "Only one release should create two ledger entries"
        );
    }
}