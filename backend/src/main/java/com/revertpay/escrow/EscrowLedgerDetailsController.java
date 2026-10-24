package com.revertpay.escrow;

import com.revertpay.dto.EscrowLedgerDetailsResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/escrow")
public class EscrowLedgerDetailsController {


    private static final Logger log =
            LoggerFactory.getLogger(EscrowLedgerDetailsController.class);

    private final EscrowLedgerDetailsService escrowLedgerDetailsService;

    public EscrowLedgerDetailsController(
            EscrowLedgerDetailsService escrowLedgerDetailsService
    ) {
        this.escrowLedgerDetailsService = escrowLedgerDetailsService;
    }

    @GetMapping("/{escrowId}/ledger-details")
    public ResponseEntity<EscrowLedgerDetailsResponse> getLedgerDetails(
            @PathVariable Long escrowId,
            @RequestHeader(
                    value = HttpHeaders.AUTHORIZATION,
                    required = false
            ) String authorization
    ) {
        System.out.println("LEDGER DETAILS CONTROLLER HIT");

        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new ResponseStatusException(
                    HttpStatus.UNAUTHORIZED,
                    "Authentication token is required"
            );
        }

        String token = authorization.substring(7);

        System.out.println(
                "TOKEN RECEIVED — ESCROW ID: " + escrowId
        );

        try {
            System.out.println("CALLING LEDGER DETAILS SERVICE");

            EscrowLedgerDetailsResponse response =
                    escrowLedgerDetailsService.getDetails(escrowId, token);

            System.out.println("SERVICE RETURNED SUCCESSFULLY");

            return ResponseEntity.ok(response);

        } catch (AccessDeniedException ex) {
            throw new ResponseStatusException(
                    HttpStatus.FORBIDDEN,
                    ex.getMessage()
            );

        } catch (IllegalArgumentException ex) {
            throw new ResponseStatusException(
                    HttpStatus.NOT_FOUND,
                    ex.getMessage()
            );

        } catch (Exception ex) {
            log.error(
                    "Failed to load ledger details for escrow ID {}",
                    escrowId,
                    ex
            );

            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Failed to load transaction details"
            );
        }
    }


}
