import { useCallback, useMemo, useState } from "react";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useResource from "../hooks/useResource";
import useAsyncAction from "../hooks/useAsyncAction";
import Icon from "./Icon";
import Button from "./Button";
import { FormField } from "./Input";
import { Alert, EmptyState, ErrorState, RefreshButton } from "./Feedback";
import { EscrowListSkeleton } from "./LoadingSpinner";
import EscrowCard, { EscrowContext } from "./EscrowCard";
import { getEscrowId, getParty } from "../utils/escrow";
import EscrowFilters from "./EscrowFilters";
import { ConfirmDialog } from "./Modal";
import { formatDate, formatMoney } from "../utils/formatters";

const activeStatuses = ["CREATED", "FUNDED", "SHIPPED", "UNDER_REVIEW"];

function BuyerEscrows({ token, setToast, setPage }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [disputeId, setDisputeId] = useState(null);
  const [disputeReason, setDisputeReason] = useState("ITEM_NOT_RECEIVED");
  const [disputeDescription, setDisputeDescription] = useState("");
  const [confirmation, setConfirmation] = useState(null);
  const [actionError, setActionError] = useState(null);
  const { pending, run } = useAsyncAction();

  const loader = useCallback(async (signal) => {
    const data = await apiRequest(API.buyerEscrows, {
      token,
      signal,
      fallbackMessage: "Your escrow orders could not be loaded.",
    });

    if (!Array.isArray(data)) {
      throw new Error("The escrow response was incomplete. Please try again.");
    }

    return data;
  }, [token]);

  const { data, loading, refreshing, error, refresh } = useResource(loader);
  const escrows = useMemo(() => data || [], [data]);

  const summary = useMemo(() => ({
    total: escrows.length,
    shipped: escrows.filter((item) => item.status === "SHIPPED").length,
    released: escrows.filter((item) => item.status === "RELEASED").length,
    active: escrows.filter((item) => activeStatuses.includes(item.status)).length,
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

      const seller = getParty(escrow.seller, escrow.sellerName);
      const searchable = [
        escrow.itemName,
        getEscrowId(escrow),
        escrow.status,
        seller.name,
        seller.email,
      ].join(" ").toLowerCase();

      return searchable.includes(query);
    });
  }, [escrows, search, statusFilter]);

  const confirmDelivery = async () => {
    if (!confirmation || pending) return;
    const escrow = confirmation;
    const id = getEscrowId(escrow);

    await run(`confirm-delivery-${id}`, async () => {
      setActionError(null);

      try {
        await apiRequest(API.escrowAction(id, "confirm-delivery"), {
          token,
          method: "POST",
          fallbackMessage: "Delivery could not be confirmed.",
        });

        setConfirmation(null);
        setToast({
          type: "success",
          title: "Delivery confirmed",
          message: "Payment has been released to the seller.",
        });
        await refresh();
      } catch (actionRequestError) {
        setConfirmation(null);
        setActionError({ id, message: actionRequestError.message });
      }
    });
  };

  const raiseDispute = async (event, id) => {
    event.preventDefault();
    if (pending) return;

    if (!disputeDescription.trim()) {
      setActionError({ id, message: "Describe the issue before submitting the dispute." });
      return;
    }

    await run(`raise-dispute-${id}`, async () => {
      setActionError(null);

      try {
        await apiRequest(API.raiseDispute(id), {
          token,
          method: "POST",
          body: {
            reason: disputeReason,
            description: disputeDescription.trim(),
          },
          fallbackMessage: "The dispute could not be raised.",
        });

        setDisputeId(null);
        setDisputeReason("ITEM_NOT_RECEIVED");
        setDisputeDescription("");
        setToast({
          type: "success",
          title: "Dispute raised",
          message: "The escrow has been moved to administrative review.",
        });
        await refresh();
      } catch (actionRequestError) {
        setActionError({ id, message: actionRequestError.message });
      }
    });
  };

  if (loading) return <EscrowListSkeleton />;

  if (error && !data) {
    return (
      <ErrorState
        title="Your escrows are unavailable"
        description={error}
        onRetry={refresh}
        retrying={refreshing}
      />
    );
  }

  const clearFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
  };

  return (
    <div className="page-stack">
      <div className="section-heading standalone-heading">
        <div>
          <p className="eyebrow">Buyer workspace</p>
          <h2>Escrow portfolio</h2>
          <p>Follow protected payments from funding through release or resolution.</p>
        </div>
        <RefreshButton refreshing={refreshing} onClick={refresh} />
      </div>

      {error && data && (
        <Alert tone="warning" title="Couldn’t refresh escrows">
          <p>{error} The last loaded orders remain visible.</p>
        </Alert>
      )}

      <section className="metrics-grid" aria-label="Buyer escrow summary">
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Total orders</span><span className="metric-icon"><Icon name="shield" size={18} /></span></div><strong className="metric-value">{summary.total}</strong><p>All returned escrow records</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Awaiting delivery</span><span className="metric-icon"><Icon name="package" size={18} /></span></div><strong className="metric-value">{summary.shipped}</strong><p>Orders currently marked shipped</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Released</span><span className="metric-icon metric-icon-success"><Icon name="checkCircle" size={18} /></span></div><strong className="metric-value">{summary.released}</strong><p>Completed escrow releases</p></article>
        <article className="metric-card"><div className="metric-card-top"><span className="metric-label">Active</span><span className="metric-icon"><Icon name="activity" size={18} /></span></div><strong className="metric-value">{summary.active}</strong><p>Funded, shipped, or in progress</p></article>
      </section>

      {escrows.length > 0 && (
        <EscrowFilters
          search={search}
          onSearchChange={setSearch}
          status={statusFilter}
          onStatusChange={setStatusFilter}
          statuses={statuses}
          resultCount={filteredEscrows.length}
          totalCount={escrows.length}
          searchLabel="Search your escrow orders"
        />
      )}

      {escrows.length === 0 ? (
        <div className="surface-card">
          <EmptyState
            icon="shield"
            title="No escrow orders yet"
            description="Your purchases will appear here after you initiate an escrow payment."
            action={<Button icon="plus" onClick={() => setPage("escrow")}>Initiate a payment</Button>}
          />
        </div>
      ) : filteredEscrows.length === 0 ? (
        <div className="surface-card">
          <EmptyState
            compact
            icon="search"
            title="No matching escrows"
            description="Try a different search or clear the status filter."
            action={<Button variant="secondary" onClick={clearFilters}>Clear filters</Button>}
          />
        </div>
      ) : (
        <div className="escrow-list">
          {filteredEscrows.map((escrow) => {
            const id = getEscrowId(escrow);
            const seller = getParty(escrow.seller, escrow.sellerName);
            const isDisputing = pending === `raise-dispute-${id}`;

            return (
              <EscrowCard
                key={id}
                escrow={escrow}
                parties={[{ label: "Seller", ...seller }]}
                icon="shield"
              >
                {actionError?.id === id && (
                  <Alert tone="error" title="Action couldn’t be completed">
                    <p>{actionError.message || "Please try again."}</p>
                  </Alert>
                )}

                {escrow.status === "SHIPPED" && (
                  <>
                    <EscrowContext
                      icon="package"
                      title="Shipment recorded"
                      description={`Shipped ${formatDate(escrow.shippedAt)}. Confirm only after you receive the item.`}
                      meta={escrow.autoReleaseAt && <><span>Auto-release</span><strong>{formatDate(escrow.autoReleaseAt)}</strong></>}
                    />
                    <div className="escrow-action-panel">
                      <div><strong>Order delivered?</strong><p>Confirming delivery releases the payment to the seller.</p></div>
                      <div className="button-group">
                        <Button
                          variant="secondary"
                          icon="shield"
                          onClick={() => {
                            if (disputeId !== id) setDisputeDescription("");
                            setDisputeId(disputeId === id ? null : id);
                            setActionError(null);
                          }}
                          disabled={pending !== null}
                        >
                          Raise dispute
                        </Button>
                        <Button icon="check" onClick={() => setConfirmation(escrow)} disabled={pending !== null}>Confirm delivery</Button>
                      </div>
                    </div>

                    {disputeId === id && (
                      <form className="dispute-form" onSubmit={(event) => raiseDispute(event, id)}>
                        <div className="dispute-form-heading"><Icon name="alertCircle" size={19} /><div><strong>Raise a dispute</strong><p>Provide a clear explanation for administrative review.</p></div></div>
                        <div className="dispute-form-grid">
                          <FormField id={`dispute-reason-${id}`} label="Reason" required>
                            <select id={`dispute-reason-${id}`} value={disputeReason} onChange={(event) => setDisputeReason(event.target.value)} disabled={isDisputing} required>
                              <option value="ITEM_NOT_RECEIVED">Item not received</option>
                              <option value="ITEM_NOT_AS_DESCRIBED">Item not as described</option>
                              <option value="DAMAGED_ITEM">Damaged item</option>
                              <option value="WRONG_ITEM">Wrong item</option>
                              <option value="COUNTERFEIT_ITEM">Counterfeit item</option>
                              <option value="SELLER_ISSUE">Seller issue</option>
                              <option value="OTHER">Other</option>
                            </select>
                          </FormField>
                          <FormField id={`dispute-description-${id}`} label="Description" required>
                            <textarea id={`dispute-description-${id}`} rows={4} value={disputeDescription} onChange={(event) => setDisputeDescription(event.target.value)} placeholder="Describe what happened with this order" disabled={isDisputing} required />
                          </FormField>
                        </div>
                        <div className="form-actions">
                          <Button variant="secondary" onClick={() => setDisputeId(null)} disabled={isDisputing}>Cancel</Button>
                          <Button type="submit" icon="shield" loading={isDisputing} loadingLabel="Submitting dispute..." disabled={pending !== null}>Submit dispute</Button>
                        </div>
                      </form>
                    )}
                  </>
                )}

                {escrow.status === "FUNDED" && <EscrowContext icon="shield" tone="success" title="Payment secured" description="Your payment is held in escrow while you wait for the seller to ship the item." />}
                {escrow.status === "PAYMENT_INITIATED" && <EscrowContext icon="clock" title="Payment awaiting review" description="This payment has been initiated but has not been confirmed or funded." />}
                {escrow.status === "CREATED" && <EscrowContext icon="clock" title="Payment confirmed" description="This escrow is confirmed and awaiting funding." />}
                {escrow.status === "UNDER_REVIEW" && <EscrowContext icon="alertCircle" tone="warning" title="Dispute under review" description="An administrator is reviewing this escrow. No buyer action is currently available." />}
                {escrow.status === "RELEASED" && <EscrowContext icon="checkCircle" tone="success" title="Payment released" description="The escrow funds have been released to the seller." />}
                {escrow.status === "REFUNDED" && <EscrowContext icon="refresh" title="Funds refunded" description="The protected funds have been returned to the buyer." />}
                {escrow.status === "CANCELLED" && <EscrowContext icon="close" title="Payment cancelled" description="This initiated payment was cancelled before funding." />}
                {escrow.status === "EXPIRED" && <EscrowContext icon="clock" title="Confirmation window expired" description="This initiated payment expired before confirmation." />}
              </EscrowCard>
            );
          })}
        </div>
      )}

      {confirmation && (
        <ConfirmDialog
          title="Confirm delivery and release funds?"
          description={`Confirm that you received ${confirmation.itemName || "this item"}. This releases ${formatMoney(confirmation.amount)} to the seller.`}
          confirmLabel="Confirm delivery"
          cancelLabel="Not yet"
          loading={pending === `confirm-delivery-${getEscrowId(confirmation)}`}
          loadingLabel="Confirming delivery..."
          onConfirm={confirmDelivery}
          onCancel={() => setConfirmation(null)}
        />
      )}
    </div>
  );
}

export default BuyerEscrows;
