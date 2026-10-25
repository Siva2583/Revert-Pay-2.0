import { useCallback } from "react";
import Icon from "./Icon";
import LedgerTable from "./LedgerTable";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useResource from "../hooks/useResource";
import { formatMoney } from "../utils/formatters";
import { Alert, EmptyState, ErrorState, RefreshButton } from "./Feedback";
import { PageSkeleton } from "./LoadingSpinner";

function AdminLedger({ token }) {
  const loader = useCallback(async (signal) => {
    const result = await apiRequest(API.adminLedger, {
      token,
      signal,
      fallbackMessage: "The system ledger could not be loaded.",
    });

    if (!result || !Array.isArray(result.recentEntries)) {
      throw new Error("The system ledger response was incomplete. Please try again.");
    }

    return result;
  }, [token]);

  const { data: ledger, loading, refreshing, error, refresh } = useResource(loader);

  if (loading) return <PageSkeleton metrics={4} rows={6} />;

  if (error && !ledger) {
    return (
      <ErrorState
        title="System ledger unavailable"
        description={error}
        onRetry={refresh}
        retrying={refreshing}
      />
    );
  }

  if (!ledger) {
    return (
      <EmptyState
        icon="book"
        title="No ledger information returned"
        description="The server did not return holding-account information."
      />
    );
  }

  const entries = ledger.recentEntries;

  return (
    <div className="page-stack">
      <div className="section-heading standalone-heading">
        <div>
          <p className="eyebrow">Administrative ledger</p>
          <h2>Holding account activity</h2>
          <p>Operational totals and the most recent escrow holding-account entries.</p>
        </div>
        <RefreshButton refreshing={refreshing} onClick={refresh} label="Refresh ledger" />
      </div>

      {error && (
        <Alert tone="warning" title="Couldn’t refresh the ledger">
          <p>{error} The last loaded ledger remains visible.</p>
        </Alert>
      )}

      <section className="metrics-grid" aria-label="System ledger summary">
        <article className="metric-card">
          <div className="metric-card-top"><span className="metric-label">Holding account</span><span className="metric-icon"><Icon name="wallet" size={18} /></span></div>
          <strong className="metric-value metric-account-number">{ledger.accountNumber || "—"}</strong>
          <p>Account ID: {ledger.accountId ?? "—"}</p>
        </article>
        <article className="metric-card metric-card-emphasis">
          <div className="metric-card-top"><span className="metric-label">Current balance</span><span className="metric-icon metric-icon-success"><Icon name="activity" size={18} /></span></div>
          <strong className="metric-value">{formatMoney(ledger.balance)}</strong>
          <p>Calculated from ledger entries</p>
        </article>
        <article className="metric-card">
          <div className="metric-card-top"><span className="metric-label">Total credits</span><span className="metric-icon metric-icon-success"><Icon name="arrowDownLeft" size={18} /></span></div>
          <strong className="metric-value">{formatMoney(ledger.totalCredits)}</strong>
          <p>Recorded holding-account credits</p>
        </article>
        <article className="metric-card">
          <div className="metric-card-top"><span className="metric-label">Total debits</span><span className="metric-icon"><Icon name="arrowUpRight" size={18} /></span></div>
          <strong className="metric-value">{formatMoney(ledger.totalDebits)}</strong>
          <p>Recorded holding-account debits</p>
        </article>
      </section>

      <section className="surface-card data-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">System records</p>
            <h2>Recent ledger entries</h2>
            <p>
              Showing {entries.length} recent {entries.length === 1 ? "entry" : "entries"} out of {ledger.totalEntries ?? entries.length} total.
            </p>
          </div>
          <span className="record-count"><Icon name="lock" size={13} />Immutable records</span>
        </div>
        <LedgerTable ledger={entries} token={token} />
      </section>
    </div>
  );
}

export default AdminLedger;
