package com.revertpay.escrow;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class EscrowScheduler {

    private final EscrowRepository escrowRepository;
    private final EscrowService escrowService;

    public EscrowScheduler(
            EscrowRepository escrowRepository,
            EscrowService escrowService
    ) {
        this.escrowRepository = escrowRepository;
        this.escrowService = escrowService;
    }
    @Scheduled(fixedRate = 5000)
    public void autoReleaseEscrows() {

        List<EscrowTransaction> transactions =
                escrowRepository.findByStatusAndAutoReleaseAtLessThanEqual(
                        EscrowStatus.SHIPPED,
                        java.time.LocalDateTime.now()
                );

        for (EscrowTransaction transaction : transactions) {
            try {
                escrowService.autoReleaseEscrow(transaction.getId());
            } catch (Exception e) {
//                System.err.println(
//                        "Auto-release failed for escrow " +
//                                transaction.getId() + ": " + e.getMessage()
//                );
            }
        }
    }
    @Scheduled(fixedRate = 5000)
    public void expireEscrows() {

        List<EscrowTransaction> transactions =
                escrowRepository.findByStatus(EscrowStatus.PAYMENT_INITIATED);

        for (EscrowTransaction transaction : transactions) {
            try {
                escrowService.checkExpiry(transaction.getId());
            } catch (Exception e) {
//                System.err.println(
//                        "Expiry check failed for escrow "
//                                + transaction.getId() + ": " + e.getMessage()
//                );
            }
        }
    }
}