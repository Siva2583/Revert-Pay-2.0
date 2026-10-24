import Icon from "./Icon";
import { formatStatus } from "../utils/formatters";

const standardSteps = [
  "PAYMENT_INITIATED",
  "CREATED",
  "FUNDED",
  "SHIPPED",
  "RELEASED",
];

const labels = {
  PAYMENT_INITIATED: "Initiated",
  CREATED: "Confirmed",
  FUNDED: "Funded",
  SHIPPED: "Shipped",
  UNDER_REVIEW: "Under review",
  RELEASED: "Released",
};

export default function EscrowLifecycle({ status }) {
  const isReview = status === "UNDER_REVIEW";
  const steps = isReview ? ["FUNDED", "SHIPPED", "UNDER_REVIEW"] : standardSteps;
  const currentIndex = steps.indexOf(status);

  // Terminal states can have more than one legitimate history. The detailed
  // audit timeline, rather than an inferred path, is the source for those.
  if (currentIndex < 0 || ["RELEASED", "REFUNDED", "CANCELLED", "EXPIRED"].includes(status)) {
    return null;
  }

  return (
    <ol className="escrow-lifecycle" aria-label="Escrow lifecycle">
      {steps.map((step, index) => {
        const complete = index < currentIndex;
        const current = index === currentIndex;

        return (
          <li
            key={step}
            className={`${complete ? "complete" : ""} ${current ? "current" : ""}`.trim()}
            aria-current={current ? "step" : undefined}
          >
            <span className="lifecycle-marker" aria-hidden="true">
              {complete ? <Icon name="check" size={12} /> : index + 1}
            </span>
            <span className="lifecycle-label">{labels[step] || formatStatus(step)}</span>
          </li>
        );
      })}
    </ol>
  );
}
