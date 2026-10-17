package com.revertpay.ledger;

import com.revertpay.account.Account;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.Objects;

@Service
public class LedgerService {

    private final LedgerEntryRepository ledgerEntryRepository;

    public LedgerService(LedgerEntryRepository ledgerEntryRepository) {
        this.ledgerEntryRepository = ledgerEntryRepository;
    }

    public void doDebit(Account account, BigDecimal amount, long referenceId) {
        LedgerEntry ledgerEntry = new LedgerEntry();
        ledgerEntry.setType(Type.DEBIT);
        ledgerEntry.setAccount(account);
        ledgerEntry.setAmount(amount);
        ledgerEntry.setReference_id(referenceId);
        ledgerEntryRepository.save(ledgerEntry);
    }

    public void doCredit(Account account, BigDecimal amount, long referenceId) {
        LedgerEntry ledgerEntry = new LedgerEntry();
        ledgerEntry.setAccount(account);
        ledgerEntry.setType(Type.CREDIT);
        ledgerEntry.setAmount(amount);
        ledgerEntry.setReference_id(referenceId);

        ledgerEntryRepository.save(ledgerEntry);
    }

    @Transactional
    public void transfer(
            Account account1,
            Account account2,
            BigDecimal amount,
            long referenceId) {

        Objects.requireNonNull(account1, "Source account cannot be null");
        Objects.requireNonNull(account2, "Destination account cannot be null");
        Objects.requireNonNull(amount, "Transfer amount cannot be null");

        if (account1.getId().equals(account2.getId())) {
            throw new IllegalArgumentException(
                    "Source and destination accounts must be different");
        }

        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException(
                    "Transfer amount must be greater than zero");
        }

        doDebit(account1, amount, referenceId);
        doCredit(account2, amount, referenceId);
    }
}