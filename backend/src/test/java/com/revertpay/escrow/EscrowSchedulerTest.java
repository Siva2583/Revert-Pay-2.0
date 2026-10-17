package com.revertpay.escrow;

import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.Mockito.*;


import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

class EscrowSchedulerTest {

    @Test
    void schedulerShouldTriggerAutoReleaseForOverdueEscrows() {
        EscrowRepository repository = mock(EscrowRepository.class);
        EscrowService service = mock(EscrowService.class);

        EscrowTransaction escrow = new EscrowTransaction();
        escrow.setId(999L);
        escrow.setStatus(EscrowStatus.SHIPPED);
        escrow.setAutoReleaseAt(LocalDateTime.now().minusMinutes(1));

        when(repository.findByStatusAndAutoReleaseAtLessThanEqual(
                eq(EscrowStatus.SHIPPED), any(LocalDateTime.class)
        )).thenReturn(List.of(escrow));

        EscrowScheduler scheduler = new EscrowScheduler(repository, service);

        scheduler.autoReleaseEscrows();

        verify(repository).findByStatusAndAutoReleaseAtLessThanEqual(
                eq(EscrowStatus.SHIPPED), any(LocalDateTime.class)
        );
        verify(service).autoReleaseEscrow(999L);
    }

    @Test
    void schedulerShouldNotCallServiceWhenNoEscrowsAreOverdue() {
        EscrowRepository repository = mock(EscrowRepository.class);
        EscrowService service = mock(EscrowService.class);

        when(repository.findByStatusAndAutoReleaseAtLessThanEqual(
                eq(EscrowStatus.SHIPPED), any(LocalDateTime.class)
        )).thenReturn(List.of());

        EscrowScheduler scheduler = new EscrowScheduler(repository, service);

        scheduler.autoReleaseEscrows();

        verify(service, never()).autoReleaseEscrow(anyLong());
    }
    @Test
    void schedulerShouldContinueWhenOneEscrowReleaseFails() {

        EscrowRepository repository = mock(EscrowRepository.class);
        EscrowService service = mock(EscrowService.class);

        EscrowTransaction first = new EscrowTransaction();
        first.setId(101L);

        EscrowTransaction second = new EscrowTransaction();
        second.setId(102L);

        when(repository.findByStatusAndAutoReleaseAtLessThanEqual(
                eq(EscrowStatus.SHIPPED),
                any(LocalDateTime.class)
        )).thenReturn(List.of(first, second));

        doThrow(new RuntimeException("Simulated release failure"))
                .when(service).autoReleaseEscrow(101L);

        EscrowScheduler scheduler = new EscrowScheduler(repository, service);

        // Should not throw even though the first release fails.
        assertDoesNotThrow(scheduler::autoReleaseEscrows);

        // Both escrows should be attempted.
        verify(service).autoReleaseEscrow(101L);
        verify(service).autoReleaseEscrow(102L);
    }
}