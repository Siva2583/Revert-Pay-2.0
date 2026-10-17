package com.revertpay.escrow;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.account.OwnerType;
import com.revertpay.ledger.LedgerEntry;
import com.revertpay.ledger.LedgerEntryRepository;
import com.revertpay.user.Role;
import com.revertpay.user.User;
import com.revertpay.user.UserRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.transaction.PlatformTransactionManager;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class EscrowAutoReleaseTest {

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
    private PlatformTransactionManager transactionManager;

    @Test
    void overdueShippedEscrowShouldAutoRelease() {

        long unique = System.nanoTime();

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        TestData data = transactions.execute(status -> {

            User buyer = new User(
                    "Auto Buyer " + unique,
                    "autobuyer" + unique + "@example.com",
                    "test-password"
            );
            buyer.setRole(Role.BUYER);
            buyer = userRepository.saveAndFlush(buyer);

            User seller = new User(
                    "Auto Seller " + unique,
                    "autoseller" + unique + "@example.com",
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

            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Automatic release test");
            escrow.setAmount(new BigDecimal("100.00"));
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now().minusMinutes(10));
            escrow.setShippedAt(LocalDateTime.now().minusMinutes(10));
            escrow.setAutoReleaseAt(LocalDateTime.now().minusMinutes(5));
            escrow.setIdempotencyKey("auto-release-" + unique);
            escrow.setRequestHash("auto-release-test-" + unique);

            escrow = escrowRepository.saveAndFlush(escrow);

            return new TestData(escrow.getId());
        });

        assertNotNull(data);

        long entriesBefore = ledgerEntryRepository.count();

        // Execute the automatic-release service method.
        escrowService.autoReleaseEscrow(data.escrowId());

        EscrowTransaction released =
                escrowRepository.findById(data.escrowId()).orElseThrow();

        assertEquals(
                EscrowStatus.RELEASED,
                released.getStatus(),
                "Overdue shipped escrow should be released"
        );

        List<LedgerEntry> entries = ledgerEntryRepository.findAll()
                .stream()
                .filter(entry ->
                        entry.getReference_id() == data.escrowId())
                .toList();

        assertEquals(
                2,
                entries.size(),
                "Automatic release should create exactly two ledger entries"
        );

        assertEquals(
                entriesBefore + 2,
                ledgerEntryRepository.count(),
                "Exactly two ledger entries should be added"
        );
    }
    @Test
    void escrowBeforeDeadlineShouldNotBeReleased() {

        long unique = System.nanoTime();

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        Long escrowId = transactions.execute(status -> {

            User buyer = new User(
                    "Future Buyer " + unique,
                    "futurebuyer" + unique + "@example.com",
                    "test-password"
            );
            buyer.setRole(Role.BUYER);
            buyer = userRepository.saveAndFlush(buyer);

            User seller = new User(
                    "Future Seller " + unique,
                    "futureseller" + unique + "@example.com",
                    "test-password"
            );
            seller.setRole(Role.SELLER);
            seller = userRepository.saveAndFlush(seller);

            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Future deadline test");
            escrow.setAmount(new BigDecimal("100.00"));
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now());
            escrow.setShippedAt(LocalDateTime.now());
            escrow.setAutoReleaseAt(LocalDateTime.now().plusMinutes(5));
            escrow.setIdempotencyKey("future-release-" + unique);
            escrow.setRequestHash("future-release-test-" + unique);

            return escrowRepository.saveAndFlush(escrow).getId();
        });

        assertNotNull(escrowId);

        escrowService.autoReleaseEscrow(escrowId);

        EscrowTransaction unchanged =
                escrowRepository.findById(escrowId).orElseThrow();

        assertEquals(
                EscrowStatus.SHIPPED,
                unchanged.getStatus(),
                "Escrow must remain SHIPPED before its deadline"
        );
    }
    @Test
    void repeatedAutoReleaseShouldNotCreateDuplicateLedgerEntries() {

        long unique = System.nanoTime();

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        Long escrowId = transactions.execute(status -> {

            User buyer = new User(
                    "Repeat Buyer " + unique,
                    "repeatbuyer" + unique + "@example.com",
                    "test-password"
            );
            buyer.setRole(Role.BUYER);
            buyer = userRepository.saveAndFlush(buyer);

            User seller = new User(
                    "Repeat Seller " + unique,
                    "repeatseller" + unique + "@example.com",
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

            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Repeated release test");
            escrow.setAmount(new BigDecimal("100.00"));
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now().minusMinutes(10));
            escrow.setShippedAt(LocalDateTime.now().minusMinutes(10));
            escrow.setAutoReleaseAt(LocalDateTime.now().minusMinutes(5));
            escrow.setIdempotencyKey("repeat-release-" + unique);
            escrow.setRequestHash("repeat-release-test-" + unique);

            return escrowRepository.saveAndFlush(escrow).getId();
        });

        assertNotNull(escrowId);

        // First release.
        escrowService.autoReleaseEscrow(escrowId);

        List<LedgerEntry> firstReleaseEntries =
                ledgerEntryRepository.findAll()
                        .stream()
                        .filter(entry ->
                                entry.getReference_id() == escrowId)
                        .toList();

        assertEquals(
                2,
                firstReleaseEntries.size(),
                "First release should create exactly two ledger entries"
        );

        // Second release attempt.
        escrowService.autoReleaseEscrow(escrowId);

        EscrowTransaction finalEscrow =
                escrowRepository.findById(escrowId).orElseThrow();

        List<LedgerEntry> finalEntries =
                ledgerEntryRepository.findAll()
                        .stream()
                        .filter(entry ->
                                entry.getReference_id() == escrowId)
                        .toList();

        assertEquals(
                EscrowStatus.RELEASED,
                finalEscrow.getStatus()
        );

        assertEquals(
                2,
                finalEntries.size(),
                "Repeated release must not create additional ledger entries"
        );
    }
    @Test
    void shippedEscrowWithoutDeadlineShouldNotBeReleased() {

        long unique = System.nanoTime();

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        Long escrowId = transactions.execute(status -> {

            User buyer = new User(
                    "No Deadline Buyer " + unique,
                    "nodeadlinebuyer" + unique + "@example.com",
                    "test-password"
            );
            buyer.setRole(Role.BUYER);
            buyer = userRepository.saveAndFlush(buyer);

            User seller = new User(
                    "No Deadline Seller " + unique,
                    "nodeadlineseller" + unique + "@example.com",
                    "test-password"
            );
            seller.setRole(Role.SELLER);
            seller = userRepository.saveAndFlush(seller);

            EscrowTransaction escrow = new EscrowTransaction();
            escrow.setBuyer(buyer);
            escrow.setSeller(seller);
            escrow.setItemName("Missing deadline test");
            escrow.setAmount(new BigDecimal("100.00"));
            escrow.setStatus(EscrowStatus.SHIPPED);
            escrow.setCreatedAt(LocalDateTime.now());
            escrow.setShippedAt(LocalDateTime.now());
            escrow.setAutoReleaseAt(null);
            escrow.setIdempotencyKey("no-deadline-" + unique);
            escrow.setRequestHash("no-deadline-test-" + unique);

            return escrowRepository.saveAndFlush(escrow).getId();
        });

        assertNotNull(escrowId);

        escrowService.autoReleaseEscrow(escrowId);

        EscrowTransaction unchanged =
                escrowRepository.findById(escrowId).orElseThrow();

        assertEquals(
                EscrowStatus.SHIPPED,
                unchanged.getStatus(),
                "Escrow without a deadline must remain SHIPPED"
        );
    }

    private record TestData(Long escrowId) {}
}