import { useRef, useState } from "react";
import Icon from "./Icon";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useAsyncAction from "../hooks/useAsyncAction";
import { formatMoney } from "../utils/formatters";
import Button from "./Button";
import { Input } from "./Input";
import { Alert, StatusBadge } from "./Feedback";
import EscrowLifecycle from "./EscrowLifecycle";
import { ConfirmDialog } from "./Modal";

const actionFeedback = {
  confirm: {
    title: "Payment confirmed",
    message: "The escrow is confirmed and ready to be funded.",
  },
  cancel: {
    title: "Payment declined",
    message: "The initiated escrow payment was cancelled.",
  },
  fund: {
    title: "Escrow funded",
    message: "The payment is now held in escrow.",
  },
};

function EscrowInitiate({ token, setToast, setPage }) {
  const [sellerAccountNumber, setSellerAccountNumber] = useState("");
  const [itemName, setItemName] = useState("");
  const [amount, setAmount] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [confirmation, setConfirmation] = useState(null);
  const idempotencyRef = useRef({ fingerprint: null, key: null });
  const { pending, run } = useAsyncAction();
  const loading = pending !== null;

  const submit = async (event) => {
    event.preventDefault();
    if (pending) return;

    const payload = {
      sellerAccountNumber: sellerAccountNumber.trim(),
      itemName: itemName.trim(),
      amount: Number(amount),
    };
    const fingerprint = JSON.stringify(payload);

    if (idempotencyRef.current.fingerprint !== fingerprint) {
      idempotencyRef.current = {
        fingerprint,
        key: crypto.randomUUID(),
      };
    }

    await run("initiate", async () => {
      setError("");
      setResult(null);

      try {
        const data = await apiRequest(API.escrowInitiate, {
          token,
          method: "POST",
          headers: { "Idempotency-Key": idempotencyRef.current.key },
          body: payload,
          fallbackMessage: "The escrow request could not be initiated.",
        });

        setResult(data);
        idempotencyRef.current = { fingerprint: null, key: null };
        setSellerAccountNumber("");
        setItemName("");
        setAmount("");
        setToast({
          type: "success",
          title: "Payment initiated",
          message: "Review the seller, item, and amount before confirming.",
        });
      } catch (initiateError) {
        setError(initiateError.message || "The escrow request could not be initiated.");
      }
    });
  };

  const performAction = async (action) => {
    if (!result || pending) return;

    const escrowId = result.escrowId ?? result.escrowid;

    await run(`escrow-${action}`, async () => {
      setError("");

      try {
        const data = await apiRequest(API.escrowAction(escrowId, action), {
          token,
          method: "POST",
          fallbackMessage: "The escrow action could not be completed.",
        });

        if (!data) {
          setConfirmation(null);
          setError("The action was accepted, but updated escrow details were not returned. Open My escrows to retrieve the current state.");
          return;
        }

        setResult(data);
        setConfirmation(null);
        setToast({ type: "success", ...actionFeedback[action] });
      } catch (actionError) {
        setConfirmation(null);
        setError(actionError.message || "The escrow action could not be completed.");
      }
    });
  };

  const escrowId = result?.escrowId ?? result?.escrowid;
  const sellerName = result?.sellerName || result?.sellername || "—";

  return (
    <div className="form-layout escrow-initiate-layout">
      <section className="surface-card form-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">New escrow · Step 1</p>
            <h2>Payment details</h2>
            <p>Identify the seller and item, then review the initiated payment before funding.</p>
          </div>
          <span className="section-icon"><Icon name="shield" size={21} /></span>
        </div>

        {error && (
          <Alert tone="error" title="Escrow action needs attention">
            <p>{error}</p>
          </Alert>
        )}

        <form onSubmit={submit} className="standard-form">
          <Input
            id="escrow-seller-account"
            label="Seller account number"
            placeholder="Example: ACC21"
            hint="The backend verifies that this account belongs to a seller."
            autoComplete="off"
            autoCapitalize="characters"
            spellCheck={false}
            value={sellerAccountNumber}
            onChange={(event) => setSellerAccountNumber(event.target.value.toUpperCase())}
            disabled={loading}
            required
          />
          <Input
            id="escrow-item-name"
            label="Item name"
            placeholder="What is being purchased?"
            value={itemName}
            onChange={(event) => setItemName(event.target.value)}
            disabled={loading}
            required
          />
          <Input
            id="escrow-payment-amount"
            label="Payment amount"
            type="number"
            min="0.01"
            step="0.01"
            inputMode="decimal"
            prefix="₹"
            placeholder="0.00"
            hint="Enter the exact payment amount in INR."
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            disabled={loading}
            required
          />
          <div className="form-actions">
            <Button
              type="submit"
              icon="shield"
              loading={pending === "initiate"}
              loadingLabel="Initiating payment..."
              disabled={loading}
            >
              Initiate escrow payment
            </Button>
          </div>
        </form>
      </section>

      <aside className="guidance-panel escrow-guidance">
        <p className="eyebrow">Protected by process</p>
        <h2>Review first. Fund second.</h2>
        <p>Initiation creates a reviewable request. It does not move funds.</p>
        <ol className="guidance-list">
          <li><span>01</span><div><strong>Initiate</strong><p>Seller, item, and amount are recorded.</p></div></li>
          <li><span>02</span><div><strong>Confirm</strong><p>Review the server-returned payment details.</p></div></li>
          <li><span>03</span><div><strong>Fund</strong><p>Only after confirmation can funds move into escrow.</p></div></li>
        </ol>
        <div className="guidance-note"><Icon name="lock" size={18} /><p>Your buyer identity continues to come from the authenticated session.</p></div>
      </aside>

      {result && (
        <section className="surface-card escrow-review-card form-layout-full">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Server-confirmed escrow · #{escrowId ?? "—"}</p>
              <h2>
                {result.status === "PAYMENT_INITIATED" ? "Review your payment" :
                  result.status === "CREATED" ? "Ready to fund" :
                    result.status === "FUNDED" ? "Funds are secured" : "Escrow update"}
              </h2>
              <p>Only actions available for the current server-returned status are shown.</p>
            </div>
            <StatusBadge status={result.status} />
          </div>

          <dl className="confirmation-details escrow-review-details">
            <div><dt>Seller</dt><dd>{sellerName}</dd></div>
            <div><dt>Item</dt><dd>{result.itemName || "—"}</dd></div>
            <div><dt>Amount</dt><dd>{formatMoney(result.amount)}</dd></div>
            <div><dt>Escrow ID</dt><dd className="mono-value">{escrowId ?? "—"}</dd></div>
          </dl>

          <EscrowLifecycle status={result.status} />

          {result.status === "PAYMENT_INITIATED" && (
            <div className="review-action-panel">
              <div><strong>Confirm the payment details</strong><p>Confirm to enable funding, or decline this initiated payment.</p></div>
              <div className="button-group">
                <Button variant="secondary" icon="close" onClick={() => setConfirmation("cancel")} disabled={loading}>Decline payment</Button>
                <Button
                  icon="check"
                  onClick={() => performAction("confirm")}
                  loading={pending === "escrow-confirm"}
                  loadingLabel="Confirming..."
                  disabled={loading}
                >
                  Confirm payment
                </Button>
              </div>
            </div>
          )}

          {result.status === "CREATED" && (
            <div className="review-action-panel">
              <div><strong>Payment confirmed</strong><p>The next action moves the stated amount into escrow.</p></div>
              <Button icon="wallet" onClick={() => setConfirmation("fund")} disabled={loading}>Fund escrow</Button>
            </div>
          )}

          {result.status === "FUNDED" && (
            <div className="review-action-panel">
              <div><strong>Escrow funded successfully</strong><p>Track shipment and delivery from your escrow workspace.</p></div>
              <Button variant="secondary" iconAfter="arrowRight" onClick={() => setPage("buyer-escrows")}>View my escrows</Button>
            </div>
          )}

          {["CANCELLED", "EXPIRED"].includes(result.status) && (
            <Alert tone="info" title={result.status === "CANCELLED" ? "Payment cancelled" : "Payment expired"}>
              <p>No further action is available for this initiated payment.</p>
            </Alert>
          )}
        </section>
      )}

      {confirmation === "fund" && result && (
        <ConfirmDialog
          title="Fund this escrow?"
          description={`Confirm that ${formatMoney(result.amount)} should be moved into escrow for ${result.itemName || "this item"}.`}
          confirmLabel="Fund escrow"
          cancelLabel="Review details"
          loading={pending === "escrow-fund"}
          loadingLabel="Funding escrow..."
          onConfirm={() => performAction("fund")}
          onCancel={() => setConfirmation(null)}
        />
      )}

      {confirmation === "cancel" && result && (
        <ConfirmDialog
          title="Decline this payment?"
          description="This cancels the initiated escrow payment. The action cannot be undone from this screen."
          confirmLabel="Decline payment"
          cancelLabel="Keep payment"
          confirmVariant="danger"
          tone="warning"
          loading={pending === "escrow-cancel"}
          loadingLabel="Declining payment..."
          onConfirm={() => performAction("cancel")}
          onCancel={() => setConfirmation(null)}
        />
      )}
    </div>
  );
}

export default EscrowInitiate;
