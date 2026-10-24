package com.revertpay.ledger;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.math.BigDecimal;
import java.util.List;

public interface LedgerEntryRepository
        extends JpaRepository<LedgerEntry, Long> {


    List<LedgerEntry> findByAccountId(Long id);
    @Query("SELECT le FROM LedgerEntry le WHERE le.reference_id = :referenceId ORDER BY le.createdAt ASC")
    List<LedgerEntry> findByReferenceIdOrderByCreatedAtAsc(@Param("referenceId") long referenceId);

    //List<LedgerEntry> findByReferenceIdOrderByCreatedAtAsc(long referenceId);

    @Query("""
    SELECT COALESCE(
        SUM(
            CASE
                WHEN le.type = com.revertpay.ledger.Type.CREDIT
                THEN le.amount
                ELSE -le.amount
            END
        ),
        0
    )
    FROM LedgerEntry le
    WHERE le.account.id = :accountId
    """)
    BigDecimal calculateBalance(@Param("accountId") Long accountId);


}
