import Icon from "./Icon";

const toastIcons = {
  success: "checkCircle",
  error: "alertCircle",
  warning: "alert",
  info: "info",
};

function Toast({ toast, closeToast }) {
  if (!toast) return null;

  const type = toast.type || "info";

  return (
    <div
      className={`toast toast-${type}`}
      role={type === "error" ? "alert" : "status"}
      aria-live={type === "error" ? "assertive" : "polite"}
    >
      <div className="toast-mark">
        <Icon name={toastIcons[type] || "info"} size={20} />
      </div>
      <div className="toast-content">
        {toast.title && <strong>{toast.title}</strong>}
        {toast.message && <p>{toast.message}</p>}
      </div>
      <button
        type="button"
        className="toast-close"
        onClick={closeToast}
        aria-label="Dismiss notification"
      >
        <Icon name="close" size={17} />
      </button>
    </div>
  );
}

export default Toast;
