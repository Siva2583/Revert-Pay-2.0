import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import Icon from "./Icon";
import Button from "./Button";

const focusableSelector = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

export default function Modal({
  title,
  eyebrow,
  children,
  onClose,
  busy = false,
  size = "medium",
  className = "",
}) {
  const titleId = useId();
  const panelRef = useRef(null);
  const closeRef = useRef(onClose);
  const busyRef = useRef(busy);

  useEffect(() => {
    closeRef.current = onClose;
  }, [onClose]);

  useEffect(() => {
    busyRef.current = busy;
  }, [busy]);

  useEffect(() => {
    const previousFocus = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const panel = panelRef.current;
    const focusable = panel?.querySelectorAll(focusableSelector);
    focusable?.[0]?.focus();

    const handleKeyDown = (event) => {
      if (event.key === "Escape" && !busyRef.current) {
        event.preventDefault();
        closeRef.current();
        return;
      }

      if (event.key !== "Tab" || !panel) return;

      const elements = Array.from(
        panel.querySelectorAll(focusableSelector)
      ).filter((element) => element.getClientRects().length > 0);

      if (!elements.length) {
        event.preventDefault();
        panel.focus();
        return;
      }

      const first = elements[0];
      const last = elements[elements.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
      previousFocus?.focus?.();
    };
  }, []);

  return createPortal(
    <div
      className="modal-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !busy) {
          onClose();
        }
      }}
    >
      <section
        ref={panelRef}
        className={`modal-panel modal-${size} ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
      >
        <header className="modal-header">
          <div>
            {eyebrow && <p className="eyebrow">{eyebrow}</p>}
            <h2 id={titleId}>{title}</h2>
          </div>
          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            disabled={busy}
            aria-label="Close dialog"
          >
            <Icon name="close" size={20} />
          </button>
        </header>
        <div className="modal-body">{children}</div>
      </section>
    </div>,
    document.body
  );
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel,
  cancelLabel = "Keep reviewing",
  confirmVariant = "primary",
  loading = false,
  loadingLabel = "Processing...",
  onConfirm,
  onCancel,
  tone = "default",
}) {
  return (
    <Modal
      title={title}
      eyebrow="Confirm action"
      onClose={onCancel}
      busy={loading}
      size="small"
      className={`confirm-dialog confirm-${tone}`}
    >
      <div className="confirm-dialog-content">
        <div className="confirm-dialog-icon">
          <Icon name={tone === "warning" ? "alert" : "shield"} size={23} />
        </div>
        <p>{description}</p>
      </div>
      <div className="modal-actions">
        <Button variant="secondary" onClick={onCancel} disabled={loading}>
          {cancelLabel}
        </Button>
        <Button
          variant={confirmVariant}
          onClick={onConfirm}
          loading={loading}
          loadingLabel={loadingLabel}
        >
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  );
}
