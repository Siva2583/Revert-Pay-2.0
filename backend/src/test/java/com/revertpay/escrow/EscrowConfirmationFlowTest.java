package com.revertpay.escrow;
import com.revertpay.dto.EscrowInitiateResponse;
import com.revertpay.account.Account;
import com.revertpay.account.AccountRepository;
import com.revertpay.account.AccountService;
import com.revertpay.account.OwnerType;
import com.revertpay.ledger.LedgerService;
import com.revertpay.security.JwtService;
import com.revertpay.user.Role;
import com.revertpay.user.User;
import com.revertpay.user.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.lenient;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EscrowConfirmationFlowTest {

    @Mock private EscrowTransitionService transitionService;
    @Mock private EscrowRepository escrowRepository;
    @Mock private UserRepository userRepository;
    @Mock private JwtService jwtService;
    @Mock private AccountService accountService;
    @Mock private AccountRepository accountRepository;
    @Mock private LedgerService ledgerService;

    @InjectMocks private EscrowService escrowService;

    private User buyer;
    private User seller;
    private EscrowTransaction transaction;
    private Account buyerAccount;
    private Account holdingAccount;
    private final String token = "test-token";
    private final Long escrowId = 101L;
    private final Long buyerId = 11L;
    private final Long sellerId = 22L;
    private final BigDecimal amount = new BigDecimal("125.00");

    @BeforeEach
    void setUp() {
        buyer = new User();
        buyer.setId(buyerId);
        buyer.setName("Test Buyer");
        buyer.setEmail("buyer-test@example.com");
        buyer.setPassword("not-a-real-password");
        buyer.setRole(Role.BUYER);

        seller = new User();
        seller.setId(sellerId);
        seller.setName("Test Seller");
        seller.setEmail("seller-test@example.com");
        seller.setPassword("not-a-real-password");
        seller.setRole(Role.SELLER);

        transaction = new EscrowTransaction();
        transaction.setId(escrowId);
        transaction.setBuyer(buyer);
        transaction.setSeller(seller);
        transaction.setItemName("Test item");
        transaction.setAmount(amount);
        transaction.setStatus(EscrowStatus.PAYMENT_INITIATED);
        transaction.setCreatedAt(LocalDateTime.now().minusSeconds(2));
        transaction.setConfirmationDeadline(LocalDateTime.now().plusSeconds(40));
        transaction.setIdempotencyKey("test-idempotency-key");

        buyerAccount = new Account(OwnerType.USER, buyerId, "ACC" + buyerId);
        buyerAccount.setId(1L);
        holdingAccount = new Account(OwnerType.SYSTEM, 0L, "ESCROW_HOLDING");
        holdingAccount.setId(2L);

        lenient().when(jwtService.isTokenValid(token)).thenReturn(true);
        // Support either lookup method while service locking changes are being applied.
        // Lenient stubs avoid Mockito errors in tests that return before loading a transaction.
        lenient().when(escrowRepository.findById(escrowId)).thenReturn(Optional.of(transaction));
        lenient().when(escrowRepository.findByIdForUpdate(escrowId)).thenReturn(Optional.of(transaction));
        lenient().when(jwtService.extractUserId(token)).thenReturn(buyerId);

        // Apply the real status mutation while mocking audit persistence.
        lenient().doAnswer(invocation -> {
            EscrowTransaction tx = invocation.getArgument(0);
            EscrowStatus next = invocation.getArgument(1);
            EscrowStatus current = tx.getStatus();
            boolean valid = switch (current) {
                case PAYMENT_INITIATED -> next == EscrowStatus.CREATED
                        || next == EscrowStatus.CANCELLED
                        || next == EscrowStatus.EXPIRED;
                case CREATED -> next == EscrowStatus.FUNDED;
                case FUNDED -> next == EscrowStatus.SHIPPED;
                case SHIPPED -> next == EscrowStatus.RELEASED
                        || next == EscrowStatus.UNDER_REVIEW;
                case UNDER_REVIEW -> next == EscrowStatus.RELEASED
                        || next == EscrowStatus.REFUNDED;
                default -> false;
            };
            if (!valid) throw new InvalidTransitionException("Invalid transition: " + current + " -> " + next);
            tx.setStatus(next);
            return null;
        }).when(transitionService).transition(
                any(EscrowTransaction.class),
                any(EscrowStatus.class),
                any(),
                anyString()
        );
    }

    @Test
    void confirmWithinFortySecondsMovesToCreatedWithoutMovingMoney() {
        when(escrowRepository.save(any(EscrowTransaction.class))).thenAnswer(i -> i.getArgument(0));

        EscrowInitiateResponse response = escrowService.confirmTransaction(escrowId, token);

        assertEquals(EscrowStatus.CREATED, response.getStatus());
        verify(transitionService).transition(transaction, EscrowStatus.CREATED, buyerId,
                "Buyer confirmed transaction");
        verifyNoInteractions(ledgerService);
    }

    @Test
    void confirmAfterDeadlineIsRejected() {
        transaction.setConfirmationDeadline(LocalDateTime.now().minusSeconds(1));

        assertThrows(RuntimeException.class, () -> escrowService.confirmTransaction(escrowId, token));
        assertEquals(EscrowStatus.PAYMENT_INITIATED, transaction.getStatus());
        verify(transitionService, never()).transition(any(), any(), any(), anyString());
        verifyNoInteractions(ledgerService);
    }

    @Test
    void confirmCancelledTransactionIsRejected() {
        transaction.setStatus(EscrowStatus.CANCELLED);

        assertThrows(RuntimeException.class, () -> escrowService.confirmTransaction(escrowId, token));
        verify(transitionService, never()).transition(any(), any(), any(), anyString());
    }

    @Test
    void wrongBuyerCannotConfirm() {
        when(jwtService.extractUserId(token)).thenReturn(999L);

        assertThrows(RuntimeException.class, () -> escrowService.confirmTransaction(escrowId, token));
        verify(transitionService, never()).transition(any(), any(), any(), anyString());
    }

    @Test
    void cancelWithinWindowMovesToCancelledWithoutMovingMoney() {
        when(escrowRepository.save(any(EscrowTransaction.class))).thenAnswer(i -> i.getArgument(0));

        EscrowInitiateResponse response = escrowService.cancelTransaction(escrowId, token);

        assertEquals(EscrowStatus.CANCELLED, response.getStatus());
        verify(transitionService).transition(transaction, EscrowStatus.CANCELLED, buyerId,
                "Buyer declined transaction");
        verifyNoInteractions(ledgerService);
    }

    @Test
    void cancelAfterDeadlineIsRejected() {
        transaction.setConfirmationDeadline(LocalDateTime.now().minusSeconds(1));

        assertThrows(RuntimeException.class, () -> escrowService.cancelTransaction(escrowId, token));
        assertEquals(EscrowStatus.PAYMENT_INITIATED, transaction.getStatus());
        verify(transitionService, never()).transition(any(), any(), any(), anyString());
    }

    @Test
    void fundingBeforeConfirmationIsRejectedAndDoesNotTransfer() {

        assertThrows(RuntimeException.class, () -> escrowService.fundTransaction(escrowId, token));
        verifyNoInteractions(ledgerService);
        verify(accountRepository, never()).findByAccountNumber(anyString());
    }

    @Test
    void fundingAfterConfirmationTransfersOnceAndMovesToFunded() {
        transaction.setStatus(EscrowStatus.CREATED);
        when(accountRepository.findByAccountNumber("ACC" + buyerId)).thenReturn(Optional.of(buyerAccount));
        when(accountRepository.findByAccountNumber("ESCROW_HOLDING")).thenReturn(Optional.of(holdingAccount));
        when(escrowRepository.save(any(EscrowTransaction.class))).thenAnswer(i -> i.getArgument(0));

        EscrowInitiateResponse response = escrowService.fundTransaction(escrowId, token);

        assertEquals(EscrowStatus.FUNDED, response.getStatus());
        verify(ledgerService, times(1)).transfer(buyerAccount, holdingAccount, amount, escrowId);
        verify(transitionService).transition(transaction, EscrowStatus.FUNDED, buyerId,
                "Escrow funded successfully");
    }

    @Test
    void fundingExpiredTransactionIsRejectedWithoutTransfer() {
        transaction.setStatus(EscrowStatus.EXPIRED);

        assertThrows(RuntimeException.class, () -> escrowService.fundTransaction(escrowId, token));
        verifyNoInteractions(ledgerService);
    }

    @Test
    void expiryTransitionsOnlyPendingTransactionsWhoseDeadlineHasPassed() {
        transaction.setConfirmationDeadline(LocalDateTime.now().minusSeconds(1));
        when(escrowRepository.save(any(EscrowTransaction.class))).thenAnswer(i -> i.getArgument(0));

        String result = escrowService.checkExpiry(escrowId);

        assertEquals("Expired", result);
        assertEquals(EscrowStatus.EXPIRED, transaction.getStatus());
        verify(transitionService).transition(transaction, EscrowStatus.EXPIRED, null,
                "Confirmation window expired");
    }

    @Test
    void expiryDoesNotChangeAlreadyConfirmedTransaction() {
        transaction.setStatus(EscrowStatus.CREATED);
        transaction.setConfirmationDeadline(LocalDateTime.now().minusSeconds(1));

        assertEquals("Not pending confirmation", escrowService.checkExpiry(escrowId));
        assertEquals(EscrowStatus.CREATED, transaction.getStatus());
        verify(transitionService, never()).transition(any(), any(), any(), anyString());
    }
}
