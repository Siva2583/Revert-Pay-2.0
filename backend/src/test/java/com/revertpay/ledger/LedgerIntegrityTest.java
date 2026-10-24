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
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest
class LedgerIntegrityTest {

    @Autowired
    private LedgerService ledgerService;

    @Autowired
    private LedgerEntryRepository ledgerEntryRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private PlatformTransactionManager transactionManager;

    @Test
    void transferShouldCreateBalancedDebitAndCreditEntries() {
        long unique = System.nanoTime();
        long referenceId = Math.abs(unique);

        TransactionTemplate transactions =
                new TransactionTemplate(transactionManager);

        transactions.executeWithoutResult(status -> {
            Account source = accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.SYSTEM,
                            700000L + unique % 100000L,
                            "TEST_SOURCE_" + unique
                    )
            );

            Account destination = accountRepository.saveAndFlush(
                    new Account(
                            OwnerType.SYSTEM,
                            800000L + unique % 100000L,
                            "TEST_DEST_" + unique
                    )
            );

            BigDecimal amount = new BigDecimal("100.00");

            // Fund the source account before transferring.
            ledgerService.doCredit(
                    source,
                    new BigDecimal("500.00"),
                    referenceId + 1
            );

            // Transfer must debit the source and credit the destination.
            ledgerService.transfer(
                    source,
                    destination,
                    amount,
                    referenceId
            );

            List<LedgerEntry> entries =
                    ledgerEntryRepository.findAll()
                            .stream()
                            .filter(entry ->
                                    entry.getReference_id() == referenceId)
                            .toList();

            assertEquals(
                    2,
                    entries.size(),
                    "A successful transfer must create exactly two ledger entries"
            );

            LedgerEntry debit = entries.stream()
                    .filter(entry -> entry.getType() == Type.DEBIT)
                    .findFirst()
                    .orElseThrow(() ->
                            new AssertionError("Debit entry was not created"));

            LedgerEntry credit = entries.stream()
                    .filter(entry -> entry.getType() == Type.CREDIT)
                    .findFirst()
                    .orElseThrow(() ->
                            new AssertionError("Credit entry was not created"));

            assertEquals(amount, debit.getAmount());
            assertEquals(amount, credit.getAmount());

            assertEquals(source.getId(), debit.getAccount().getId());
            assertEquals(destination.getId(), credit.getAccount().getId());
        });
    }
}
