package com.revertpay.escrow;

import com.revertpay.dto.EscrowInitiateRequest;
import com.revertpay.dto.EscrowInitiateResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/escrow")
public class EscrowController {

    private final EscrowService escrowService;

    public EscrowController(EscrowService escrowService) {
        this.escrowService = escrowService;
    }

    @GetMapping("/buyer")
    @PreAuthorize("hasRole('BUYER')")
    public List<EscrowTransaction> getBuyerTransactions(
            HttpServletRequest req) {

        String authHeader = req.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Missing Authorization header!!");
        }

        String token = authHeader.substring(7);

        return escrowService.getTransactions(token, "buyer");
    }
    @GetMapping("/admin")
    @PreAuthorize("hasRole('ADMIN')")
    public List<EscrowTransaction> getAdminDisputes() {
        return escrowService.getAdminDisputes();
    }

    @GetMapping("/seller")
    @PreAuthorize("hasRole('SELLER')")
    public List<EscrowTransaction> getSellerTransactions(
            HttpServletRequest req) {

        String authHeader = req.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Missing Authorization header!!");
        }

        String token = authHeader.substring(7);

        return escrowService.getTransactions(token, "seller");
    }

    @PostMapping("/{id}/confirm-delivery")
    @PreAuthorize("@resourceOwnershipService.isBuyer(#id, authentication)")
    public void escrowConfirm(
            @PathVariable Long id,
            HttpServletRequest req) {

        String token = extractToken(req);

        escrowService.confirmEscrow(id, token);
    }

    @PostMapping("/{id}/ship")
    @PreAuthorize("@resourceOwnershipService.isSeller(#id, authentication)")
    public void escrowInitiateShip(
            @PathVariable Long id,
            HttpServletRequest req) {

        String token = extractToken(req);

        escrowService.shipTransaction(id, token);
    }

    @PostMapping("/{id}/fund")
    @PreAuthorize("@resourceOwnershipService.isBuyer(#id, authentication)")
    public EscrowInitiateResponse fundTransaction(
            @PathVariable Long id,
            HttpServletRequest request) {

        String token = extractToken(request);

        return escrowService.fundTransaction(id, token);
    }

    @PostMapping("/{id}/cancel")
    @PreAuthorize("@resourceOwnershipService.isBuyer(#id, authentication)")
    public EscrowInitiateResponse cancelTransaction(
            @PathVariable Long id,
            HttpServletRequest request) {

        String token = extractToken(request);

        return escrowService.cancelTransaction(id, token);
    }

    @PostMapping("/{id}/confirm")
    @PreAuthorize("@resourceOwnershipService.isBuyer(#id, authentication)")
    public EscrowInitiateResponse confirmTransaction(
            @PathVariable Long id,
            HttpServletRequest request) {

        String token = extractToken(request);

        return escrowService.confirmTransaction(id, token);
    }

    @PostMapping("/initiate")
    @PreAuthorize("hasRole('BUYER')")
    public EscrowInitiateResponse initiate(
            @RequestBody @Valid EscrowInitiateRequest req,
            HttpServletRequest request) {

        String token = extractToken(request);

        String idempotencyKey = request.getHeader("Idempotency-Key");

        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            throw new RuntimeException("Idempotency-Key header missing");
        }

        return escrowService.transactionRequest(
                req, token, idempotencyKey);
    }

    private String extractToken(HttpServletRequest request) {

        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Authorization token missing");
        }

        return authHeader.substring(7);
    }
}