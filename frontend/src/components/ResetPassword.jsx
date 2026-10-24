import { useState } from "react";
import Logo from "./Logo";
import Icon from "./Icon";
import API from "../services/api";
import { readResponse } from "../utils/formatters";

function ResetPassword({ token, onBackToLogin }) {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!token) {
      setError("The reset link is invalid or missing its token.");
      return;
    }

    if (password.length < 8) {
      setError("Your password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(API.resetPassword, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          newPassword: password,
        }),
      });

      const data = await readResponse(response);

      if (!response.ok) {
        setError(
          typeof data === "string"
            ? data
            : data.message || "Unable to reset your password."
        );
        return;
      }

      setSuccess(
        typeof data === "string"
          ? data
          : data.message || "Password reset successfully."
      );

      setPassword("");
      setConfirmPassword("");
    } catch {
      setError("Cannot reach the RevertPay server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="reset-password-shell">
      <section className="reset-password-card">
        <div className="reset-password-brand">
          <Logo size={36} />
          <strong>RevertPay</strong>
        </div>

        <p className="micro-label">ACCOUNT RECOVERY</p>

        <h1>Choose a new password.</h1>

        <p className="reset-password-description">
          Create a new password to regain access to your RevertPay
          workspace.
        </p>

        {error && (
          <div className="auth-alert" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="auth-alert success" role="status">
            {success}
          </div>
        )}

        {!success && (
          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >
            <label htmlFor="new-password">New password</label>

            <input
              id="new-password"
              type="password"
              autoComplete="new-password"
              placeholder="At least 8 characters"
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />

            <label htmlFor="confirm-password">
              Confirm new password
            </label>

            <input
              id="confirm-password"
              type="password"
              autoComplete="new-password"
              placeholder="Enter your new password again"
              minLength={8}
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
              required
            />

            <button
              className="auth-submit"
              type="submit"
              disabled={loading}
            >
              {loading ? "Resetting..." : "Reset password"}
              <Icon name="chevron" size={18} />
            </button>
          </form>
        )}

        {success ? (
          <button
            type="button"
            className="forgot-password-back"
            onClick={onBackToLogin}
          >
            Return to sign in
          </button>
        ) : (
          <button
            type="button"
            className="forgot-password-back"
            onClick={onBackToLogin}
          >
            Back to sign in
          </button>
        )}
      </section>
    </main>
  );
}

export default ResetPassword;