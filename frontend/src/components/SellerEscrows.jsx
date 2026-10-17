import { useEffect, useMemo, useState } from "react";
import API from "../services/api";
import Icon from "./Icon";
import {
  formatMoney,
  formatDate,
  readResponse,
} from "../utils/formatters";

function SellerEscrows({ token, setToast }) {
  const [escrows, setEscrows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [shippingId, setShippingId] = useState(null);

  const [disputes, setDisputes] = useState({});
  const [disputeLoadingId, setDisputeLoadingId] = useState(null);
  const [responseText, setResponseText] = useState({});
  const [respondingId, setRespondingId] = useState(null);

  const loadEscrows = async () => {
    setLoading(true);

    try {
      const response = await fetch(API.sellerEscrows, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data.message || "Could not load seller escrows."
        );
      }

      const sellerEscrows = Array.isArray(data) ? data : [];

      setEscrows(sellerEscrows);

      // Load disputes for UNDER_REVIEW escrows
      const underReview = sellerEscrows.filter(
        (item) => item.status === "UNDER_REVIEW"
      );

      for (const escrow of underReview) {
        const escrowId = escrow.id ?? escrow.escrowid;

        try {
          setDisputeLoadingId(escrowId);

          const disputeResponse = await fetch(
            `/api/escrow/${escrowId}/dispute`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          const disputeData = await readResponse(disputeResponse);

          if (disputeResponse.ok && disputeData) {
            setDisputes((prev) => ({
              ...prev,
              [escrowId]: disputeData,
            }));

            if (disputeData.sellerResponse) {
              setResponseText((prev) => ({
                ...prev,
                [escrowId]: disputeData.sellerResponse,
              }));
            }
          }
        } catch (error) {
          console.error(
            `Could not load dispute for escrow ${escrowId}`,
            error
          );
        } finally {
          setDisputeLoadingId(null);
        }
      }
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

  const shipEscrow = async (id) => {
    setShippingId(id);

    try {
      const response = await fetch(`/api/escrow/${id}/ship`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data.message || "Could not ship this escrow."
        );
      }

      setToast({
        type: "success",
        title: "Item marked as shipped",
        message: "The escrow has moved to SHIPPED.",
      });

      await loadEscrows();
    } catch (error) {
      setToast({
        type: "error",
        title: "Shipping failed",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setShippingId(null);
    }
  };

  const respondToDispute = async (escrowId) => {
    const dispute = disputes[escrowId];

    if (!dispute) {
      setToast({
        type: "error",
        title: "Dispute unavailable",
        message: "Could not find the dispute for this escrow.",
      });
      return;
    }

    const response = responseText[escrowId]?.trim();

    if (!response) {
      setToast({
        type: "error",
        title: "Response required",
        message: "Please enter a response before submitting.",
      });
      return;
    }

    setRespondingId(escrowId);

    try {
      const result = await fetch(
        `/api/escrow/${dispute.id}/respond`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            response,
          }),
        }
      );

      const data = await readResponse(result);

      if (!result.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data.message || "Could not submit your response."
        );
      }

      setToast({
        type: "success",
        title: "Response submitted",
        message:
          "Your dispute response has been recorded for admin review.",
      });

      await loadEscrows();
    } catch (error) {
      setToast({
        type: "error",
        title: "Response failed",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setRespondingId(null);
    }
  };

  const summary = useMemo(
    () => ({
      total: escrows.length,
      ready: escrows.filter(
        (item) => item.status === "FUNDED"
      ).length,
      shipped: escrows.filter(
        (item) => item.status === "SHIPPED"
      ).length,
      closed: escrows.filter((item) =>
        [
          "EXPIRED",
          "CANCELLED",
          "RELEASED",
          "REFUNDED",
        ].includes(item.status)
      ).length,
    }),
    [escrows]
  );

  if (loading) {
    return (
      <section className="seller-page">
        <div className="seller-loading">
          <div className="seller-loading-mark">
            <Icon name="package" size={24} />
          </div>

          <p className="micro-label">
            SELLER WORKSPACE
          </p>

          <h2>Loading your escrow orders...</h2>

          <span>
            Fetching transactions assigned to your account.
          </span>
        </div>
      </section>
    );
  }

  return (
    <section className="seller-page">
      <div className="seller-dashboard-head">
        <div>
          <p className="micro-label">
            SELLER WORKSPACE
          </p>

          <h2>Incoming escrow orders</h2>

          <p>
            Review funded payments, ship orders,
            and track release timing.
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

      <div className="seller-stats">
        <div className="seller-stat-card">
          <span>Total escrows</span>
          <strong>{summary.total}</strong>
          <small>
            All transactions assigned to you
          </small>
        </div>

        <div className="seller-stat-card seller-stat-action">
          <span>Ready to ship</span>
          <strong>{summary.ready}</strong>
          <small>
            Funded orders awaiting shipment
          </small>
        </div>

        <div className="seller-stat-card">
          <span>Shipped</span>
          <strong>{summary.shipped}</strong>
          <small>
            Orders already marked shipped
          </small>
        </div>

        <div className="seller-stat-card">
          <span>Closed</span>
          <strong>{summary.closed}</strong>
          <small>
            Completed or terminal transactions
          </small>
        </div>
      </div>

      {escrows.length === 0 ? (
        <div className="seller-empty">
          <div className="seller-empty-icon">
            <Icon name="package" size={30} />
          </div>

          <p className="micro-label">
            NO ORDERS YET
          </p>

          <h3>No incoming payments</h3>

          <p>
            When a buyer funds an escrow for one
            of your transactions, it will appear here.
          </p>
        </div>
      ) : (
        <div className="seller-order-list">
          {escrows.map((escrow) => {
            const escrowId =
              escrow.id ?? escrow.escrowid;

            const buyerName =
              escrow.buyer?.name ||
              escrow.buyerName ||
              escrow.buyer?.email ||
              "Unknown buyer";

            const buyerEmail =
              escrow.buyer?.email || "";

            const status =
              escrow.status || "UNKNOWN";

            const statusClass = status
              .toLowerCase()
              .replaceAll("_", "-");

            const dispute = disputes[escrowId];

            return (
              <article
                className="seller-order-card"
                key={escrowId}
              >
                <div className="seller-order-top">
                  <div className="seller-order-title">
                    <div className="seller-order-icon">
                      <Icon
                        name="package"
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

                <div className="seller-order-details">
                  <div>
                    <span>BUYER</span>
                    <strong>{buyerName}</strong>

                    {buyerEmail && (
                      <small>
                        {buyerEmail}
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
                      Escrowed payment
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

                {status === "FUNDED" && (
                  <div className="seller-order-action">
                    <div>
                      <strong>
                        Payment is funded and ready.
                      </strong>

                      <span>
                        Ship the item to start
                        the auto-release window.
                      </span>
                    </div>

                    <button
                      className="seller-ship-button"
                      onClick={() =>
                        shipEscrow(escrowId)
                      }
                      disabled={
                        shippingId === escrowId
                      }
                    >
                      <Icon
                        name="package"
                        size={17}
                      />

                      {shippingId === escrowId
                        ? "Marking shipped..."
                        : "Ship item"}
                    </button>
                  </div>
                )}

                {status === "SHIPPED" && (
                  <div className="seller-shipment-panel">
                    <div className="seller-shipment-icon">
                      <Icon
                        name="shield"
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
                )}

                {status === "UNDER_REVIEW" && (
                  <div className="seller-dispute-panel">
                    <div className="seller-dispute-header">
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
                          The buyer has raised a dispute
                          against this transaction.
                        </span>
                      </div>
                    </div>

                    {disputeLoadingId === escrowId &&
                      !dispute && (
                        <div className="seller-dispute-loading">
                          Loading dispute details...
                        </div>
                      )}

                    {dispute && (
                      <>
                        <div className="seller-dispute-details">
                          <div>
                            <span>
                              REASON
                            </span>

                            <strong>
                              {dispute.reason
                                ?.replaceAll(
                                  "_",
                                  " "
                                )}
                            </strong>
                          </div>

                          <div>
                            <span>
                              BUYER DESCRIPTION
                            </span>

                            <p className="seller-dispute-description">
                              {dispute.description}
                            </p>
                          </div>
                        </div>

                        {dispute.status ===
                        "RESPONDED" ? (
                          <div className="seller-dispute-response">
                            <span>
                              YOUR RESPONSE
                            </span>

                            <p>
                              {dispute.sellerResponse}
                            </p>

                            <small>
                              Waiting for admin resolution.
                            </small>
                          </div>
                        ) : (
                          <div className="seller-dispute-response-form">
                            <label>
                              YOUR RESPONSE
                            </label>

                            <textarea
                              value={
                                responseText[
                                  escrowId
                                ] || ""
                              }
                              onChange={(event) =>
                                setResponseText(
                                  (prev) => ({
                                    ...prev,
                                    [escrowId]:
                                      event.target.value,
                                  })
                                )
                              }
                              placeholder="Explain your side of the dispute..."
                              rows={4}
                            />

                            <button
                              className="seller-ship-button"
                              onClick={() =>
                                respondToDispute(
                                  escrowId
                                )
                              }
                              disabled={
                                respondingId ===
                                escrowId
                              }
                            >
                              {respondingId ===
                              escrowId
                                ? "Submitting..."
                                : "Submit response"}
                            </button>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                {![
                  "FUNDED",
                  "SHIPPED",
                  "UNDER_REVIEW",
                ].includes(status) && (
                  <div className="seller-order-footer">
                    <span>
                      {status === "EXPIRED"
                        ? "This confirmation window expired."
                        : status === "CANCELLED"
                        ? "This payment was cancelled."
                        : status === "RELEASED"
                        ? "Funds have been released."
                        : status === "REFUNDED"
                        ? "Funds have been refunded."
                        : "No seller action is available for this status."}
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

export default SellerEscrows;