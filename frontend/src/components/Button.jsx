import Icon from "./Icon";
import { Spinner } from "./LoadingSpinner";

function Button({
  children,
  variant = "primary",
  size = "medium",
  loading = false,
  loadingLabel,
  icon,
  iconAfter,
  className = "",
  disabled,
  type = "button",
  ...props
}) {
  return (
    <button
      type={type}
      className={`button button-${variant} button-${size} ${className}`.trim()}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? (
        <Spinner size={16} />
      ) : (
        icon && <Icon name={icon} size={size === "small" ? 15 : 17} />
      )}

      <span>{loading ? loadingLabel || children : children}</span>

      {!loading && iconAfter && (
        <Icon name={iconAfter} size={size === "small" ? 15 : 17} />
      )}
    </button>
  );
}

export default Button;
