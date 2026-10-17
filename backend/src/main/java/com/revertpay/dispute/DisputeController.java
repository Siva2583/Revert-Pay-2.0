package com.revertpay.dispute;

import com.revertpay.dto.DisputeRequest;
import com.revertpay.dto.DisputeResolutionRequest;
import com.revertpay.dto.DisputeSellerResponse;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("api/escrow")
public class DisputeController {
    private final DisputeService disputeService;

    public DisputeController(DisputeService disputeService) {
        this.disputeService = disputeService;
    }
    @GetMapping("{escrowId}/dispute")
    public Optional<Dispute> getDisputes(@PathVariable Long escrowId){
        return disputeService.findByransactionalId(escrowId);
    }
    @PostMapping("/{disputeId}/resolve")
    public void resolveDispute(
            @PathVariable Long disputeId,
            HttpServletRequest req,
            @RequestBody DisputeResolutionRequest request
    ) {
        String authHeader = req.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Missing Authorization header!!");
        }

        String token = authHeader.substring(7);

        disputeService.resolveDispute(token, disputeId, request);
    }
    @PostMapping("{disputeId}/respond")
    public void respondToDispute(@PathVariable Long disputeId, HttpServletRequest req, @RequestBody DisputeSellerResponse res){
        String authHeader =req.getHeader("Authorization");
        if(authHeader==null || !authHeader.startsWith("Bearer ")){
            throw new RuntimeException("Missing Authorization header!!");
        }
        String token=authHeader.substring(7);
        disputeService.respondToDispute(token,disputeId,res);

    }

    @PostMapping("{id}/dispute")
    public void raiseDispute(@PathVariable Long id, HttpServletRequest req, @RequestBody DisputeRequest request){
        String authHeader =req.getHeader("Authorization");
        if(authHeader==null || !authHeader.startsWith("Bearer ")){
            throw new RuntimeException("Missing Authorization header!!");
        }
        String token=authHeader.substring(7);
        disputeService.Underreview(token,id,request);
    }

}
