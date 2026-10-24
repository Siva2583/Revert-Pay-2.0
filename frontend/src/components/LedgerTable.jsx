import { useEffect, useRef, useState } from "react";
import Icon from "./Icon";
import TransactionDetailsModal from "./TransactionDetailsModal";
import Button from "./Button";
import { EmptyState } from "./Feedback";
import API from "../services/api";
import { apiRequest } from "../services/request";
import { formatMoney, formatDate } from "../utils/formatters";

function LedgerTable({ ledger = [], compact = false, token }) {
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [transaction, setTransaction] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");
  const detailsRequestRef = useRef({ id: 0, controller: null });

  useEffect(() => {
    return () => {
      detailsRequestRef.current.id += 1;
      detailsRequestRef.current.controller?.abort();
    };
  }, []);

  const sortedEntries = [...ledger].sort(
    (first, second) => Number(second.entry_id || 0) - Number(first.entry_id || 0)
  );
  const data = compact ? sortedEntries.slice(0, 6) : sortedEntries;

  const openTransactionDetails = async (entry) => {
    const requestId = detailsRequestRef.current.id + 1;
    detailsRequestRef.current.controller?.abort();
    const controller = new AbortController();
    detailsRequestRef.current = { id: requestId, controller };

    setSelectedEntry(entry);
    setTransaction(null);
    setDetailsError("");
    setDetailsLoading(true);

    try {
      const result = await apiRequest(
        API.getEscrowLedgerDetails(entry.reference_id),
        {
          token,
          signal: controller.signal,
          fallbackMessage: "Transaction details could not be loaded.",
        }
      );

      if (detailsRequestRef.current.id !== requestId) return;
      setTransaction(result);
    } catch (detailsRequestError) {
      if (
        detailsRequestError.name === "AbortError" ||
        detailsRequestRef.current.id !== requestId
      ) {
        return;
      }

      setDetailsError(
        detailsRequestError.message || "Transaction details could not be loaded."
      );
    } finally {
      if (detailsRequestRef.current.id === requestId) {
        setDetailsLoading(false);
      }
    }
  };

  const closeTransactionDetails = () => {
    detailsRequestRef.current.id += 1;
    detailsRequestRef.current.controller?.abort();
    setSelectedEntry(null);
    setTransaction(null);
    setDetailsError("");
    setDetailsLoading(false);
  };

  if (!ledger.length) {
    return (
      <EmptyState
        compact
        icon="book"
        title="No ledger activity yet"
        description="When funds move, permanent debit and credit records will appear here."
      />
    );
  }

  return (
    <>
      <div
        className="data-table-scroll"
        tabIndex={0}
        role="region"
        aria-label="Ledger entries; scroll horizontally on small screens"
      >
        <table className="data-table ledger-table">
          <caption className="sr-only">Account ledger entries</caption>
          <thead>
            <tr>
              <th scope="col">Entry</th>
              <th scope="col">Reference</th>
              <th scope="col">Recorded at</th>
              <th scope="col" className="numeric-cell">Amount</th>
              <th scope="col" className="action-cell"><span className="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            {data.map((entry, index) => {
              const isCredit = entry.type === "CREDIT";

              return (
                <tr key={entry.entry_id ?? `${entry.reference_id}-${index}`}>
                  <td>
                    <div className="ledger-entry-cell">
                      <span className={`entry-direction ${isCredit ? "credit" : "debit"}`}>
                        <Icon name={isCredit ? "arrowDownLeft" : "arrowUpRight"} size={16} />
                      </span>
                      <div>
                        <strong>{isCredit ? "Credit" : "Debit"}</strong>
                        <span>Entry #{entry.entry_id ?? "—"}</span>
                      </div>
                    </div>
                  </td>
                  <td><span className="reference-value">{entry.reference_id ?? "—"}</span></td>
                  <td>
                    <time className="table-date" dateTime={entry.createdAt || undefined}>
                      {formatDate(entry.createdAt)}
                    </time>
                  </td>
                  <td className={`numeric-cell money-cell ${isCredit ? "credit-money" : "debit-money"}`}>
                    <span aria-label={isCredit ? "Credit" : "Debit"}>{isCredit ? "+" : "−"}</span>
                    {formatMoney(entry.amount)}
                  </td>
                  <td className="action-cell">
                    <Button
                      variant="ghost"
                      size="small"
                      iconAfter="chevron"
                      onClick={() => openTransactionDetails(entry)}
                      aria-label={`View transaction for ledger entry ${entry.entry_id ?? entry.reference_id}`}
                    >
                      Details
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <TransactionDetailsModal
        selectedEntry={selectedEntry}
        transaction={transaction}
        loading={detailsLoading}
        error={detailsError}
        onClose={closeTransactionDetails}
        onRetry={() => {
          if (selectedEntry) openTransactionDetails(selectedEntry);
        }}
      />
    </>
  );
}

export default LedgerTable;
