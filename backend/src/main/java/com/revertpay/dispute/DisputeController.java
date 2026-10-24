package com.revertpay.dispute;

import com.revertpay.dto.DisputeRequest;
import com.revertpay.dto.DisputeResolutionRequest;
import com.revertpay.dto.DisputeSellerResponse;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/escrow")
public class DisputeController {

    private final DisputeService disputeService;

    public DisputeController(DisputeService disputeService) {
        this.disputeService = disputeService;
    }

    @GetMapping("/{escrowId}/dispute")
    @PreAuthorize(
            "hasRole('ADMIN') or " +
                    "@resourceOwnershipService.isBuyer(#escrowId, authentication) or " +
                    "@resourceOwnershipService.isSeller(#escrowId, authentication)"
    )
    public Optional<Dispute> getDisputes(
            @PathVariable Long escrowId
    ) {
        return disputeService.findByransactionalId(escrowId);
    }

    @PostMapping("/{disputeId}/resolve")
    @PreAuthorize("hasRole('ADMIN')")
    public void resolveDispute(
            @PathVariable Long disputeId,
            HttpServletRequest req,
            @RequestBody DisputeResolutionRequest request
    ) {
        String token = extractBearerToken(req);

        disputeService.resolveDispute(token, disputeId, request);
    }

    @PostMapping("/{disputeId}/respond")
    @PreAuthorize(
            "@resourceOwnershipService.canAccessDispute(#disputeId, authentication)"
    )
    public void respondToDispute(
            @PathVariable Long disputeId,
            HttpServletRequest req,
            @RequestBody DisputeSellerResponse res
    ) {
        String token = extractBearerToken(req);

        disputeService.respondToDispute(token, disputeId, res);
    }

    @PostMapping("/{id}/dispute")
    public void raiseDispute(
            @PathVariable Long id,
            HttpServletRequest req,
            @RequestBody DisputeRequest request
    ) {
        String token = extractBearerToken(req);

        disputeService.Underreview(token, id, request);
    }

    private String extractBearerToken(HttpServletRequest req) {

        String authHeader = req.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new IllegalArgumentException(
                    "A valid Bearer token is required."
            );
        }

        return authHeader.substring(7);
    }
}