import React, { useEffect, useMemo, useState } from "react";
import Icon from "./Icon";
import {
  formatMoney,
  formatDate,
  readResponse,
} from "../utils/formatters";

const AdminEscrows = ({ token, setToast }) => {
  const [escrows, setEscrows] = useState([]);
  const [disputes, setDisputes] = useState({});
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState(null);
  // -----------------------------------------
  // LOAD DISPUTES
  // -----------------------------------------
  const loadDisputes = async () => {
    if (!token) return;

    setLoading(true);

    try {
      const response = await fetch("/api/escrow/admin", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data?.message || "Could not load admin disputes."
        );
      }

      const adminEscrows = Array.isArray(data) ? data : [];

      setEscrows(adminEscrows);
      setDisputes({});

      for (const escrow of adminEscrows) {
        try {
          const disputeResponse = await fetch(
            `/api/escrow/${escrow.id}/dispute`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (!disputeResponse.ok) continue;

          const disputeData = await readResponse(disputeResponse);

          if (disputeData) {
            setDisputes((prev) => ({
              ...prev,
              [escrow.id]: disputeData,
            }));
          }
        } catch (error) {
          console.error(
            `Could not load dispute for escrow ${escrow.id}`,
            error
          );
        }
      }
    } catch (error) {
      console.error("Failed to load admin disputes", error);

      setToast({
        type: "error",
        title: "Failed to load disputes",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    if (token) {
      loadDisputes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const resolveDispute = async (disputeId, resolution) => {
    setResolvingId(disputeId);

    try {
      const response = await fetch(
        `/api/escrow/${disputeId}/resolve`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ resolution }),
        }
      );

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data === "string"
            ? data
            : data?.message || "Could not resolve the dispute."
        );
      }

      setToast({
        type: "success",
        title:
          resolution === "RELEASE"
            ? "Funds released"
            : "Refund approved",
        message:
          resolution === "RELEASE"
            ? "The dispute was resolved in favor of the seller."
            : "The dispute was resolved in favor of the buyer.",
      });

      await loadDisputes();
    } catch (error) {
      setToast({
        type: "error",
        title: "Resolution failed",
        message: error.message || "Something went wrong.",
      });
    } finally {
      setResolvingId(null);
    }
  };

  // -----------------------------------------
  // SUMMARY
  // -----------------------------------------
  const summary = useMemo(
    () => ({
      total: escrows.length,

      underReview: escrows.filter(
        (item) => item.status === "UNDER_REVIEW"
      ).length,

      totalAmount: escrows.reduce(
        (sum, item) => sum + Number(item.amount || 0),
        0
      ),

      withSellerResponse: escrows.filter(
        (item) => disputes[item.id]?.sellerResponse
      ).length,
    }),
    [escrows, disputes]
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

          <p className="micro-label">ADMIN WORKSPACE</p>

          <h2>Loading dispute queue...</h2>

          <span>
            Fetching escrow disputes that require review.
          </span>
        </div>
      </section>
    );
  }

  return (
    <section className="seller-page">
      <div className="seller-dashboard-head">
        <div>
          <p className="micro-label">ADMIN WORKSPACE</p>

          <h2>Dispute resolution</h2>

          <p>
            Review buyer disputes, seller responses, and resolve protected
            escrow payments.
          </p>
        </div>

        <button
          className="seller-refresh"
          onClick={loadDisputes}
        >
          <Icon name="activity" size={17} />
          Refresh
        </button>
      </div>

      {/* ------------------------------------- */}
      {/* DISPUTE SUMMARY */}
      {/* ------------------------------------- */}
      <div className="seller-stats">
        <div className="seller-stat-card">
          <span>Disputes</span>
          <strong>{summary.total}</strong>
        </div>

        <div className="seller-stat-card">
          <span>Under review</span>
          <strong>{summary.underReview}</strong>
        </div>

        <div className="seller-stat-card">
          <span>Seller responded</span>
          <strong>{summary.withSellerResponse}</strong>
        </div>

        <div className="seller-stat-card">
          <span>Protected amount</span>
          <strong>{formatMoney(summary.totalAmount)}</strong>
        </div>
      </div>

      {/* ------------------------------------- */}
      {/* EMPTY STATE */}
      {/* ------------------------------------- */}
      {escrows.length === 0 ? (
        <div className="seller-empty">
          <div className="seller-empty-icon">
            <Icon name="check" size={24} />
          </div>

          <h3>No disputes require review</h3>

          <p>The dispute queue is currently clear.</p>
        </div>
      ) : (
        /* ------------------------------------- */
        /* DISPUTE LIST */
        /* ------------------------------------- */
        <div className="seller-order-list">
          {escrows.map((escrow) => {
            const dispute = disputes[escrow.id];

            const buyerName =
              escrow.buyer?.name ||
              escrow.buyerName ||
              escrow.buyer?.email ||
              "Unknown buyer";

            const buyerEmail = escrow.buyer?.email || "";

            const sellerName =
              escrow.seller?.name ||
              escrow.sellerName ||
              escrow.seller?.email ||
              "Unknown seller";

            const sellerEmail = escrow.seller?.email || "";

            const status = escrow.status || "UNKNOWN";

            const statusClass = status
              .toLowerCase()
              .replaceAll("_", "-");

            return (
              <article
                className="seller-order-card"
                key={escrow.id}
              >
                {/* TOP */}
                <div className="seller-order-top">
                  <div className="seller-order-title">
                    <div className="seller-order-icon">
                      <Icon name="shield" size={21} />
                    </div>

                    <div>
                      <p className="micro-label">
                        ESCROW #{escrow.id}
                      </p>

                      <h3>
                        {escrow.itemName || "Unnamed item"}
                      </h3>
                    </div>
                  </div>

                  <span
                    className={`seller-status seller-status-${statusClass}`}
                  >
                    <i />

                    {status.replaceAll("_", " ")}
                  </span>
                </div>

                {/* ESCROW DETAILS */}
                <div className="seller-order-details">
                  <div>
                    <span>BUYER</span>

                    <strong>{buyerName}</strong>

                    {buyerEmail && (
                      <small>{buyerEmail}</small>
                    )}
                  </div>

                  <div>
                    <span>SELLER</span>

                    <strong>{sellerName}</strong>

                    {sellerEmail && (
                      <small>{sellerEmail}</small>
                    )}
                  </div>

                  <div>
                    <span>AMOUNT</span>

                    <strong>
                      {formatMoney(escrow.amount)}
                    </strong>

                    <small>Protected escrow</small>
                  </div>
                </div>

                {/* TIMELINE */}
                <div className="seller-order-details">
                  <div>
                    <span>CREATED</span>

                    <strong>
                      {formatDate(escrow.createdAt)}
                    </strong>
                  </div>

                  {escrow.shippedAt && (
                    <div>
                      <span>SHIPPED</span>

                      <strong>
                        {formatDate(escrow.shippedAt)}
                      </strong>
                    </div>
                  )}

                  <div>
                    <span>TRANSACTION</span>

                    <strong>#{escrow.id}</strong>
                  </div>
                </div>

                {/* DISPUTE */}
                {dispute && (
                  <div className="seller-dispute-panel">
                    {/* DISPUTE HEADER */}
                    <div className="seller-dispute-header">
                      <div className="seller-dispute-icon">
                        <Icon name="shield" size={19} />
                      </div>

                      <div>
                        <strong>Dispute raised</strong>

                        <span>
                          Buyer has requested administrative review.
                        </span>
                      </div>
                    </div>

                    {/* DISPUTE DETAILS */}
                    <div className="seller-dispute-details">
                      <div>
                        <span>REASON</span>

                        <strong>
                          {dispute.reason?.replaceAll("_", " ") ||
                            "Not specified"}
                        </strong>
                      </div>

                      <div>
                        <span>BUYER DESCRIPTION</span>

                        <strong>
                          {dispute.description ||
                            "No description provided."}
                        </strong>
                      </div>

                      <div>
                        <span>SELLER RESPONSE</span>

                        <div className="seller-dispute-response">
                          {dispute.sellerResponse ? (
                            <>
                              <strong>Seller response</strong>

                              <span>
                                {dispute.sellerResponse}
                              </span>
                            </>
                          ) : (
                            <span>
                              No response from the seller yet.
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* ADMIN DECISION */}
                    <div className="seller-order-action">
                      <div>
                        <strong>Resolve this dispute</strong>

                        <span>
                          Choose whether the protected funds should go to
                          the seller or return to the buyer.
                        </span>
                      </div>

                      <div
                        style={{
                          display: "flex",
                          gap: 10,
                          flexWrap: "wrap",
                        }}
                      >
                        <button
                          className="seller-ship-button"
                          onClick={() =>
                            resolveDispute(dispute.id, "RELEASE")
                          }
                          disabled={resolvingId === dispute.id}
                        >
                          <Icon name="check" size={17} />

                          {resolvingId === dispute.id
                            ? "Resolving..."
                            : "Release Funds"}
                        </button>

                        <button
                          className="seller-ship-button"
                          onClick={() =>
                            resolveDispute(dispute.id, "REFUND")
                          }
                          disabled={resolvingId === dispute.id}
                        >
                          <Icon name="shield" size={17} />

                          {resolvingId === dispute.id
                            ? "Resolving..."
                            : "Refund Buyer"}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
};

export default AdminEscrows;
