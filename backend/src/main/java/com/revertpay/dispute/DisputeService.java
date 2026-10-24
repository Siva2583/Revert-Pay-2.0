package com.revertpay.dispute;

import com.revertpay.account.Account;
import com.revertpay.account.AccountService;
import com.revertpay.dto.DisputeRequest;
import com.revertpay.dto.DisputeResolutionRequest;
import com.revertpay.dto.DisputeSellerResponse;
import com.revertpay.escrow.EscrowRepository;
import com.revertpay.escrow.EscrowStatus;
import com.revertpay.escrow.EscrowTransaction;
import com.revertpay.escrow.EscrowTransitionService;
import com.revertpay.ledger.LedgerService;
import com.revertpay.security.JwtService;
import com.revertpay.user.User;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class DisputeService {

    private final DisputeRepository disputeRepository;
    private final JwtService jwtService;
    private final EscrowRepository escrowRepository;
    private final EscrowTransitionService transitionService;
    private final LedgerService ledgerService;
    private final AccountService accountService;

    public DisputeService(
            DisputeRepository disputeRepository,
            JwtService jwtService,
            EscrowRepository escrowRepository,
            EscrowTransitionService transitionService,
            LedgerService ledgerService,
            AccountService accountService
    ) {
        this.disputeRepository = disputeRepository;
        this.jwtService = jwtService;
        this.escrowRepository = escrowRepository;
        this.transitionService = transitionService;
        this.ledgerService = ledgerService;
        this.accountService = accountService;
    }

    public Optional<Dispute> findByransactionalId(Long transactionId) {
        return disputeRepository.findByTransactionId(transactionId);
    }

    @Transactional
    public void respondToDispute(
            String token,
            Long disputeId,
            DisputeSellerResponse res
    ) {
        if (!jwtService.isTokenValid(token)) {
            throw new AccessDeniedException("Invalid or expired token");
        }

        Dispute dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() ->
                        new IllegalArgumentException("Invalid dispute"));

        EscrowTransaction transaction = dispute.getTransaction();

        Long sellerId = jwtService.extractUserId(token);

        if (!transaction.getSeller().getId().equals(sellerId)) {
            throw new AccessDeniedException(
                    "Only the seller can respond to this dispute"
            );
        }

        if (dispute.getStatus() != DisputeStatus.OPENED) {
            throw new IllegalStateException(
                    "Dispute is not open for a response"
            );
        }

        if (res == null || res.getResponse() == null
                || res.getResponse().isBlank()) {
            throw new IllegalArgumentException(
                    "A seller response is required"
            );
        }

        dispute.setSellerResponse(res.getResponse());
        dispute.setRespondedAt(LocalDateTime.now());
        dispute.setStatus(DisputeStatus.RESPONDED);

        disputeRepository.save(dispute);
    }

    @Transactional
    @PreAuthorize("hasRole('ADMIN')")
    public void resolveDispute(
            String token,
            Long disputeId,
            DisputeResolutionRequest request
    ) {
        if (!jwtService.isTokenValid(token)) {
            throw new org.springframework.security.access.AccessDeniedException(
                    "Invalid or expired token"
            );
        }

        // Ensure the token belongs to the same authenticated administrator
        org.springframework.security.core.Authentication authentication =
                org.springframework.security.core.context.SecurityContextHolder
                        .getContext()
                        .getAuthentication();

        if (authentication == null
                || !(authentication.getPrincipal() instanceof User admin)
                || !admin.getId().equals(jwtService.extractUserId(token))) {
            throw new org.springframework.security.access.AccessDeniedException(
                    "Authenticated administrator does not match token"
            );
        }

        Dispute dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() ->
                        new IllegalArgumentException("Invalid dispute"));

        EscrowTransaction transaction = dispute.getTransaction();

        if (transaction.getStatus() != EscrowStatus.UNDER_REVIEW) {
            throw new IllegalStateException(
                    "Escrow transaction is not under review"
            );
        }

        if (request == null || request.getResolution() == null) {
            throw new IllegalArgumentException(
                    "A valid resolution is required"
            );
        }

        Long sellerId = transaction.getSeller().getId();
        Long buyerId = transaction.getBuyer().getId();
        BigDecimal amount = transaction.getAmount();

        Account escrow = accountService
                .findByAccountNumber("ESCROW_HOLDING")
                .orElseThrow(() ->
                        new IllegalStateException(
                                "Escrow holding account not found"));

        Account buyer = accountService
                .findByAccountNumber("ACC" + buyerId)
                .orElseThrow(() ->
                        new IllegalStateException("Buyer account not found"));

        Account seller = accountService
                .findByAccountNumber("ACC" + sellerId)
                .orElseThrow(() ->
                        new IllegalStateException("Seller account not found"));

        if (request.getResolution() == ResolutionType.RELEASE) {

            transitionService.transition(
                    transaction,
                    EscrowStatus.RELEASED,
                    admin.getId(),
                    "Admin released funds"
            );

            ledgerService.transfer(
                    escrow,
                    seller,
                    amount,
                    transaction.getId()
            );

        } else if (request.getResolution() == ResolutionType.REFUND) {

            transitionService.transition(
                    transaction,
                    EscrowStatus.REFUNDED,
                    admin.getId(),
                    "Admin approved refund"
            );

            ledgerService.transfer(
                    escrow,
                    buyer,
                    amount,
                    transaction.getId()
            );

        } else {
            throw new IllegalArgumentException(
                    "Unsupported dispute resolution"
            );
        }

        escrowRepository.save(transaction);
    }

    @Transactional
    public void Underreview(
            String token,
            Long id,
            DisputeRequest req
    ) {
        if (!jwtService.isTokenValid(token)) {
            throw new AccessDeniedException(
                    "Invalid or expired token"
            );
        }

        EscrowTransaction transaction = escrowRepository.findById(id)
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "Escrow transaction not found"));

        Long buyerId = jwtService.extractUserId(token);

        if (!transaction.getBuyer().getId().equals(buyerId)) {
            throw new AccessDeniedException(
                    "Only the buyer can raise a dispute"
            );
        }

        if (req == null
                || req.getReason() == null) {
            throw new IllegalArgumentException(
                    "A dispute reason is required"
            );
        }

        if (transaction.getStatus() == EscrowStatus.UNDER_REVIEW) {
            throw new IllegalStateException(
                    "This transaction is already under review"
            );
        }

        Dispute dispute = new Dispute();
        dispute.setTransaction(transaction);
        dispute.setStatus(DisputeStatus.OPENED);
        dispute.setCreatedAt(LocalDateTime.now());
        dispute.setReason(req.getReason());
        dispute.setDescription(req.getDescription());

        transitionService.transition(
                transaction,
                EscrowStatus.UNDER_REVIEW,
                buyerId,
                "Customer review requested"
        );

        escrowRepository.save(transaction);
        disputeRepository.save(dispute);
    }
}