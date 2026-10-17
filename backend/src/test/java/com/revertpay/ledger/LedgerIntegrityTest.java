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

import static org.junit.jupiter.api.Assertions.*;

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
                    "Transfer must create exactly two ledger entries"
            );

            List<LedgerEntry> debits = entries.stream()
                    .filter(entry -> entry.getType() == Type.DEBIT)
                    .toList();

            List<LedgerEntry> credits = entries.stream()
                    .filter(entry -> entry.getType() == Type.CREDIT)
                    .toList();

            assertEquals(1, debits.size(), "Exactly one debit is required");
            assertEquals(1, credits.size(), "Exactly one credit is required");

            assertEquals(
                    0,
                    amount.compareTo(debits.get(0).getAmount()),
                    "Debit amount must match the transfer amount"
            );

            assertEquals(
                    0,
                    amount.compareTo(credits.get(0).getAmount()),
                    "Credit amount must match the transfer amount"
            );

            assertEquals(
                    source.getId(),
                    debits.get(0).getAccount().getId(),
                    "Debit must belong to the source account"
            );

            assertEquals(
                    destination.getId(),
                    credits.get(0).getAccount().getId(),
                    "Credit must belong to the destination account"
            );
        });
    }
}