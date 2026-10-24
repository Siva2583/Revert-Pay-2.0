import { useState } from "react";
import Icon from "./Icon";
import TransactionDetailsModal from "./TransactionDetailsModal";
import {
  formatMoney,
  formatDate,
  readResponse,
} from "../utils/formatters";

function LedgerTable({ ledger = [], compact = false, token }) {
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [transaction, setTransaction] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");

  const data = compact
    ? ledger.slice(-6).reverse()
    : [...ledger].reverse();

  const openTransactionDetails = async (entry) => {
    setSelectedEntry(entry);
    setTransaction(null);
    setDetailsError("");
    setDetailsLoading(true);

    try {
      const response = await fetch(
        `/api/escrow/${entry.reference_id}/ledger-details`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const result = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          result?.message ||
            result?.error ||
            "Unable to load transaction details."
        );
      }

      setTransaction(result);
    } catch (err) {
      setDetailsError(
        err.message || "Unable to load transaction details."
      );
    } finally {
      setDetailsLoading(false);
    }
  };

  const closeTransactionDetails = () => {
    setSelectedEntry(null);
    setTransaction(null);
    setDetailsError("");
    setDetailsLoading(false);
  };

  if (!ledger.length) {
    return (
      <div className="empty-ledger">
        <div className="empty-ledger-icon">
          <Icon name="book" size={24} />
        </div>

        <strong>No ledger activity yet</strong>

        <p>
          When funds move, immutable debit and credit records will appear here.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="ledger-list">
        <div className="ledger-columns">
          <span>Entry</span>
          <span>Reference</span>
          <span>Recorded at</span>
          <span>Amount</span>
        </div>

        {data.map((entry) => {
          const isCredit = entry.type === "CREDIT";

          return (
            <div className="ledger-entry" key={entry.entry_id}>
              <div className="ledger-type">
                <div
                  className={`entry-direction ${
                    isCredit ? "in" : "out"
                  }`}
                >
                  {isCredit ? "+" : "−"}
                </div>

                <div>
                  <strong>
                    {isCredit ? "Credit posted" : "Debit posted"}
                  </strong>
                  <span>{entry.type} ENTRY</span>
                </div>
              </div>

              <div className="reference">
                <span className="mobile-ledger-label">
                  Reference
                </span>
                {entry.reference_id ?? "—"}
              </div>

              <div className="date">
                <span className="mobile-ledger-label">
                  Recorded
                </span>
                {formatDate(entry.createdAt)}
              </div>

              <div
                className={`entry-amount ${
                  isCredit ? "positive" : "negative"
                }`}
              >
                {isCredit ? "+" : "−"} {formatMoney(entry.amount)}
              </div>

              <div className="ledger-transaction-action">
                <button
                  type="button"
                  className="secondary-button ledger-view-transaction"
                  onClick={() => openTransactionDetails(entry)}
                >
                  View transaction
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <TransactionDetailsModal
        selectedEntry={selectedEntry}
        transaction={transaction}
        loading={detailsLoading}
        error={detailsError}
        onClose={closeTransactionDetails}
        onRetry={() => {
          if (selectedEntry) {
            openTransactionDetails(selectedEntry);
          }
        }}
      />
    </>
  );
}

export default LedgerTable;