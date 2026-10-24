package com.revertpay.ledger;

import com.revertpay.account.Account;
import com.revertpay.account.AccountService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/admin/ledger")
@PreAuthorize("hasRole('ADMIN')")
public class AdminLedgerController {

    private final AccountService accountService;
    private final LedgerService ledgerService;
    private final LedgerEntryRepository ledgerEntryRepository;

    public AdminLedgerController(
            AccountService accountService,
            LedgerService ledgerService,
            LedgerEntryRepository ledgerEntryRepository
    ) {
        this.accountService = accountService;
        this.ledgerService = ledgerService;
        this.ledgerEntryRepository = ledgerEntryRepository;
    }

    @GetMapping("/holding")
    public AdminLedgerResponse getHoldingAccount() {

        Account holding = accountService
                .findByAccountNumber("ESCROW_HOLDING")
                .orElseThrow(() ->
                        new IllegalStateException(
                                "ESCROW_HOLDING account not found"
                        )
                );

        BigDecimal balance =
                ledgerService.getBalance(holding.getId());

        List<LedgerEntry> entries =
                ledgerEntryRepository.findByAccountId(holding.getId());

        BigDecimal totalCredits = entries.stream()
                .filter(entry -> entry.getType() == Type.CREDIT)
                .map(LedgerEntry::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal totalDebits = entries.stream()
                .filter(entry -> entry.getType() == Type.DEBIT)
                .map(LedgerEntry::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        return new AdminLedgerResponse(
                holding.getId(),
                holding.getAccountNumber(),
                balance,
                totalCredits,
                totalDebits,
                entries.size(),
                entries.stream()
                        .sorted((a, b) ->
                                Long.compare(
                                        b.getEntry_id(),
                                        a.getEntry_id()
                                ))
                        .limit(20)
                        .toList()
        );
    }

    public record AdminLedgerResponse(
            Long accountId,
            String accountNumber,
            BigDecimal balance,
            BigDecimal totalCredits,
            BigDecimal totalDebits,
            int totalEntries,
            List<LedgerEntry> recentEntries
    ) {}
}