package com.revertpay.escrow;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EscrowStatusLogRepository extends JpaRepository<EscrowStatusLog, Long> {

    List<EscrowStatusLog> findByEscrowTransaction_IdOrderByTimestampAsc(Long escrowId);
}