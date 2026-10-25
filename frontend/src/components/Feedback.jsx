import Icon from "./Icon";
import Button from "./Button";
import { formatStatus } from "../utils/formatters";

const toneIcons = {
  success: "checkCircle",
  error: "alertCircle",
  warning: "alert",
  info: "info",
  neutral: "info",
};

export function Alert({
  tone = "info",
  title,
  children,
  action,
  className = "",
  role,
}) {
  return (
    <div
      className={`alert alert-${tone} ${className}`.trim()}
      role={role || (tone === "error" ? "alert" : "status")}
    >
      <Icon name={toneIcons[tone] || "info"} size={19} />
      <div className="alert-content">
        {title && <strong>{title}</strong>}
        {children && <div className="alert-description">{children}</div>}
      </div>
      {action && <div className="alert-action">{action}</div>}
    </div>
  );
}

export function EmptyState({
  icon = "inbox",
  title,
  description,
  action,
  compact = false,
}) {
  return (
    <div className={`empty-state ${compact ? "empty-state-compact" : ""}`}>
      <div className="empty-state-icon">
        <Icon name={icon} size={compact ? 21 : 26} />
      </div>
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {action && <div className="empty-state-action">{action}</div>}
    </div>
  );
}

export function ErrorState({
  title = "We couldn’t load this information",
  description,
  onRetry,
  retrying = false,
}) {
  return (
    <div className="error-state" role="alert">
      <div className="empty-state-icon error-state-icon">
        <Icon name="alertCircle" size={25} />
      </div>
      <h2>{title}</h2>
      <p>{description || "Check your connection and try again."}</p>
      {onRetry && (
        <Button
          variant="secondary"
          icon="refresh"
          loading={retrying}
          loadingLabel="Retrying..."
          onClick={onRetry}
        >
          Try again
        </Button>
      )}
    </div>
  );
}

const statusTones = {
  PAYMENT_INITIATED: "info",
  CREATED: "info",
  FUNDED: "success",
  SHIPPED: "info",
  UNDER_REVIEW: "warning",
  RELEASED: "success",
  REFUNDED: "neutral",
  CANCELLED: "neutral",
  EXPIRED: "neutral",
  OPENED: "warning",
  RESPONDED: "info",
  RESOLVED: "success",
};

export function StatusBadge({ status, className = "" }) {
  const normalized = String(status || "UNKNOWN").toUpperCase();
  const tone = statusTones[normalized] || "neutral";

  return (
    <span className={`status-badge status-${tone} ${className}`.trim()}>
      <span className="status-dot" aria-hidden="true" />
      {formatStatus(normalized)}
    </span>
  );
}

export function RefreshButton({ refreshing, onClick, label = "Refresh" }) {
  return (
    <Button
      variant="secondary"
      size="small"
      icon="refresh"
      loading={refreshing}
      loadingLabel="Refreshing..."
      onClick={onClick}
    >
      {label}
    </Button>
  );
}
