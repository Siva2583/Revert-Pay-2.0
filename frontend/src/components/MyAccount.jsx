import { useCallback } from "react";
import AccountSnapshot from "./AccountSnapshot";
import LedgerTable from "./LedgerTable";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useResource from "../hooks/useResource";
import { Alert, EmptyState, ErrorState, RefreshButton } from "./Feedback";
import { PageSkeleton } from "./LoadingSpinner";

function MyAccount({ token }) {
  const loader = useCallback(async (signal) => {
    const result = await apiRequest(API.me, {
      token,
      signal,
      fallbackMessage: "Your account could not be loaded.",
    });

    if (!result?.account || !Array.isArray(result.ledger)) {
      throw new Error("The account response was incomplete. Please try again.");
    }

    return result;
  }, [token]);

  const { data, loading, refreshing, error, refresh } = useResource(loader);

  if (loading) {
    return <PageSkeleton metrics={3} rows={5} />;
  }

  if (error && !data) {
    return (
      <ErrorState
        title="Your account is unavailable"
        description={error}
        onRetry={refresh}
        retrying={refreshing}
      />
    );
  }

  if (!data) {
    return (
      <EmptyState
        icon="wallet"
        title="No account information returned"
        description="The server did not return an account profile for this session."
      />
    );
  }

  const { account, ledger } = data;

  return (
    <div className="page-stack">
      <div className="section-heading standalone-heading">
        <div>
          <p className="eyebrow">Account workspace</p>
          <h2>Account summary</h2>
          <p>Review your current profile and ledger-derived financial position.</p>
        </div>
        <RefreshButton refreshing={refreshing} onClick={refresh} />
      </div>

      {error && (
        <Alert tone="warning" title="Couldn’t refresh account data">
          <p>{error} The last loaded information remains visible.</p>
        </Alert>
      )}

      <AccountSnapshot
        account={account}
        balance={data.balance}
        ledger={ledger}
        profile={data}
      />

      <section className="surface-card data-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Immutable records</p>
            <h2>My ledger history</h2>
            <p>Every debit and credit associated with your account.</p>
          </div>
          <span className="record-count">{ledger.length} {ledger.length === 1 ? "entry" : "entries"}</span>
        </div>
        <LedgerTable ledger={ledger} token={token} />
      </section>
    </div>
  );
}

export default MyAccount;
