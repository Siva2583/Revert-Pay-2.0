import { useCallback, useMemo, useState } from "react";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useResource from "../hooks/useResource";
import useAsyncAction from "../hooks/useAsyncAction";
import Icon from "./Icon";
import Button from "./Button";
import { FormField } from "./Input";
import { Alert, EmptyState, ErrorState, RefreshButton, StatusBadge } from "./Feedback";
import { EscrowListSkeleton } from "./LoadingSpinner";
import EscrowCard, { EscrowContext } from "./EscrowCard";
import { getEscrowId, getParty } from "../utils/escrow";
import EscrowFilters from "./EscrowFilters";
import { ConfirmDialog } from "./Modal";
import { formatDate, formatStatus } from "../utils/formatters";

const closedStatuses = ["EXPIRED", "CANCELLED", "RELEASED", "REFUNDED"];

function SellerEscrows({ token, setToast }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [responseText, setResponseText] = useState({});
  const [confirmation, setConfirmation] = useState(null);
  const [actionError, setActionError] = useState(null);
  const { pending, run } = useAsyncAction();

  const loader = useCallback(async (signal) => {
    const sellerEscrows = await apiRequest(API.sellerEscrows, {
      token,
      signal,
      fallbackMessage: "Seller escrows could not be loaded.",
    });

    if (!Array.isArray(sellerEscrows)) {
      throw new Error("The escrow response was incomplete. Please try again.");
    }

    const underReview = sellerEscrows.filter((item) => item.status === "UNDER_REVIEW");
    const disputeResults = await Promise.all(underReview.map(async (escrow) => {
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

    disputeResults.forEach((result) => {
      if (result.dispute) disputes[result.id] = result.dispute;
      if (result.error) disputeErrors.push({ id: result.id, message: result.error });
    });

    return { escrows: sellerEscrows, disputes, disputeErrors };
  }, [token]);

  const { data, loading, refreshing, error, refresh } = useResource(loader);
  const escrows = useMemo(() => data?.escrows || [], [data]);
  const disputes = useMemo(() => data?.disputes || {}, [data]);
  const disputeErrors = data?.disputeErrors || [];

  const summary = useMemo(() => ({
    total: escrows.length,
    ready: escrows.filter((item) => item.status === "FUNDED").length,
    shipped: escrows.filter((item) => item.status === "SHIPPED").length,
    closed: escrows.filter((item) => closedStatuses.includes(item.status)).length,
  }), [escrows]);

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
      return [escrow.itemName, getEscrowId(escrow), escrow.status, buyer.name, buyer.email]
        .join(" ")
        .toLowerCase()
        .includes(query);
    });
  }, [escrows, search, statusFilter]);

  const shipEscrow = async () => {
    if (!confirmation || pending) return;
    const escrow = confirmation;
    const id = getEscrowId(escrow);

    await run(`ship-${id}`, async () => {
      setActionError(null);

      try {
        await apiRequest(API.escrowAction(id, "ship"), {
          token,
          method: "POST",
          fallbackMessage: "The escrow could not be marked as shipped.",
        });

        setConfirmation(null);
        setToast({
          type: "success",
          title: "Item marked as shipped",
          message: "The escrow has moved to SHIPPED.",
        });
        await refresh();
      } catch (actionRequestError) {
        setConfirmation(null);
        setActionError({ id, message: actionRequestError.message });
      }
    });
  };

  const respondToDispute = async (event, escrowId) => {
    event.preventDefault();
    if (pending) return;

    const dispute = disputes[escrowId];
    const response = responseText[escrowId]?.trim();

    if (!dispute) {
      setActionError({ id: escrowId, message: "Dispute details are unavailable. Refresh before responding." });
      return;
    }

    if (!response) {
      setActionError({ id: escrowId, message: "Enter a response before submitting." });
      return;
    }

    await run(`respond-${escrowId}`, async () => {
      setActionError(null);

      try {
        await apiRequest(API.respondToDispute(dispute.id), {
          token,
          method: "POST",
          body: { response },
          fallbackMessage: "Your dispute response could not be submitted.",
        });

        setResponseText((current) => ({ ...current, [escrowId]: "" }));
        setToast({
          type: "success",
          title: "Response submitted",
          message: "Your response has been recorded for administrative review.",
        });
        await refresh();
      } catch (actionRequestError) {
        setActionError({ id: escrowId, message: actionRequestError.message });
      }
    });
  };

  if (loading) return <EscrowListSkeleton />;

  if (error && !data) {
    return <ErrorState title="Seller escrows are unavailable" description={error} onRetry={refresh} retrying={refreshing} />;
  }

  const clearFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
  };

  return (
    <div className="page-stack">
      <div className="section-heading standalone-heading">
        <div><p className="eyebrow">Seller workspace</p><h2>Order operations</h2><p>Review funded payments, record shipment, and manage dispute responses.</p></div>
        <RefreshButton refreshing={refreshing} onClick={refresh} />
      </div>

      {error && data && <Alert tone="warning" title="Couldn’t refresh escrows"><p>{error} The last loaded orders remain visible.</p></Alert>}
      {disputeErrors.length > 0 && (
        <Alert tone="warning" title="Some dispute details need attention">
          <p>{disputeErrors.length} {disputeErrors.length === 1 ? "dispute" : "disputes"} could not be loaded. Affected cards include the available error details.</p>
        </Alert>
      )}

      <section className="metrics-grid" aria-label="Seller escrow summary">
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Total escrows</span><span className="metric-icon"><Icon name="package" size={18} /></span></div><strong className="metric-value">{summary.total}</strong><p>All transactions assigned to you</p></article>
        <article className="metric-card metric-card-emphasis"><div className="metric-card-top"><span className="metric-label">Ready to ship</span><span className="metric-icon metric-icon-success"><Icon name="package" size={18} /></span></div><strong className="metric-value">{summary.ready}</strong><p>Funded orders awaiting shipment</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Shipped</span><span className="metric-icon"><Icon name="activity" size={18} /></span></div><strong className="metric-value">{summary.shipped}</strong><p>Orders with shipment recorded</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Closed</span><span className="metric-icon"><Icon name="checkCircle" size={18} /></span></div><strong className="metric-value">{summary.closed}</strong><p>Completed or terminal transactions</p></article>
      </section>

      {escrows.length > 0 && <EscrowFilters search={search} onSearchChange={setSearch} status={statusFilter} onStatusChange={setStatusFilter} statuses={statuses} resultCount={filteredEscrows.length} totalCount={escrows.length} searchLabel="Search seller escrows" />}

      {escrows.length === 0 ? (
        <div className="surface-card"><EmptyState icon="package" title="No incoming payments" description="When a buyer creates an escrow with you as the seller, it will appear here." /></div>
      ) : filteredEscrows.length === 0 ? (
        <div className="surface-card"><EmptyState compact icon="search" title="No matching escrows" description="Try a different search or clear the status filter." action={<Button variant="secondary" onClick={clearFilters}>Clear filters</Button>} /></div>
      ) : (
        <div className="escrow-list">
          {filteredEscrows.map((escrow) => {
            const id = getEscrowId(escrow);
            const buyer = getParty(escrow.buyer, escrow.buyerName);
            const dispute = disputes[id];
            const disputeError = disputeErrors.find((item) => item.id === id);
            const isResponding = pending === `respond-${id}`;

            return (
              <EscrowCard key={id} escrow={escrow} parties={[{ label: "Buyer", ...buyer }]} icon="package">
                {actionError?.id === id && <Alert tone="error" title="Action couldn’t be completed"><p>{actionError.message || "Please try again."}</p></Alert>}

                {escrow.status === "FUNDED" && (
                  <div className="escrow-action-panel">
                    <div><strong>Payment is funded and ready</strong><p>Record shipment only after the item has been dispatched.</p></div>
                    <Button icon="package" onClick={() => setConfirmation(escrow)} disabled={pending !== null}>Mark as shipped</Button>
                  </div>
                )}

                {escrow.status === "SHIPPED" && (
                  <EscrowContext icon="package" title="Shipment recorded" description={`Shipped ${formatDate(escrow.shippedAt)}. The buyer can now confirm delivery or raise a dispute.`} meta={escrow.autoReleaseAt && <><span>Auto-release</span><strong>{formatDate(escrow.autoReleaseAt)}</strong></>} />
                )}

                {escrow.status === "UNDER_REVIEW" && (
                  <section className="dispute-record">
                    <div className="dispute-record-heading"><div><p className="eyebrow">Administrative review</p><h3>Buyer dispute</h3></div>{dispute && <StatusBadge status={dispute.status} />}</div>
                    {disputeError && <Alert tone="warning" title="Dispute details unavailable"><p>{disputeError.message}</p></Alert>}
                    {dispute ? (
                      <>
                        <dl className="dispute-details-grid">
                          <div><dt>Reason</dt><dd>{formatStatus(dispute.reason)}</dd></div>
                          <div><dt>Buyer description</dt><dd>{dispute.description || "No description provided."}</dd></div>
                        </dl>
                        {dispute.status === "RESPONDED" ? (
                          <div className="seller-response-record"><span>Your response</span><p>{dispute.sellerResponse || "—"}</p><small>Waiting for administrative resolution.</small></div>
                        ) : (
                          <form className="dispute-response-form" onSubmit={(event) => respondToDispute(event, id)}>
                            <FormField id={`seller-response-${id}`} label="Your response" hint="Explain your position for the administrator reviewing this dispute." required>
                              <textarea id={`seller-response-${id}`} rows={4} value={responseText[id] ?? dispute.sellerResponse ?? ""} onChange={(event) => setResponseText((current) => ({ ...current, [id]: event.target.value }))} placeholder="Explain your side of the dispute" disabled={isResponding} aria-describedby={`seller-response-${id}-hint`} required />
                            </FormField>
                            <div className="form-actions"><Button type="submit" icon="arrowRight" loading={isResponding} loadingLabel="Submitting response..." disabled={pending !== null}>Submit response</Button></div>
                          </form>
                        )}
                      </>
                    ) : !disputeError && <Alert tone="warning" title="Dispute details unavailable"><p>Refresh the queue before attempting to respond.</p></Alert>}
                  </section>
                )}

                {["PAYMENT_INITIATED", "CREATED"].includes(escrow.status) && <EscrowContext icon="clock" title="Awaiting buyer funding" description="No seller action is available until this payment reaches the funded stage." />}
                {escrow.status === "RELEASED" && <EscrowContext icon="checkCircle" tone="success" title="Funds released" description="This escrow has been released to the seller." />}
                {escrow.status === "REFUNDED" && <EscrowContext icon="refresh" title="Funds refunded" description="This escrow was resolved with a refund to the buyer." />}
                {escrow.status === "CANCELLED" && <EscrowContext icon="close" title="Payment cancelled" description="This initiated payment was cancelled before funding." />}
                {escrow.status === "EXPIRED" && <EscrowContext icon="clock" title="Confirmation window expired" description="This initiated payment expired before confirmation." />}
              </EscrowCard>
            );
          })}
        </div>
      )}

      {confirmation && (
        <ConfirmDialog
          title="Mark this item as shipped?"
          description={`Confirm that ${confirmation.itemName || "this item"} has been dispatched. This moves the escrow to SHIPPED and starts the delivery stage.`}
          confirmLabel="Mark as shipped"
          cancelLabel="Review order"
          loading={pending === `ship-${getEscrowId(confirmation)}`}
          loadingLabel="Recording shipment..."
          onConfirm={shipEscrow}
          onCancel={() => setConfirmation(null)}
        />
      )}
    </div>
  );
}

export default SellerEscrows;
