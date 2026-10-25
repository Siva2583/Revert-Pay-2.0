import { useState } from "react";
import Logo from "./Logo";
import Icon from "./Icon";
import Button from "./Button";
import { PasswordInput } from "./Input";
import { Alert } from "./Feedback";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useAsyncAction from "../hooks/useAsyncAction";

function ResetPassword({ token, onBackToLogin }) {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { pending, run } = useAsyncAction();
  const loading = pending !== null;

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (pending) return;

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

    await run("reset-password", async () => {
      try {
        const data = await apiRequest(API.resetPassword, {
          method: "POST",
          body: { token, newPassword: password },
          fallbackMessage: "Your password could not be reset.",
        });

        setSuccess(
          typeof data === "string" ? data : data?.message || "Password reset successfully."
        );
        setPassword("");
        setConfirmPassword("");
      } catch (resetError) {
        setError(resetError.message || "Your password could not be reset.");
      }
    });
  };

  return (
    <main className="reset-password-shell">
      <section className="reset-password-card">
        <div className="reset-password-brand"><Logo size={38} withWordmark /></div>
        <span className="reset-password-icon"><Icon name={success ? "checkCircle" : "lock"} size={25} /></span>
        <p className="eyebrow">Account recovery</p>
        <h1>{success ? "Password updated" : "Choose a new password"}</h1>
        <p className="reset-password-description">
          {success ? "Your reset was confirmed by the server. You can now return to sign in." : "Create a new password to regain access to your RevertPay workspace."}
        </p>

        {error && <Alert tone="error" title="Password wasn’t reset"><p>{error}</p></Alert>}
        {success && <Alert tone="success" title="Password reset complete"><p>{success}</p></Alert>}

        {!success && (
          <form className="standard-form" onSubmit={handleSubmit}>
            <PasswordInput id="new-password" label="New password" autoComplete="new-password" placeholder="At least 8 characters" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} disabled={loading} required />
            <PasswordInput id="confirm-password" label="Confirm new password" autoComplete="new-password" placeholder="Enter your new password again" minLength={8} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} disabled={loading} required />
            <Button type="submit" iconAfter="arrowRight" loading={pending === "reset-password"} loadingLabel="Resetting password..." disabled={loading} className="button-full">Reset password</Button>
          </form>
        )}

        <Button variant="ghost" onClick={onBackToLogin} disabled={loading} className="button-full">
          {success ? "Return to sign in" : "Back to sign in"}
        </Button>

        <p className="recovery-note"><Icon name="shield" size={15} />Reset tokens are submitted only through the existing recovery request.</p>
      </section>
    </main>
  );
}

export default ResetPassword;
