import { useCallback, useEffect, useState } from "react";
import Icon from "./Icon";
import TransactionDetailsModal from "./TransactionDetailsModal";
import {
  formatMoney,
  formatDate,
  readResponse,
} from "../utils/formatters";

function AdminLedger({ token }) {
  const [ledger, setLedger] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [selectedEntry, setSelectedEntry] = useState(null);
  const [transaction, setTransaction] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");

  const loadLedger = useCallback(
    async (isRefresh = false) => {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      try {
        const response = await fetch("/api/admin/ledger/holding", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await readResponse(response);

        if (!response.ok) {
          throw new Error(
            data?.message ||
              data?.error ||
              "Unable to load system ledger."
          );
        }

        setLedger(data);
      } catch (err) {
        setError(err.message || "Unable to load system ledger.");
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [token]
  );

  useEffect(() => {
    loadLedger();
  }, [loadLedger]);

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

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          data?.message ||
            data?.error ||
            "No escrow transaction details were found for this entry."
        );
      }

      setTransaction(data);
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

  const entries = ledger?.recentEntries || [];

  return (
    <section className="admin-ledger-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">ADMIN WORKSPACE</span>
          <h1>System Ledger</h1>
          <p>
            Monitor the escrow holding account and its ledger activity.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => loadLedger(true)}
          disabled={loading || refreshing}
        >
          <Icon name="activity" />
          {refreshing ? "Refreshing..." : "Refresh Ledger"}
        </button>
      </div>

      {error && (
        <div className="ledger-error" role="alert">
          <strong>Unable to load ledger</strong>
          <p>{error}</p>

          <button
            className="secondary-button"
            onClick={() => loadLedger(true)}
            disabled={refreshing}
          >
            Try again
          </button>
        </div>
      )}

      {loading ? (
        <div className="ledger-state">Loading system ledger...</div>
      ) : ledger ? (
        <>
          <section className="ledger-summary">
            <article className="ledger-stat">
              <span className="ledger-stat-label">HOLDING ACCOUNT</span>
              <h2>{ledger.accountNumber}</h2>
              <p>Account ID: {ledger.accountId}</p>
            </article>

            <article className="ledger-stat">
              <span className="ledger-stat-label">CURRENT BALANCE</span>
              <h2>{formatMoney(ledger.balance)}</h2>
              <p>Calculated from ledger entries</p>
            </article>

            <article className="ledger-stat">
              <span className="ledger-stat-label">TOTAL CREDITS</span>
              <h2>{formatMoney(ledger.totalCredits)}</h2>
              <p>Total recorded credits</p>
            </article>

            <article className="ledger-stat">
              <span className="ledger-stat-label">TOTAL DEBITS</span>
              <h2>{formatMoney(ledger.totalDebits)}</h2>
              <p>Total recorded debits</p>
            </article>
          </section>

          <section className="ledger-table-card">
            <div className="ledger-table-heading">
              <div>
                <h2>Recent Ledger Entries</h2>
                <p>
                  Showing {entries.length} recent entries out of{" "}
                  {ledger.totalEntries ?? entries.length} total entries.
                </p>
                <p>Select an entry to inspect its escrow transaction.</p>
              </div>
            </div>

            {entries.length === 0 ? (
              <div className="ledger-state">
                No ledger entries are available.
              </div>
            ) : (
              <div className="ledger-table-wrapper">
                <table className="ledger-table">
                  <thead>
                    <tr>
                      <th>Entry ID</th>
                      <th>Type</th>
                      <th>Amount</th>
                      <th>Reference ID</th>
                      <th>Created</th>
                      <th>Details</th>
                    </tr>
                  </thead>

                  <tbody>
                    {entries.map((entry) => (
                      <tr key={entry.entry_id}>
                        <td className="ledger-entry-id">
                          {entry.entry_id}
                        </td>

                        <td>
                          <span
                            className={`ledger-type ${
                              String(entry.type).toUpperCase() === "CREDIT"
                                ? "ledger-type-credit"
                                : "ledger-type-debit"
                            }`}
                          >
                            {entry.type}
                          </span>
                        </td>

                        <td className="ledger-amount">
                          {formatMoney(entry.amount)}
                        </td>

                        <td>{entry.reference_id ?? "—"}</td>
                        <td>{formatDate(entry.createdAt)}</td>

                        <td>
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => openTransactionDetails(entry)}
                          >
                            View transaction
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      ) : (
        !error && (
          <div className="ledger-state">
            No ledger information is available.
          </div>
        )
      )}

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
    </section>
  );
}

export default AdminLedger;