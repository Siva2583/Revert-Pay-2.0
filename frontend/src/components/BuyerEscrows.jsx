import { useEffect, useMemo, useState } from "react";
import API from "../services/api";
import Icon from "./Icon";
import {
  formatMoney,
  formatDate,
  readResponse,
} from "../utils/formatters";

function BuyerEscrows({ token, setToast }) {
  const [escrows, setEscrows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirmingId, setConfirmingId] = useState(null);

  // Dispute state
  const [disputeId, setDisputeId] = useState(null);
  const [disputeReason, setDisputeReason] =
    useState("ITEM_NOT_RECEIVED");
  const [disputeDescription, setDisputeDescription] =
    useState("");
  const [disputingId, setDisputingId] = useState(null);

  const loadEscrows = async () => {
    setLoading(true);

    try {
      const response = await fetch(API.buyerEscrows, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data.message || "Could not load buyer escrows."
        );
      }

      setEscrows(Array.isArray(data) ? data : []);
    } catch (error) {
      setToast({
        type: "error",
        title: "Could not load escrows",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadEscrows();
    }
  }, [token]);

  // -----------------------------------------
  // CONFIRM DELIVERY
  // -----------------------------------------
  const confirmDelivery = async (id) => {
    setConfirmingId(id);

    try {
      const response = await fetch(
        `/api/escrow/${id}/confirm-delivery`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data.message || "Could not confirm delivery."
        );
      }

      setToast({
        type: "success",
        title: "Delivery confirmed",
        message: "Payment has been released to the seller.",
      });

      await loadEscrows();
    } catch (error) {
      setToast({
        type: "error",
        title: "Confirmation failed",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setConfirmingId(null);
    }
  };

  // -----------------------------------------
  // RAISE DISPUTE
  // -----------------------------------------
  const raiseDispute = async (id) => {
    if (!disputeDescription.trim()) {
      setToast({
        type: "error",
        title: "Description required",
        message:
          "Please describe the issue before submitting the dispute.",
      });
      return;
    }

    setDisputingId(id);

    try {
      const response = await fetch(API.raiseDispute(id), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          reason: disputeReason,
          description: disputeDescription.trim(),
        }),
      });

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data.message || "Could not raise the dispute."
        );
      }

      setToast({
        type: "success",
        title: "Dispute raised",
        message: "The escrow has been moved to review.",
      });

      setDisputeId(null);
      setDisputeReason("ITEM_NOT_RECEIVED");
      setDisputeDescription("");

      await loadEscrows();
    } catch (error) {
      setToast({
        type: "error",
        title: "Dispute failed",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setDisputingId(null);
    }
  };

  // -----------------------------------------
  // SUMMARY
  // -----------------------------------------
  const summary = useMemo(
    () => ({
      total: escrows.length,

      shipped: escrows.filter(
        (item) => item.status === "SHIPPED"
      ).length,

      released: escrows.filter(
        (item) => item.status === "RELEASED"
      ).length,

      active: escrows.filter((item) =>
        [
          "CREATED",
          "FUNDED",
          "SHIPPED",
          "UNDER_REVIEW",
        ].includes(item.status)
      ).length,
    }),
    [escrows]
  );

  // -----------------------------------------
  // LOADING
  // -----------------------------------------
  if (loading) {
    return (
      <section className="seller-page">
        <div className="seller-loading">
          <div className="seller-loading-mark">
            <Icon name="shield" size={24} />
          </div>

          <p className="micro-label">
            BUYER WORKSPACE
          </p>

          <h2>Loading your escrow orders...</h2>

          <span>
            Fetching purchases linked to your account.
          </span>
        </div>
      </section>
    );
  }

  // -----------------------------------------
  // PAGE
  // -----------------------------------------
  return (
    <section className="seller-page">

      {/* PAGE HEADER */}
      <div className="seller-dashboard-head">
        <div>
          <p className="micro-label">
            BUYER WORKSPACE
          </p>

          <h2>My escrow orders</h2>

          <p>
            Track your purchases, delivery status,
            and protected payments.
          </p>
        </div>

        <button
          className="seller-refresh"
          onClick={loadEscrows}
        >
          <Icon name="activity" size={17} />
          Refresh
        </button>
      </div>

      {/* SUMMARY */}
      <div className="seller-stats">

        <div className="seller-stat-card">
          <span>Total orders</span>
          <strong>{summary.total}</strong>
        </div>

        <div className="seller-stat-card">
          <span>Awaiting delivery</span>
          <strong>{summary.shipped}</strong>
        </div>

        <div className="seller-stat-card">
          <span>Released</span>
          <strong>{summary.released}</strong>
        </div>

        <div className="seller-stat-card">
          <span>Active</span>
          <strong>{summary.active}</strong>
        </div>

      </div>

      {/* EMPTY STATE */}
      {escrows.length === 0 ? (
        <div className="seller-empty">

          <div className="seller-empty-icon">
            <Icon name="shield" size={24} />
          </div>

          <h3>No escrow orders yet</h3>

          <p>
            Your purchases will appear here once you
            initiate an escrow payment.
          </p>

        </div>
      ) : (

        /* ORDER LIST */
        <div className="seller-order-list">

          {escrows.map((escrow) => {

            const escrowId =
              escrow.id ?? escrow.escrowid;

            const sellerName =
              escrow.seller?.name ||
              escrow.sellerName ||
              escrow.seller?.email ||
              "Unknown seller";

            const sellerEmail =
              escrow.seller?.email || "";

            const status =
              escrow.status || "UNKNOWN";

            const statusClass = status
              .toLowerCase()
              .replaceAll("_", "-");

            return (
              <article
                className="seller-order-card"
                key={escrowId}
              >

                {/* -------------------------------- */}
                {/* TOP — SAME STRUCTURE AS SELLER */}
                {/* -------------------------------- */}

                <div className="seller-order-top">

                  <div className="seller-order-title">

                    <div className="seller-order-icon">
                      <Icon
                        name="shield"
                        size={21}
                      />
                    </div>

                    <div>

                      <p className="micro-label">
                        ESCROW #{escrowId}
                      </p>

                      <h3>
                        {escrow.itemName ||
                          "Unnamed item"}
                      </h3>

                    </div>

                  </div>

                  <span
                    className={`seller-status seller-status-${statusClass}`}
                  >
                    <i />
                    {status.replaceAll(
                      "_",
                      " "
                    )}
                  </span>

                </div>

                {/* -------------------------------- */}
                {/* DETAILS — SAME AS SELLER */}
                {/* -------------------------------- */}

                <div className="seller-order-details">

                  <div>

                    <span>SELLER</span>

                    <strong>
                      {sellerName}
                    </strong>

                    {sellerEmail && (
                      <small>
                        {sellerEmail}
                      </small>
                    )}

                  </div>

                  <div>

                    <span>AMOUNT</span>

                    <strong>
                      {formatMoney(
                        escrow.amount
                      )}
                    </strong>

                    <small>
                      Protected escrow
                    </small>

                  </div>

                  <div>

                    <span>TRANSACTION</span>

                    <strong>
                      #{escrowId}
                    </strong>

                    <small>
                      Protected escrow
                    </small>

                  </div>

                </div>

                {/* -------------------------------- */}
                {/* SHIPPED */}
                {/* -------------------------------- */}

                {status === "SHIPPED" && (
                  <>

                    <div className="seller-shipment-panel">

                      <div className="seller-shipment-icon">
                        <Icon
                          name="package"
                          size={19}
                        />
                      </div>

                      <div>

                        <strong>
                          Shipment recorded
                        </strong>

                        <span>
                          Shipped{" "}
                          {formatDate(
                            escrow.shippedAt
                          )}
                        </span>

                      </div>

                      <div className="seller-release-time">

                        <span>
                          AUTO RELEASE
                        </span>

                        <strong>
                          {formatDate(
                            escrow.autoReleaseAt
                          )}
                        </strong>

                      </div>

                    </div>

                    {/* BUYER ACTIONS */}

                    <div className="seller-order-action">

                      <div>

                        <strong>
                          Order delivered?
                        </strong>

                        <span>
                          Confirm delivery to release
                          the payment to the seller,
                          or raise a dispute.
                        </span>

                      </div>

                      <div
                        style={{
                          display: "flex",
                          gap: "10px",
                          alignItems: "center",
                          flexWrap: "wrap",
                        }}
                      >

                        <button
                          className="seller-ship-button"
                          onClick={() =>
                            setDisputeId(
                              disputeId === escrowId
                                ? null
                                : escrowId
                            )
                          }
                          disabled={
                            confirmingId === escrowId ||
                            disputingId === escrowId
                          }
                        >
                          <Icon
                            name="shield"
                            size={17}
                          />

                          Raise Dispute
                        </button>

                        <button
                          className="seller-ship-button"
                          onClick={() =>
                            confirmDelivery(
                              escrowId
                            )
                          }
                          disabled={
                            confirmingId === escrowId ||
                            disputingId === escrowId
                          }
                        >
                          <Icon
                            name="check"
                            size={17}
                          />

                          {confirmingId === escrowId
                            ? "Confirming..."
                            : "Confirm Delivery"}
                        </button>

                      </div>

                    </div>

                    {/* DISPUTE FORM */}

                    {disputeId === escrowId && (
                      <div className="seller-dispute-panel">

                        <div className="seller-dispute-header">

                          <div className="seller-dispute-icon">
                            <Icon
                              name="shield"
                              size={19}
                            />
                          </div>

                          <div>
                            <strong>
                              Raise a dispute
                            </strong>

                            <span>
                              Tell us what went wrong
                              with this order.
                            </span>
                          </div>

                        </div>

                        <div className="seller-dispute-details">

                          <div>

                            <span>
                              REASON
                            </span>

                            <select
                              value={disputeReason}
                              onChange={(event) =>
                                setDisputeReason(
                                  event.target.value
                                )
                              }
                              style={{
                                width: "100%",
                                marginTop: "7px",
                                padding: "10px",
                                borderRadius: "8px",
                                border:
                                  "1px solid #deded8",
                                background: "#fff",
                              }}
                            >

                              <option value="ITEM_NOT_RECEIVED">
                                Item not received
                              </option>

                              <option value="ITEM_NOT_AS_DESCRIBED">
                                Item not as described
                              </option>

                              <option value="DAMAGED_ITEM">
                                Damaged item
                              </option>

                              <option value="WRONG_ITEM">
                                Wrong item
                              </option>

                              <option value="COUNTERFEIT_ITEM">
                                Counterfeit item
                              </option>

                              <option value="SELLER_ISSUE">
                                Seller issue
                              </option>

                              <option value="OTHER">
                                Other
                              </option>

                            </select>

                          </div>

                          <div>

                            <span>
                              DESCRIPTION
                            </span>

                            <textarea
                              value={
                                disputeDescription
                              }
                              onChange={(event) =>
                                setDisputeDescription(
                                  event.target.value
                                )
                              }
                              placeholder="Describe the issue..."
                              rows={4}
                              style={{
                                width: "100%",
                                marginTop: "7px",
                                padding: "10px",
                                borderRadius: "8px",
                                border:
                                  "1px solid #deded8",
                                resize: "vertical",
                                boxSizing:
                                  "border-box",
                                font: "inherit",
                              }}
                            />

                          </div>

                        </div>

                        <div className="seller-dispute-response-form">

                          <button
                            className="seller-ship-button"
                            onClick={() =>
                              setDisputeId(null)
                            }
                            disabled={
                              disputingId === escrowId
                            }
                          >
                            Cancel
                          </button>

                          <button
                            className="seller-ship-button"
                            onClick={() =>
                              raiseDispute(
                                escrowId
                              )
                            }
                            disabled={
                              disputingId === escrowId
                            }
                          >
                            {disputingId === escrowId
                              ? "Submitting..."
                              : "Submit Dispute"}
                          </button>

                        </div>

                      </div>
                    )}

                  </>
                )}

                {/* -------------------------------- */}
                {/* FUNDED */}
                {/* -------------------------------- */}

                {status === "FUNDED" && (
                  <div className="seller-shipment-panel">

                    <div className="seller-shipment-icon">
                      <Icon
                        name="shield"
                        size={19}
                      />
                    </div>

                    <div>

                      <strong>
                        Payment secured
                      </strong>

                      <span>
                        Your payment is held safely
                        until the seller ships the item.
                      </span>

                    </div>

                  </div>
                )}

                {/* -------------------------------- */}
                {/* UNDER REVIEW */}
                {/* -------------------------------- */}

                {status === "UNDER_REVIEW" && (
                  <div className="seller-shipment-panel">

                    <div className="seller-shipment-icon">
                      <Icon
                        name="shield"
                        size={19}
                      />
                    </div>

                    <div>

                      <strong>
                        Dispute under review
                      </strong>

                      <span>
                        This escrow is currently being
                        reviewed.
                      </span>

                    </div>

                  </div>
                )}

                {/* -------------------------------- */}
                {/* RELEASED */}
                {/* -------------------------------- */}

                {status === "RELEASED" && (
                  <div className="seller-shipment-panel">

                    <div className="seller-shipment-icon">
                      <Icon
                        name="check"
                        size={19}
                      />
                    </div>

                    <div>

                      <strong>
                        Payment released
                      </strong>

                      <span>
                        Delivery was confirmed and
                        the seller has received the
                        escrow funds.
                      </span>

                    </div>

                  </div>
                )}

                {/* -------------------------------- */}
                {/* TERMINAL STATES */}
                {/* -------------------------------- */}

                {[
                  "EXPIRED",
                  "CANCELLED",
                  "REFUNDED",
                ].includes(status) && (
                  <div className="seller-order-footer">

                    <span>
                      {status === "EXPIRED"
                        ? "This confirmation window expired."
                        : status === "CANCELLED"
                        ? "This payment was cancelled."
                        : "Funds have been refunded."}
                    </span>

                    <strong>
                      {status.replaceAll(
                        "_",
                        " "
                      )}
                    </strong>

                  </div>
                )}

              </article>
            );
          })}

        </div>
      )}

    </section>
  );
}

export default BuyerEscrows;