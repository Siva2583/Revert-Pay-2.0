import { useCallback, useMemo } from "react";
import Icon from "./Icon";
import Button from "./Button";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useResource from "../hooks/useResource";
import { getRoleLabel } from "../utils/auth";
import { formatDate, formatMoney } from "../utils/formatters";
import { Alert, EmptyState, ErrorState, RefreshButton, StatusBadge } from "./Feedback";
import { PageSkeleton } from "./LoadingSpinner";
import { getEscrowId } from "../utils/escrow";

const protectedStatuses = ["FUNDED", "SHIPPED", "UNDER_REVIEW"];

function RecentLedger({ entries }) {
  if (!entries.length) {
    return <EmptyState compact icon="book" title="No ledger activity" description="Recent debit and credit entries will appear here." />;
  }

  const recent = [...entries]
    .sort((first, second) => Number(second.entry_id || 0) - Number(first.entry_id || 0))
    .slice(0, 5);

  return (
    <div className="ledger-activity-list">
      {recent.map((entry, index) => {
        const isCredit = entry.type === "CREDIT";
        return (
          <div className="ledger-activity-item" key={entry.entry_id ?? index}>
            <span className={`entry-direction ${isCredit ? "credit" : "debit"}`}><Icon name={isCredit ? "arrowDownLeft" : "arrowUpRight"} size={16} /></span>
            <div className="activity-primary"><strong>{isCredit ? "Credit posted" : "Debit posted"}</strong><span>Reference #{entry.reference_id ?? "—"} · Entry #{entry.entry_id ?? "—"}</span></div>
            <div className="activity-secondary"><strong className={isCredit ? "credit-money" : "debit-money"}>{isCredit ? "+" : "−"}{formatMoney(entry.amount)}</strong><time dateTime={entry.createdAt || undefined}>{formatDate(entry.createdAt)}</time></div>
          </div>
        );
      })}
    </div>
  );
}

function Overview({ token, role, setPage }) {
  const loader = useCallback(async (signal) => {
    if (role === "ADMIN") {
      const [ledger, disputes] = await Promise.all([
        apiRequest(API.adminLedger, { token, signal, fallbackMessage: "The holding ledger could not be loaded." }),
        apiRequest(API.adminEscrows, { token, signal, fallbackMessage: "The dispute queue could not be loaded." }),
      ]);

      if (!ledger || !Array.isArray(ledger.recentEntries) || !Array.isArray(disputes)) {
        throw new Error("The overview response was incomplete. Please try again.");
      }

      return { kind: "admin", ledger, escrows: disputes };
    }

    const profile = await apiRequest(API.me, {
      token,
      signal,
      fallbackMessage: "Your account overview could not be loaded.",
    });

    if (!profile?.account || !Array.isArray(profile.ledger)) {
      throw new Error("The account overview response was incomplete. Please try again.");
    }

    let escrows = [];
    if (role === "BUYER" || role === "SELLER") {
      const escrowData = await apiRequest(
        role === "BUYER" ? API.buyerEscrows : API.sellerEscrows,
        { token, signal, fallbackMessage: "Escrow activity could not be loaded." }
      );

      if (!Array.isArray(escrowData)) {
        throw new Error("The escrow overview response was incomplete. Please try again.");
      }
      escrows = escrowData;
    }

    return { kind: "account", profile, escrows };
  }, [role, token]);

  const { data, loading, refreshing, error, refresh } = useResource(loader);
  const escrows = data?.escrows || [];

  const metrics = useMemo(() => {
    if (!data) return null;

    if (data.kind === "admin") {
      return {
        balance: data.ledger.balance,
        ledgerCount: data.ledger.totalEntries ?? data.ledger.recentEntries.length,
        active: data.escrows.filter((item) => item.status === "UNDER_REVIEW").length,
        protectedAmount: data.escrows.reduce((sum, item) => sum + Number(item.amount || 0), 0),
      };
    }

    const activeEscrows = data.escrows.filter((item) => protectedStatuses.includes(item.status));
    return {
      balance: data.profile.balance,
      ledgerCount: data.profile.ledger.length,
      active: activeEscrows.length,
      protectedAmount: activeEscrows.reduce((sum, item) => sum + Number(item.amount || 0), 0),
    };
  }, [data]);

  if (loading) return <PageSkeleton metrics={4} rows={5} />;

  if (error && !data) {
    return <ErrorState title="Your overview is unavailable" description={error} onRetry={refresh} retrying={refreshing} />;
  }

  if (!data || !metrics) {
    return <EmptyState icon="grid" title="No overview data returned" description="The server did not return information for this workspace." />;
  }

  const isAdmin = data.kind === "admin";
  const ledgerEntries = isAdmin ? data.ledger.recentEntries : data.profile.ledger;
  const ledgerPage = isAdmin ? "admin-ledger" : "my-account";
  const escrowPage = isAdmin ? "admin-escrows" : role === "BUYER" ? "buyer-escrows" : "seller-escrows";
  const firstName = !isAdmin && data.profile.name ? data.profile.name.split(" ")[0] : null;
  const attentionCount = isAdmin
    ? escrows.filter((item) => item.status === "UNDER_REVIEW").length
    : role === "BUYER"
      ? escrows.filter((item) => item.status === "SHIPPED").length
      : escrows.filter((item) => item.status === "FUNDED").length;

  const recentEscrows = [...escrows]
    .sort((first, second) => new Date(second.createdAt || 0) - new Date(first.createdAt || 0))
    .slice(0, 5);

  return (
    <div className="page-stack overview-page">
      <div className="overview-topline">
        <span><Icon name="activity" size={15} />Workspace snapshot</span>
        <RefreshButton refreshing={refreshing} onClick={refresh} />
      </div>

      {error && <Alert tone="warning" title="Couldn’t refresh the overview"><p>{error} The last loaded information remains visible.</p></Alert>}

      <section className="overview-welcome">
        <div className="overview-welcome-copy">
          <p className="eyebrow">{getRoleLabel(role)} workspace</p>
          <h2>{firstName ? `Welcome back, ${firstName}.` : "Financial operations, clearly organized."}</h2>
          <p>
            {isAdmin
              ? "Monitor holding-account records and focus on disputes that need an operational decision."
              : role === "BUYER"
                ? "Track your ledger-derived balance, protected purchases, and deliveries awaiting confirmation."
                : "Track your ledger-derived balance, incoming protected payments, and orders ready to ship."}
          </p>
          <div className="hero-balance">
            <span>{isAdmin ? "Holding-account balance" : "Available balance"}</span>
            <strong>{formatMoney(metrics.balance)}</strong>
            <small>Calculated from ledger entries</small>
          </div>

          <div className="button-group">
            {role === "BUYER" && <Button icon="plus" onClick={() => setPage("escrow")}>Initiate payment</Button>}
            {role === "SELLER" && <Button icon="package" onClick={() => setPage("seller-escrows")}>Manage orders</Button>}
            {isAdmin && (
              <>
                <Button icon="shield" onClick={() => setPage("admin-escrows")}>Review disputes</Button>
                <Button variant="secondary" icon="search" onClick={() => setPage("accounts")}>Account lookup</Button>
                <Button variant="ghost" icon="plus" onClick={() => setPage("create")}>Create account</Button>
              </>
            )}
            {!isAdmin && <Button variant="secondary" iconAfter="arrowRight" onClick={() => setPage(ledgerPage)}>View my ledger</Button>}
          </div>
        </div>

        <button type="button" className="attention-card" onClick={() => setPage(escrowPage)}>
          <span className="attention-card-icon"><Icon name={attentionCount ? "clock" : "checkCircle"} size={22} /></span>
          <span className="attention-card-label">Current focus</span>
          <strong>{attentionCount}</strong>
          <p>
            {isAdmin
              ? attentionCount === 1 ? "dispute under review" : "disputes under review"
              : role === "BUYER"
                ? attentionCount === 1 ? "shipped order awaiting delivery" : "shipped orders awaiting delivery"
                : attentionCount === 1 ? "funded order ready to ship" : "funded orders ready to ship"}
          </p>
          <span className="attention-link">Open workspace <Icon name="arrowRight" size={15} /></span>
        </button>
      </section>

      <section className="metrics-grid metrics-three overview-metrics" aria-label="Financial overview">
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Ledger entries</span><span className="metric-icon"><Icon name="book" size={18} /></span></div><strong className="metric-value">{metrics.ledgerCount}</strong><p>{isAdmin ? "Total holding-account records" : "Records on your account"}</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">{isAdmin ? "Open disputes" : "Active escrows"}</span><span className="metric-icon"><Icon name="shield" size={18} /></span></div><strong className="metric-value">{metrics.active}</strong><p>{isAdmin ? "Currently under review" : "Funded, shipped, or under review"}</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">{isAdmin ? "Disputed value" : "Protected value"}</span><span className="metric-icon"><Icon name="lock" size={18} /></span></div><strong className="metric-value">{formatMoney(metrics.protectedAmount)}</strong><p>{isAdmin ? "Value in the returned dispute queue" : "Amount in active protected escrows"}</p></article>
      </section>

      <div className="overview-columns">
        <section className="surface-card activity-panel">
          <div className="section-heading">
            <div><p className="eyebrow">Ledger activity</p><h2>Recent entries</h2><p>Latest records from the {isAdmin ? "holding account" : "account ledger"}.</p></div>
            <Button variant="ghost" size="small" iconAfter="chevron" onClick={() => setPage(ledgerPage)}>View all</Button>
          </div>
          <RecentLedger entries={ledgerEntries} />
        </section>

        <section className="surface-card activity-panel">
          <div className="section-heading">
            <div><p className="eyebrow">Escrow activity</p><h2>{isAdmin ? "Dispute queue" : "Recent escrows"}</h2><p>Current records returned by the escrow workspace.</p></div>
            <Button variant="ghost" size="small" iconAfter="chevron" onClick={() => setPage(escrowPage)}>View all</Button>
          </div>

          {recentEscrows.length ? (
            <div className="escrow-activity-list">
              {recentEscrows.map((escrow) => (
                <button type="button" className="escrow-activity-item" key={getEscrowId(escrow)} onClick={() => setPage(escrowPage)}>
                  <div className="activity-primary"><strong>{escrow.itemName || "Unnamed item"}</strong><span>Escrow #{getEscrowId(escrow)} · {formatDate(escrow.createdAt)}</span></div>
                  <div className="activity-secondary"><strong>{formatMoney(escrow.amount)}</strong><StatusBadge status={escrow.status} /></div>
                </button>
              ))}
            </div>
          ) : (
            <EmptyState compact icon="shield" title={isAdmin ? "No open disputes" : "No escrow activity"} description={isAdmin ? "The dispute queue is currently clear." : "Escrow records will appear here when available."} />
          )}
        </section>
      </div>
    </div>
  );
}

export default Overview;
