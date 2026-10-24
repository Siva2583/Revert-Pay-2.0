import Icon from "./Icon";
import Modal from "./Modal";
import Button from "./Button";
import { Alert, StatusBadge } from "./Feedback";
import { Skeleton, Spinner } from "./LoadingSpinner";
import { formatMoney, formatDate, formatStatus } from "../utils/formatters";

function Detail({ label, children, mono = false }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd className={mono ? "mono-value" : ""}>{children ?? "—"}</dd>
    </div>
  );
}

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
    <Modal
      title="Transaction details"
      eyebrow={`Ledger entry #${selectedEntry.entry_id ?? "—"}`}
      onClose={onClose}
      size="large"
      className="transaction-details-modal"
    >
      {loading ? (
        <div className="modal-loading" role="status">
          <Spinner size={24} label="Loading transaction details" />
          <div>
            <h3>Loading transaction details</h3>
            <p>Retrieving the escrow record and available audit history.</p>
          </div>
          <div className="modal-skeleton-grid" aria-hidden="true">
            <Skeleton height={110} />
            <Skeleton height={110} />
            <Skeleton height={180} />
          </div>
        </div>
      ) : error ? (
        <div className="modal-error-state">
          <Alert tone="error" title="Unable to load transaction">
            <p>{error}</p>
          </Alert>
          <p>
            This ledger reference may not correspond to an escrow transaction, or the details may be temporarily unavailable.
          </p>
          <Button variant="secondary" icon="refresh" onClick={onRetry}>Try again</Button>
        </div>
      ) : transaction ? (
        <div className="transaction-details-content">
          <section className="transaction-overview-card">
            <div>
              <p className="eyebrow">Escrow #{transaction.escrowId ?? "—"}</p>
              <h3>{transaction.itemName || "Escrow transaction"}</h3>
              <p>Created {formatDate(transaction.createdAt)}</p>
            </div>
            <div className="transaction-overview-value">
              <StatusBadge status={transaction.status} />
              <strong>{formatMoney(transaction.amount)}</strong>
            </div>
          </section>

          <section className="detail-section">
            <div className="detail-section-heading">
              <Icon name="shield" size={18} />
              <h3>Transaction overview</h3>
            </div>
            <dl className="detail-grid">
              <Detail label="Escrow ID" mono>{transaction.escrowId ?? "—"}</Detail>
              <Detail label="Item">{transaction.itemName || "—"}</Detail>
              <Detail label="Amount">{formatMoney(transaction.amount)}</Detail>
              <Detail label="Status"><StatusBadge status={transaction.status} /></Detail>
              <Detail label="Created">{formatDate(transaction.createdAt)}</Detail>
              <Detail label="Shipped">{formatDate(transaction.shippedAt)}</Detail>
              <Detail label="Resolved">{formatDate(transaction.resolvedAt)}</Detail>
              <Detail label="Resolution">{transaction.resolution ? formatStatus(transaction.resolution) : "—"}</Detail>
            </dl>
          </section>

          <div className="party-detail-grid">
            <section className="detail-section">
              <div className="detail-section-heading">
                <Icon name="user" size={18} />
                <h3>Buyer</h3>
              </div>
              <dl className="party-details">
                <Detail label="Name">{transaction.buyer?.name || "—"}</Detail>
                <Detail label="Email">{transaction.buyer?.email || "—"}</Detail>
                <Detail label="User ID" mono>{transaction.buyer?.userId ?? transaction.buyer?.id ?? "—"}</Detail>
              </dl>
            </section>

            <section className="detail-section">
              <div className="detail-section-heading">
                <Icon name="user" size={18} />
                <h3>Seller</h3>
              </div>
              <dl className="party-details">
                <Detail label="Name">{transaction.seller?.name || "—"}</Detail>
                <Detail label="Email">{transaction.seller?.email || "—"}</Detail>
                <Detail label="User ID" mono>{transaction.seller?.userId ?? transaction.seller?.id ?? "—"}</Detail>
              </dl>
            </section>
          </div>

          <section className="detail-section">
            <div className="detail-section-heading">
              <Icon name="book" size={18} />
              <h3>Related ledger movements</h3>
            </div>
            {transaction.ledgerMovements?.length ? (
              <div className="data-table-scroll" tabIndex={0} role="region" aria-label="Related ledger movements">
                <table className="data-table compact-table">
                  <thead><tr><th>Entry</th><th>Account</th><th>Owner</th><th>Type</th><th className="numeric-cell">Amount</th><th>Created</th></tr></thead>
                  <tbody>
                    {transaction.ledgerMovements.map((movement, index) => (
                      <tr key={movement.entryId ?? index}>
                        <td className="mono-value">#{movement.entryId ?? "—"}</td>
                        <td className="mono-value">{movement.accountNumber || "—"}</td>
                        <td>
                          {movement.accountOwnerType || "—"}
                          {movement.accountOwnerId != null ? ` · ${movement.accountOwnerId}` : ""}
                        </td>
                        <td>{movement.type || "—"}</td>
                        <td className="numeric-cell money-cell">{formatMoney(movement.amount)}</td>
                        <td>{formatDate(movement.createdAt)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="inline-empty"><Icon name="inbox" size={17} />No related ledger movements were returned.</p>
            )}
          </section>

          <section className="detail-section">
            <div className="detail-section-heading">
              <Icon name="activity" size={18} />
              <h3>Status timeline</h3>
            </div>
            {transaction.timeline?.length ? (
              <ol className="audit-timeline">
                {transaction.timeline.map((event, index) => (
                  <li key={event.eventId ?? index}>
                    <span className="timeline-marker" aria-hidden="true" />
                    <div className="timeline-content">
                      <div className="timeline-heading">
                        <strong>
                          {event.fromStatus ? formatStatus(event.fromStatus) : "Start"}
                          <Icon name="arrowRight" size={15} />
                          {formatStatus(event.toStatus)}
                        </strong>
                        <time dateTime={event.timestamp || undefined}>{formatDate(event.timestamp)}</time>
                      </div>
                      <p>{event.reason || "No reason recorded."}</p>
                      <span>Actor ID: {event.actorId ?? "—"}</span>
                    </div>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="inline-empty"><Icon name="clock" size={17} />No status history is available.</p>
            )}
          </section>

          <section className="detail-section">
            <div className="detail-section-heading">
              <Icon name="alertCircle" size={18} />
              <h3>Dispute details</h3>
            </div>
            {transaction.dispute ? (
              <dl className="detail-grid dispute-detail-grid">
                <Detail label="Dispute ID" mono>{transaction.dispute.disputeId ?? transaction.dispute.id ?? "—"}</Detail>
                <Detail label="Reason">{formatStatus(transaction.dispute.reason)}</Detail>
                <Detail label="Status"><StatusBadge status={transaction.dispute.status} /></Detail>
                <Detail label="Description">{transaction.dispute.description || "—"}</Detail>
                <Detail label="Seller response">{transaction.dispute.sellerResponse || "—"}</Detail>
                <Detail label="Created">{formatDate(transaction.dispute.createdAt)}</Detail>
                <Detail label="Responded">{formatDate(transaction.dispute.respondedAt)}</Detail>
                <Detail label="Resolved">{formatDate(transaction.dispute.resolvedAt)}</Detail>
              </dl>
            ) : (
              <p className="inline-empty"><Icon name="checkCircle" size={17} />No dispute is associated with this transaction.</p>
            )}
          </section>
        </div>
      ) : null}
    </Modal>
  );
}

export default TransactionDetailsModal;
