import { useCallback, useMemo, useState } from "react";
import Icon from "./Icon";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useResource from "../hooks/useResource";
import useAsyncAction from "../hooks/useAsyncAction";
import Button from "./Button";
import { Alert, EmptyState, ErrorState, RefreshButton, StatusBadge } from "./Feedback";
import { EscrowListSkeleton } from "./LoadingSpinner";
import EscrowCard from "./EscrowCard";
import { getEscrowId, getParty } from "../utils/escrow";
import EscrowFilters from "./EscrowFilters";
import { ConfirmDialog } from "./Modal";
import { formatDate, formatMoney, formatStatus } from "../utils/formatters";

function AdminEscrows({ token, setToast }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [resolution, setResolution] = useState(null);
  const [actionError, setActionError] = useState(null);
  const { pending, run } = useAsyncAction();

  const loader = useCallback(async (signal) => {
    const adminEscrows = await apiRequest(API.adminEscrows, {
      token,
      signal,
      fallbackMessage: "The administrative dispute queue could not be loaded.",
    });

    if (!Array.isArray(adminEscrows)) {
      throw new Error("The dispute queue response was incomplete. Please try again.");
    }

    const results = await Promise.all(adminEscrows.map(async (escrow) => {
      const id = getEscrowId(escrow);

      try {
        const dispute = await apiRequest(API.getDispute(id), {
          token,
          signal,
          fallbackMessage: "Dispute details could not be loaded.",
        });
        return { id, dispute, error: null };
      } catch (disputeError) {
        if (disputeError.name === "AbortError") throw disputeError;
        return { id, dispute: null, error: disputeError.message };
      }
    }));

    const disputes = {};
    const disputeErrors = [];

    results.forEach((result) => {
      if (result.dispute) disputes[result.id] = result.dispute;
      if (result.error) disputeErrors.push({ id: result.id, message: result.error });
    });

    return { escrows: adminEscrows, disputes, disputeErrors };
  }, [token]);

  const { data, loading, refreshing, error, refresh } = useResource(loader);
  const escrows = useMemo(() => data?.escrows || [], [data]);
  const disputes = useMemo(() => data?.disputes || {}, [data]);
  const disputeErrors = data?.disputeErrors || [];

  const summary = useMemo(() => ({
    total: escrows.length,
    underReview: escrows.filter((item) => item.status === "UNDER_REVIEW").length,
    totalAmount: escrows.reduce((sum, item) => sum + Number(item.amount || 0), 0),
    withSellerResponse: escrows.filter((item) => disputes[getEscrowId(item)]?.sellerResponse).length,
  }), [escrows, disputes]);

  const statuses = useMemo(
    () => [...new Set(escrows.map((item) => item.status).filter(Boolean))],
    [escrows]
  );

  const filteredEscrows = useMemo(() => {
    const query = search.trim().toLowerCase();

    return escrows.filter((escrow) => {
      if (statusFilter !== "ALL" && escrow.status !== statusFilter) return false;
      if (!query) return true;

      const buyer = getParty(escrow.buyer, escrow.buyerName);
      const seller = getParty(escrow.seller, escrow.sellerName);
      return [escrow.itemName, getEscrowId(escrow), escrow.status, buyer.name, buyer.email, seller.name, seller.email]
        .join(" ")
        .toLowerCase()
        .includes(query);
    });
  }, [escrows, search, statusFilter]);

  const resolveDispute = async () => {
    if (!resolution || pending) return;

    const { dispute, escrow, decision } = resolution;
    const escrowId = getEscrowId(escrow);

    await run(`resolve-${dispute.id}`, async () => {
      setActionError(null);

      try {
        await apiRequest(API.resolveDispute(dispute.id), {
          token,
          method: "POST",
          body: { resolution: decision },
          fallbackMessage: "The dispute could not be resolved.",
        });

        setResolution(null);
        setToast({
          type: "success",
          title: decision === "RELEASE" ? "Funds released" : "Refund approved",
          message: decision === "RELEASE"
            ? "The dispute was resolved in favor of the seller."
            : "The dispute was resolved in favor of the buyer.",
        });
        await refresh();
      } catch (actionRequestError) {
        setResolution(null);
        setActionError({ id: escrowId, message: actionRequestError.message });
      }
    });
  };

  if (loading) return <EscrowListSkeleton />;

  if (error && !data) {
    return <ErrorState title="The dispute queue is unavailable" description={error} onRetry={refresh} retrying={refreshing} />;
  }

  const clearFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
  };

  return (
    <div className="page-stack">
      <div className="section-heading standalone-heading">
        <div><p className="eyebrow">Administrative workspace</p><h2>Dispute queue</h2><p>Review buyer evidence, seller responses, and the available resolution actions.</p></div>
        <RefreshButton refreshing={refreshing} onClick={refresh} />
      </div>

      {error && data && <Alert tone="warning" title="Couldn’t refresh disputes"><p>{error} The last loaded queue remains visible.</p></Alert>}
      {disputeErrors.length > 0 && <Alert tone="warning" title="Some records need attention"><p>{disputeErrors.length} dispute {disputeErrors.length === 1 ? "record" : "records"} could not be fully loaded. Resolution is unavailable where the dispute ID is missing.</p></Alert>}

      <section className="metrics-grid" aria-label="Dispute queue summary">
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Disputes</span><span className="metric-icon"><Icon name="alertCircle" size={18} /></span></div><strong className="metric-value">{summary.total}</strong><p>Records returned to the admin queue</p></article>
        <article className="metric-card metric-card-emphasis"><div className="metric-card-top"><span className="metric-label">Under review</span><span className="metric-icon"><Icon name="clock" size={18} /></span></div><strong className="metric-value">{summary.underReview}</strong><p>Escrows currently under review</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Seller responded</span><span className="metric-icon metric-icon-success"><Icon name="checkCircle" size={18} /></span></div><strong className="metric-value">{summary.withSellerResponse}</strong><p>Records with a seller response</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Protected amount</span><span className="metric-icon"><Icon name="shield" size={18} /></span></div><strong className="metric-value">{formatMoney(summary.totalAmount)}</strong><p>Sum of returned escrow amounts</p></article>
      </section>

      {escrows.length > 0 && <EscrowFilters search={search} onSearchChange={setSearch} status={statusFilter} onStatusChange={setStatusFilter} statuses={statuses} resultCount={filteredEscrows.length} totalCount={escrows.length} searchLabel="Search administrative disputes" />}

      {escrows.length === 0 ? (
        <div className="surface-card"><EmptyState icon="checkCircle" title="No disputes require review" description="The administrative dispute queue is currently clear." /></div>
      ) : filteredEscrows.length === 0 ? (
        <div className="surface-card"><EmptyState compact icon="search" title="No matching disputes" description="Try a different search or clear the status filter." action={<Button variant="secondary" onClick={clearFilters}>Clear filters</Button>} /></div>
      ) : (
        <div className="escrow-list">
          {filteredEscrows.map((escrow) => {
            const id = getEscrowId(escrow);
            const dispute = disputes[id];
            const disputeError = disputeErrors.find((item) => item.id === id);
            const buyer = getParty(escrow.buyer, escrow.buyerName);
            const seller = getParty(escrow.seller, escrow.sellerName);

            return (
              <EscrowCard key={id} escrow={escrow} icon="alertCircle" parties={[{ label: "Buyer", ...buyer }, { label: "Seller", ...seller }]}>
                {actionError?.id === id && <Alert tone="error" title="Resolution couldn’t be completed"><p>{actionError.message || "Please try again."}</p></Alert>}

                <section className="dispute-record admin-dispute-record">
                  <div className="dispute-record-heading"><div><p className="eyebrow">Case evidence</p><h3>Dispute #{dispute?.id ?? "unavailable"}</h3></div>{dispute && <StatusBadge status={dispute.status} />}</div>

                  {disputeError && <Alert tone="warning" title="Dispute details unavailable"><p>{disputeError.message}</p></Alert>}

                  {dispute ? (
                    <>
                      <dl className="dispute-details-grid admin-dispute-details">
                        <div><dt>Reason</dt><dd>{formatStatus(dispute.reason)}</dd></div>
                        <div><dt>Opened</dt><dd>{formatDate(dispute.createdAt)}</dd></div>
                        <div className="detail-span-full"><dt>Buyer description</dt><dd>{dispute.description || "No description provided."}</dd></div>
                        <div className="detail-span-full"><dt>Seller response</dt><dd>{dispute.sellerResponse || "No response from the seller yet."}</dd></div>
                        {dispute.respondedAt && <div><dt>Responded</dt><dd>{formatDate(dispute.respondedAt)}</dd></div>}
                      </dl>

                      <div className="escrow-action-panel admin-resolution-panel">
                        <div><strong>Resolve this dispute</strong><p>Choose where the protected funds should go. Each decision requires confirmation.</p></div>
                        <div className="button-group">
                          <Button variant="secondary" icon="refresh" onClick={() => setResolution({ dispute, escrow, decision: "REFUND" })} disabled={pending !== null}>Refund buyer</Button>
                          <Button icon="check" onClick={() => setResolution({ dispute, escrow, decision: "RELEASE" })} disabled={pending !== null}>Release to seller</Button>
                        </div>
                      </div>
                    </>
                  ) : !disputeError && <Alert tone="warning" title="Resolution unavailable"><p>The dispute ID was not returned. Refresh the queue before taking action.</p></Alert>}
                </section>
              </EscrowCard>
            );
          })}
        </div>
      )}

      {resolution && (
        <ConfirmDialog
          title={resolution.decision === "RELEASE" ? "Release funds to the seller?" : "Refund the buyer?"}
          description={resolution.decision === "RELEASE"
            ? `Resolve this dispute in the seller’s favor and release ${formatMoney(resolution.escrow.amount)} for ${resolution.escrow.itemName || "this item"}.`
            : `Resolve this dispute in the buyer’s favor and return ${formatMoney(resolution.escrow.amount)} for ${resolution.escrow.itemName || "this item"}.`}
          confirmLabel={resolution.decision === "RELEASE" ? "Release to seller" : "Refund buyer"}
          cancelLabel="Review evidence"
          confirmVariant={resolution.decision === "REFUND" ? "danger" : "primary"}
          tone={resolution.decision === "REFUND" ? "warning" : "default"}
          loading={pending === `resolve-${resolution.dispute.id}`}
          loadingLabel={resolution.decision === "RELEASE" ? "Releasing funds..." : "Processing refund..."}
          onConfirm={resolveDispute}
          onCancel={() => setResolution(null)}
        />
      )}
    </div>
  );
}

export default AdminEscrows;
