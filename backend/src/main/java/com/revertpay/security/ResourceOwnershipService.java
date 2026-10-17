package com.revertpay.security;

import com.revertpay.dispute.Dispute;
import com.revertpay.dispute.DisputeRepository;
import com.revertpay.escrow.EscrowRepository;
import com.revertpay.escrow.EscrowTransaction;
import com.revertpay.user.User;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

@Service("resourceOwnershipService")
@RequiredArgsConstructor
public class ResourceOwnershipService {

    private final EscrowRepository escrowRepository;
    private final DisputeRepository disputeRepository;
    public boolean isBuyer(Long escrowId, Authentication authentication) {
        User user = getAuthenticatedUser(authentication);

        if (user == null) {
            return false;
        }
        return escrowRepository.findById(escrowId)
                .map(EscrowTransaction::getBuyer)
                .map(buyer -> buyer.getId().equals(user.getId()))
                .orElse(false);
    }

    public boolean isSeller(Long escrowId, Authentication authentication) {
        User user = getAuthenticatedUser(authentication);

        if (user == null) {
            return false;
        }

        return escrowRepository.findById(escrowId)
                .map(EscrowTransaction::getSeller)
                .map(seller -> seller.getId().equals(user.getId()))
                .orElse(false);
    }

    public boolean canAccessDispute(
            Long disputeId,
            Authentication authentication
    ) {
        User user = getAuthenticatedUser(authentication);

        if (user == null) {
            return false;
        }

        return disputeRepository.findById(disputeId)
                .map(Dispute::getTransaction)
                .map(transaction ->
                        transaction.getBuyer().getId().equals(user.getId())
                                || transaction.getSeller().getId().equals(user.getId())
                )
                .orElse(false);
    }

    private User getAuthenticatedUser(Authentication authentication) {
        if (authentication == null
                || !authentication.isAuthenticated()
                || !(authentication.getPrincipal() instanceof User user)) {
            return null;
        }

        return user;
    }
}