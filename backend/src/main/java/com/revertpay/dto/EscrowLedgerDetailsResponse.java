package com.revertpay.dto;

import com.revertpay.escrow.EscrowStatus;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public record EscrowLedgerDetailsResponse(
        Long escrowId,
        String itemName,
        BigDecimal amount,
        EscrowStatus status,
        LocalDateTime createdAt,
        LocalDateTime shippedAt,
        LocalDateTime resolvedAt,
        String resolution,
        Participant buyer,
        Participant seller,
        List<LedgerMovement> ledgerMovements,
        List<StatusEvent> timeline,
        DisputeDetails dispute
) {
    public record Participant(
            Long userId,
            String name,
            String email
    ) {}


    public record LedgerMovement(
            Long entryId,
            String accountNumber,
            String accountOwnerType,
            Long accountOwnerId,
            String type,
            BigDecimal amount,
            LocalDateTime createdAt,
            long referenceId
    ) {}

    public record StatusEvent(
            Long eventId,
            String fromStatus,
            String toStatus,
            Long actorId,
            String reason,
            LocalDateTime timestamp
    ) {}

    public record DisputeDetails(
            Long disputeId,
            String reason,
            String description,
            String status,
            LocalDateTime createdAt,
            LocalDateTime resolvedAt,
            String sellerResponse,
            LocalDateTime respondedAt
    ) {}


}
