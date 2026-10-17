package com.revertpay.ledger;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.account.OwnerType;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@SpringBootTest
class LedgerServiceRollbackTest {

    @Autowired
    private LedgerService ledgerService;

    @Autowired
    private LedgerEntryRepository ledgerEntryRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private PlatformTransactionManager transactionManager;

    @Test
    void transferEntriesShouldRollbackWhenOuterTransactionFails() {
        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        long referenceId = System.nanoTime();

        // Persist valid accounts before starting the transaction under test.
        Account[] accounts = transactions.execute(status -> {
            Account source = accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.USER,
                            900001L,
                            "TEST-SOURCE-" + referenceId
                    )
            );

            Account destination = accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.SYSTEM,
                            900002L,
                            "TEST-DEST-" + referenceId
                    )
            );

            return new Account[]{source, destination};
        });

        Account source = accounts[0];
        Account destination = accounts[1];

        long entriesBefore = ledgerEntryRepository.count();

        // The exception escapes the transaction, triggering rollback.
        assertThrows(RuntimeException.class, () ->
                transactions.executeWithoutResult(status -> {
                    ledgerService.transfer(
                            source,
                            destination,
                            new BigDecimal("100.00"),
                            referenceId
                    );

                    throw new RuntimeException("Intentional rollback test");
                })
        );

        // Neither the debit nor credit should remain committed.
        assertEquals(
                entriesBefore,
                ledgerEntryRepository.count(),
                "Ledger entries must roll back when the outer transaction fails"
        );
    }
}