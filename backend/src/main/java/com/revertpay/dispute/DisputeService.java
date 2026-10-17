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
import org.springframework.security.access.prepost.PreAuthorize;
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

    public DisputeService(DisputeRepository disputeRepository, JwtService jwtService, EscrowRepository escrowRepository, EscrowTransitionService transitionService, LedgerService ledgerService, AccountService accountService) {
        this.disputeRepository = disputeRepository;
        this.jwtService = jwtService;
        this.escrowRepository = escrowRepository;
        this.transitionService = transitionService;
        this.ledgerService=ledgerService;
        this.accountService = accountService;
    }
    public Optional<Dispute> findByransactionalId(Long transactionId){
        return disputeRepository.findByTransactionId(transactionId);
    }
    public void respondToDispute(String token, Long disputeId, DisputeSellerResponse res){
        if(!jwtService.isTokenValid(token)){
            throw new RuntimeException("Invalid Token!!");
        }
        Dispute dispute=disputeRepository.findById(disputeId).orElseThrow(()->new RuntimeException("Invalid Dispute!!"));
        EscrowTransaction transaction=escrowRepository.findById(dispute.getTransaction().getId()).orElseThrow(()->new RuntimeException("Invalid Transaction!!"));
        Long sellerId= jwtService.extractUserId(token);
        if(!transaction.getSeller().getId().equals(sellerId)){
            throw new RuntimeException("Not a  Seller!!");
        }
        //EscrowTransaction transaction=escrowRepository.findById()

        if(!dispute.getStatus().equals(DisputeStatus.OPENED)){
            throw new RuntimeException("Invalid action!!");

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
        DisputeResolutionRequest request){
        Dispute dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() -> new RuntimeException("Invalid Dispute!!"));
        //EscrowTransaction transaction= escrowRepository.findById(dispute.getTransaction().getId()).orElseThrow(()->(new RuntimeException("No Such Escrow!!")));
        EscrowTransaction transaction = dispute.getTransaction();
        if(transaction.getStatus()!=EscrowStatus.UNDER_REVIEW)  throw new RuntimeException("Invalid action!!");
        if (request.getResolution() == null) {
            throw new RuntimeException("Resolution is required!!");
        }
        Long seller_id=transaction.getSeller().getId();
        Long buyer_id=transaction.getBuyer().getId();
        BigDecimal amount=transaction.getAmount();
        Account escrow=accountService.findByAccountNumber("ESCROW_HOLDING").orElseThrow(()->new RuntimeException("No Escrow Holding found!!"));
        Account buyer=accountService.findByAccountNumber("ACC"+buyer_id).orElseThrow(()->new RuntimeException("No buyer found!!"));
        Account seller=accountService.findByAccountNumber("ACC"+seller_id).orElseThrow(()->new RuntimeException("No seller found!!"));

        if (request.getResolution() == ResolutionType.RELEASE) {

            transitionService.transition(
                    transaction,
                    EscrowStatus.RELEASED,
                    jwtService.extractUserId(token),
                    "Admin released funds"
            );
            ledgerService.transfer(escrow,seller,amount, transaction.getId());

        } else if (request.getResolution() == ResolutionType.REFUND) {

            transitionService.transition(
                    transaction,
                    EscrowStatus.REFUNDED,
                    jwtService.extractUserId(token),
                    "Admin approved refund"
            );
            ledgerService.transfer(escrow,buyer,amount,transaction.getId());
        }
        escrowRepository.save(transaction);
    }
    public void Underreview(String token,Long id, DisputeRequest req){
        if (!jwtService.isTokenValid(token)) {
            throw new RuntimeException("Invalid or expired token");
        }
        EscrowTransaction transaction = escrowRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Escrow transaction not found"));
        Long buyer_id= jwtService.extractUserId(token);
        if(!(transaction.getBuyer().getId()).equals(buyer_id)){
            throw new RuntimeException("Invalid Buyer!!");
        }
        Dispute dispute=new Dispute();
        dispute.setTransaction(transaction);
        dispute.setStatus(DisputeStatus.OPENED);
        dispute.setCreatedAt(LocalDateTime.now());
        dispute.setReason(req.getReason());
        dispute.setDescription(req.getDescription());
        transitionService.transition(transaction,EscrowStatus.UNDER_REVIEW, buyer_id, "Customer review requested");
        escrowRepository.save(transaction);
        disputeRepository.save(dispute);



    }


}