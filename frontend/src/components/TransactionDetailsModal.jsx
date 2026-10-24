import { formatMoney, formatDate } from "../utils/formatters";

function TransactionDetailsModal({
  selectedEntry,
  transaction,
  loading,
  error,
  onClose,
  onRetry,
}) {
  if (!selectedEntry) return null;

  return (
    <div
      className="transaction-details-backdrop"
      onClick={onClose}
    >
      <section
        className="transaction-details-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="transaction-details-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="transaction-details-header">
          <div>
            <span className="eyebrow">
              LEDGER ENTRY #{selectedEntry.entry_id}
            </span>

            <h2 id="transaction-details-title">
              Escrow Transaction Details
            </h2>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        {loading ? (
          <div className="ledger-state">
            Loading transaction details...
          </div>
        ) : error ? (
          <div className="ledger-error" role="alert">
            <strong>Unable to load transaction</strong>
            <p>{error}</p>
            <p>
              This reference may not correspond to an escrow transaction.
            </p>

            <button
              type="button"
              className="secondary-button"
              onClick={onRetry}
            >
              Try again
            </button>
          </div>
        ) : transaction ? (
          <div className="transaction-details-content">
            <section className="transaction-detail-card">
              <h3>Transaction Overview</h3>

              <dl className="transaction-detail-grid">
                <div>
                  <dt>Escrow ID</dt>
                  <dd>{transaction.escrowId ?? transaction.escrowId === 0 ? transaction.escrowId : "—"}</dd>
                </div>

                <div>
                  <dt>Item</dt>
                  <dd>{transaction.itemName || "—"}</dd>
                </div>

                <div>
                  <dt>Amount</dt>
                  <dd>{formatMoney(transaction.amount)}</dd>
                </div>

                <div>
                  <dt>Status</dt>
                  <dd>{transaction.status || "—"}</dd>
                </div>

                <div>
                  <dt>Created</dt>
                  <dd>{formatDate(transaction.createdAt)}</dd>
                </div>

                <div>
                  <dt>Shipped</dt>
                  <dd>{formatDate(transaction.shippedAt)}</dd>
                </div>

                <div>
                  <dt>Resolved</dt>
                  <dd>{formatDate(transaction.resolvedAt)}</dd>
                </div>

                <div>
                  <dt>Resolution</dt>
                  <dd>{transaction.resolution || "—"}</dd>
                </div>
              </dl>
            </section>

            <section className="transaction-detail-card">
              <h3>Buyer</h3>
              <p>{transaction.buyer?.name || "—"}</p>
              <p>{transaction.buyer?.email || "—"}</p>
              <p>User ID: {transaction.buyer?.userId ?? "—"}</p>
            </section>

            <section className="transaction-detail-card">
              <h3>Seller</h3>
              <p>{transaction.seller?.name || "—"}</p>
              <p>{transaction.seller?.email || "—"}</p>
              <p>User ID: {transaction.seller?.userId ?? "—"}</p>
            </section>

            <section className="transaction-detail-card">
              <h3>Related Ledger Movements</h3>

              {transaction.ledgerMovements?.length ? (
                <div className="ledger-table-wrapper">
                  <table className="ledger-table">
                    <thead>
                      <tr>
                        <th>Entry ID</th>
                        <th>Account</th>
                        <th>Owner</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Created</th>
                      </tr>
                    </thead>

                    <tbody>
                      {transaction.ledgerMovements.map((movement) => (
                        <tr key={movement.entryId}>
                          <td>{movement.entryId}</td>
                          <td>{movement.accountNumber || "—"}</td>
                          <td>
                            {movement.accountOwnerType || "—"}
                            {movement.accountOwnerId != null
                              ? ` #${movement.accountOwnerId}`
                              : ""}
                          </td>
                          <td>{movement.type || "—"}</td>
                          <td>{formatMoney(movement.amount)}</td>
                          <td>{formatDate(movement.createdAt)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No related ledger movements were returned.</p>
              )}
            </section>

            <section className="transaction-detail-card">
              <h3>Status Timeline</h3>

              {transaction.timeline?.length ? (
                <ol className="transaction-timeline">
                  {transaction.timeline.map((event) => (
                    <li key={event.eventId}>
                      <strong>
                        {event.fromStatus || "START"} →{" "}
                        {event.toStatus || "—"}
                      </strong>

                      <p>{event.reason || "No reason recorded."}</p>
                      <p>Actor ID: {event.actorId ?? "—"}</p>
                      <time>{formatDate(event.timestamp)}</time>
                    </li>
                  ))}
                </ol>
              ) : (
                <p>No status history is available.</p>
              )}
            </section>

            <section className="transaction-detail-card">
              <h3>Dispute Details</h3>

              {transaction.dispute ? (
                <>
                  <p>
                    <strong>Dispute ID:</strong>{" "}
                    {transaction.dispute.disputeId ?? "—"}
                  </p>

                  <p>
                    <strong>Reason:</strong>{" "}
                    {transaction.dispute.reason || "—"}
                  </p>

                  <p>
                    <strong>Status:</strong>{" "}
                    {transaction.dispute.status || "—"}
                  </p>

                  <p>
                    <strong>Description:</strong>{" "}
                    {transaction.dispute.description || "—"}
                  </p>

                  <p>
                    <strong>Seller response:</strong>{" "}
                    {transaction.dispute.sellerResponse || "—"}
                  </p>

                  <p>
                    <strong>Created:</strong>{" "}
                    {formatDate(transaction.dispute.createdAt)}
                  </p>

                  <p>
                    <strong>Responded:</strong>{" "}
                    {formatDate(transaction.dispute.respondedAt)}
                  </p>

                  <p>
                    <strong>Resolved:</strong>{" "}
                    {formatDate(transaction.dispute.resolvedAt)}
                  </p>
                </>
              ) : (
                <p>No dispute is associated with this transaction.</p>
              )}
            </section>
          </div>
        ) : null}
      </section>
    </div>
  );
}

export default TransactionDetailsModal;