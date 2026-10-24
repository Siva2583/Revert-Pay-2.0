package com.revertpay.ledger;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Objects;

@Service
public class LedgerService {

    private final LedgerEntryRepository ledgerEntryRepository;
    private final AccountRepository accountRepository;

    public LedgerService(
            LedgerEntryRepository ledgerEntryRepository,
            AccountRepository accountRepository
    ) {
        this.ledgerEntryRepository = ledgerEntryRepository;
        this.accountRepository = accountRepository;
    }

    public BigDecimal getBalance(Long accountId) {
        return ledgerEntryRepository.calculateBalance(accountId);
    }

    public void doDebit(Account account, BigDecimal amount, long referenceId) {
        LedgerEntry entry = new LedgerEntry();
        entry.setType(Type.DEBIT);
        entry.setAccount(account);
        entry.setAmount(amount);
        entry.setReference_id(referenceId);
        ledgerEntryRepository.save(entry);
    }

    public void doCredit(Account account, BigDecimal amount, long referenceId) {
        LedgerEntry entry = new LedgerEntry();
        entry.setType(Type.CREDIT);
        entry.setAccount(account);
        entry.setAmount(amount);
        entry.setReference_id(referenceId);
        ledgerEntryRepository.save(entry);
    }

    @Transactional
    public void transfer(
            Account source,
            Account destination,
            BigDecimal amount,
            long referenceId
    ) {
        Objects.requireNonNull(source, "Source account cannot be null");
        Objects.requireNonNull(destination, "Destination account cannot be null");
        Objects.requireNonNull(amount, "Amount cannot be null");

        if (source.getId().equals(destination.getId())) {
            throw new IllegalArgumentException(
                    "Source and destination accounts must be different");
        }

        if (amount.signum() <= 0) {
            throw new IllegalArgumentException(
                    "Transfer amount must be greater than zero");
        }

        // Always lock accounts in ascending ID order to reduce deadlocks.
        Long firstId = Math.min(source.getId(), destination.getId());
        Long secondId = Math.max(source.getId(), destination.getId());

        Account first = accountRepository.findByIdForUpdate(firstId)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        Account second = accountRepository.findByIdForUpdate(secondId)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        Account lockedSource = source.getId().equals(firstId) ? first : second;
        Account lockedDestination =
                destination.getId().equals(firstId) ? first : second;
//        System.out.println(
//                "SOURCE ACCOUNT: " + lockedSource.getAccountNumber()
//        );

//        System.out.println(
//                "SOURCE ACCOUNT ID: " + lockedSource.getId()
//        );
//
//        System.out.println(
//                "SOURCE BALANCE: " +
//                        ledgerEntryRepository.calculateBalance(lockedSource.getId())
//        );
//
//        System.out.println("TRANSFER AMOUNT: " + amount);
        BigDecimal balance = ledgerEntryRepository.calculateBalance(
                lockedSource.getId());

        if (balance.compareTo(amount) < 0) {
            throw new IllegalArgumentException("Insufficient available balance");
        }

        doDebit(lockedSource, amount, referenceId);
        doCredit(lockedDestination, amount, referenceId);
    }
}