import { useId, useState } from "react";
import Icon from "./Icon";

export function FormField({
  id,
  label,
  hint,
  error,
  required = false,
  children,
  className = "",
}) {
  const hintId = id ? `${id}-hint` : undefined;
  const errorId = id ? `${id}-error` : undefined;

  return (
    <div className={`form-field ${error ? "has-error" : ""} ${className}`.trim()}>
      <label htmlFor={id}>
        {label}
        {required && <span className="required-mark" aria-hidden="true"> *</span>}
      </label>

      {children}

      {error ? (
        <p className="field-message field-error" id={errorId} role="alert">
          <Icon name="alert" size={14} />
          {error}
        </p>
      ) : hint ? (
        <p className="field-message" id={hintId}>{hint}</p>
      ) : null}
    </div>
  );
}

export function Input({
  id: providedId,
  label,
  hint,
  error,
  required,
  prefix,
  className = "",
  ...props
}) {
  const generatedId = useId();
  const id = providedId || generatedId;
  const describedBy = error
    ? `${id}-error`
    : hint
      ? `${id}-hint`
      : undefined;

  return (
    <FormField
      id={id}
      label={label}
      hint={hint}
      error={error}
      required={required}
      className={className}
    >
      <div className={`input-shell ${prefix ? "has-prefix" : ""}`}>
        {prefix && <span className="input-prefix" aria-hidden="true">{prefix}</span>}
        <input
          id={id}
          required={required}
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={describedBy}
          {...props}
        />
      </div>
    </FormField>
  );
}

export function PasswordInput({
  id: providedId,
  label = "Password",
  hint,
  error,
  required,
  disabled,
  ...props
}) {
  const generatedId = useId();
  const id = providedId || generatedId;
  const [visible, setVisible] = useState(false);
  const describedBy = error
    ? `${id}-error`
    : hint
      ? `${id}-hint`
      : undefined;

  return (
    <FormField
      id={id}
      label={label}
      hint={hint}
      error={error}
      required={required}
    >
      <div className="input-shell password-shell">
        <input
          id={id}
          type={visible ? "text" : "password"}
          required={required}
          disabled={disabled}
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={describedBy}
          {...props}
        />
        <button
          type="button"
          className="password-toggle"
          onClick={() => setVisible((current) => !current)}
          disabled={disabled}
          aria-label={visible ? "Hide password" : "Show password"}
          aria-pressed={visible}
        >
          <Icon name={visible ? "eyeOff" : "eye"} size={18} />
        </button>
      </div>
    </FormField>
  );
}
