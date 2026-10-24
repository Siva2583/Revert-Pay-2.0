package com.revertpay.escrow;

import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.dispute.Dispute;
import com.revertpay.dispute.DisputeRepository;
import com.revertpay.dto.EscrowLedgerDetailsResponse;
import com.revertpay.ledger.LedgerEntry;
import com.revertpay.ledger.LedgerEntryRepository;
import com.revertpay.security.JwtService;
import com.revertpay.user.User;
import com.revertpay.user.UserRepository;

import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class EscrowLedgerDetailsService {
    private final EscrowRepository escrowRepository;
    private final EscrowStatusLogRepository statusLogRepository;
    private final LedgerEntryRepository ledgerEntryRepository;
    private final AccountRepository accountRepository;
    private final DisputeRepository disputeRepository;
    private final UserRepository userRepository;
    private final JwtService jwtService;

    public EscrowLedgerDetailsService(
            EscrowRepository escrowRepository,
            EscrowStatusLogRepository statusLogRepository,
            LedgerEntryRepository ledgerEntryRepository,
            AccountRepository accountRepository,
            DisputeRepository disputeRepository,
            UserRepository userRepository,
            JwtService jwtService
    ) {
        this.escrowRepository = escrowRepository;
        this.statusLogRepository = statusLogRepository;
        this.ledgerEntryRepository = ledgerEntryRepository;
        this.accountRepository = accountRepository;
        this.disputeRepository = disputeRepository;
        this.userRepository = userRepository;
        this.jwtService = jwtService;
    }

    @Transactional(readOnly = true)
    public EscrowLedgerDetailsResponse getDetails(Long escrowId, String token) {

        if (token == null || !jwtService.isTokenValid(token)) {
            throw new AccessDeniedException("Invalid or expired token");
        }

        Long requesterId = jwtService.extractUserId(token);

        EscrowTransaction escrow = escrowRepository.findById(escrowId)
                .orElseThrow(() ->
                        new IllegalArgumentException("Escrow not found"));

        User buyer = escrow.getBuyer();
        User seller = escrow.getSeller();

        boolean isAdmin = userRepository.findById(requesterId)
                .map(user -> user.getRole().name().equals("ADMIN"))
                .orElse(false);

        boolean isBuyer = buyer.getId().equals(requesterId);
        boolean isSeller = seller.getId().equals(requesterId);

        if (!isAdmin && !isBuyer && !isSeller) {
            throw new AccessDeniedException(
                    "You are not authorized to view this escrow");
        }

        List<EscrowLedgerDetailsResponse.LedgerMovement> movements =
                ledgerEntryRepository
                        .findByReferenceIdOrderByCreatedAtAsc(escrowId)
                        .stream()
                        .map(this::toLedgerMovement)
                        .toList();

        List<EscrowLedgerDetailsResponse.StatusEvent> timeline =
                statusLogRepository
                        .findByEscrowTransaction_IdOrderByTimestampAsc(escrowId)
                        .stream()
                        .map(log -> new EscrowLedgerDetailsResponse.StatusEvent(
                                log.getId(),
                                log.getFromStatus() == null
                                        ? null : log.getFromStatus().name(),
                                log.getToStatus() == null
                                        ? null : log.getToStatus().name(),
                                log.getActorId(),
                                log.getReason(),
                                log.getTimestamp()
                        ))
                        .toList();

        EscrowLedgerDetailsResponse.DisputeDetails disputeDetails =
                disputeRepository.findByTransactionId(escrowId)
                        .map(dispute ->
                                new EscrowLedgerDetailsResponse.DisputeDetails(
                                        dispute.getId(),
                                        dispute.getReason() == null
                                                ? null : dispute.getReason().name(),
                                        dispute.getDescription(),
                                        dispute.getStatus() == null
                                                ? null : dispute.getStatus().name(),
                                        dispute.getCreatedAt(),
                                        dispute.getResolvedAt(),
                                        dispute.getSellerResponse(),
                                        dispute.getRespondedAt()
                                ))
                        .orElse(null);

        return new EscrowLedgerDetailsResponse(
                escrow.getId(),
                escrow.getItemName(),
                escrow.getAmount(),
                escrow.getStatus(),
                escrow.getCreatedAt(),
                escrow.getShippedAt(),
                escrow.getResolvedAt(),
                escrow.getResolution(),
                toParticipant(buyer),
                toParticipant(seller),
                movements,
                timeline,
                disputeDetails
        );
    }

    private EscrowLedgerDetailsResponse.Participant toParticipant(User user) {
        return new EscrowLedgerDetailsResponse.Participant(
                user.getId(),
                user.getName(),
                user.getEmail()
        );
    }

    private EscrowLedgerDetailsResponse.LedgerMovement toLedgerMovement(
            LedgerEntry entry
    ) {
        Account account = entry.getAccount();

        return new EscrowLedgerDetailsResponse.LedgerMovement(
                entry.getEntry_id(),
                account.getAccountNumber(),
                account.getOwnerType().name(),
                account.getOwnerId(),
                entry.getType().name(),
                entry.getAmount(),
                entry.getCreatedAt(),
                entry.getReference_id()
        );
    }


}
