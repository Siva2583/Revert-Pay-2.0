package com.revertpay.escrow;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface EscrowRepository extends JpaRepository<EscrowTransaction,Long> {
    Optional<EscrowTransaction> findByIdempotencyKey(String idempotencyKey);
    //Optional<EscrowTransaction> findBy
    List<EscrowTransaction> findByStatusAndAutoReleaseAtLessThanEqual(
            EscrowStatus status,
            LocalDateTime time
    );
    List<EscrowTransaction> findByBuyerId(Long buyerId);

    List<EscrowTransaction> findBySellerId(Long sellerId);
    EscrowTransaction findById(long escrowId);
    List<EscrowTransaction> findByStatus(EscrowStatus status);
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT e FROM EscrowTransaction e WHERE e.id = :id")
    Optional<EscrowTransaction> findByIdForUpdate(@Param("id") Long id);
    



}
