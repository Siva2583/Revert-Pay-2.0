import { useState } from "react";
import Logo from "./Logo";
import Icon from "./Icon";
import Button from "./Button";
import { Input, PasswordInput } from "./Input";
import { Alert } from "./Feedback";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useAsyncAction from "../hooks/useAsyncAction";
import editorialArtwork from "../assets/revertpay-editorial.webp";

const roles = [
  { value: "BUYER", label: "Buyer", description: "Make protected purchases", icon: "shield" },
  { value: "SELLER", label: "Seller", description: "Manage escrow orders", icon: "package" },
  { value: "ADMIN", label: "Admin", description: "Oversee ledger and disputes", icon: "book" },
];

function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("BUYER");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [forgotPassword, setForgotPassword] = useState(false);
  const [resetMessage, setResetMessage] = useState("");
  const { pending, run } = useAsyncAction();
  const loading = pending !== null;

  const submit = async (event) => {
    event.preventDefault();
    if (pending) return;

    const isLogin = mode === "login";
    const payload = isLogin ? { email, password } : { name, email, password, role };

    await run(isLogin ? "login" : "register", async () => {
      setError("");
      setNotice("");

      try {
        const data = await apiRequest(isLogin ? API.login : API.register, {
          method: "POST",
          body: payload,
          fallbackMessage: isLogin ? "Sign in could not be completed." : "Registration could not be completed.",
        });

        if (!isLogin) {
          setMode("login");
          setPassword("");
          setName("");
          setNotice("Account created successfully. Please sign in.");
          return;
        }

        const newToken = typeof data === "string" ? data : data?.token || data?.accessToken;

        if (!newToken) {
          setError("Login succeeded, but the server did not return a token.");
          return;
        }

        onLogin(newToken);
      } catch (authError) {
        setError(authError.message || "The request could not be completed.");
      }
    });
  };

  const handleForgotPassword = async (event) => {
    event.preventDefault();
    if (pending) return;

    await run("forgot-password", async () => {
      setError("");
      setResetMessage("");

      try {
        const data = await apiRequest(API.forgotPassword, {
          method: "POST",
          body: { email },
          fallbackMessage: "The password reset request could not be processed.",
        });

        setResetMessage(
          typeof data === "string"
            ? data
            : data?.message || "If an account exists with that email, password reset instructions will be sent."
        );
      } catch (resetError) {
        setError(resetError.message || "The password reset request could not be processed.");
      }
    });
  };

  const showForgotPassword = () => {
    setForgotPassword(true);
    setError("");
    setNotice("");
    setResetMessage("");
  };

  const backToLogin = () => {
    setForgotPassword(false);
    setError("");
    setResetMessage("");
  };

  const heading = forgotPassword
    ? { eyebrow: "Password recovery", title: "Reset your password", description: "Request a secure reset link for your registered email." }
    : mode === "login"
      ? { eyebrow: "Secure sign in", title: "Welcome back.", description: "Enter your credentials to access your ledger workspace." }
      : { eyebrow: "New workspace", title: "Create your account", description: "Choose a role and register with the existing RevertPay workflow." };

  return (
    <main className="auth-shell">
      <section className="auth-intro">
        <img className="auth-artwork" src={editorialArtwork} alt="" aria-hidden="true" />
        <div className="auth-art-shade" aria-hidden="true" />
        <div className="auth-brand"><Logo size={40} withWordmark light /></div>

        <div className="auth-copy">
          <p className="eyebrow">Ledger-first escrow infrastructure</p>
          <h1>Payments should<br />be <span>provable.</span></h1>
          <p>A secure transaction workspace built on immutable ledger records, derived balances, and financial correctness.</p>
        </div>

        <div className="auth-principles" aria-label="RevertPay principles">
          <article><Icon name="book" size={19} /><strong>Immutable ledger</strong><p>Every movement is recorded permanently.</p></article>
          <article><Icon name="shield" size={19} /><strong>Secure access</strong><p>JWT-protected account operations.</p></article>
          <article><Icon name="activity" size={19} /><strong>Derived balances</strong><p>Credits minus debits — never mutable totals.</p></article>
        </div>

        <p className="auth-footer-note">RevertPay / Financial transaction workspace</p>
      </section>

      <section className="auth-form-panel">
        <div className="auth-form-wrap">
          <div className="mobile-brand"><Logo size={36} withWordmark /></div>

          <div className="form-heading">
            <p className="eyebrow">{heading.eyebrow}</p>
            <h2>{heading.title}</h2>
            <p>{heading.description}</p>
          </div>

          {error && <Alert tone="error" title="We couldn’t complete that request"><p>{error}</p></Alert>}
          {notice && <Alert tone="success" title="Registration complete"><p>{notice}</p></Alert>}
          {resetMessage && <Alert tone="success" title="Reset request received"><p>{resetMessage}</p></Alert>}

          <form onSubmit={forgotPassword ? handleForgotPassword : submit} className="standard-form auth-form">
            {forgotPassword ? (
              <>
                <p className="form-intro">Enter your registered email. If an account exists, password reset instructions will be sent.</p>
                <Input id="reset-email" label="Email address" type="email" placeholder="name@example.com" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" disabled={loading} required />
                <Button type="submit" iconAfter="arrowRight" loading={pending === "forgot-password"} loadingLabel="Sending reset link..." disabled={loading} className="button-full">Send reset link</Button>
                <Button variant="ghost" onClick={backToLogin} disabled={loading} className="button-full">Back to sign in</Button>
              </>
            ) : (
              <>
                {mode === "register" && (
                  <Input id="register-name" label="Full name" placeholder="Enter your full name" value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" disabled={loading} required />
                )}

                <Input id="auth-email" label="Email address" type="email" placeholder="name@example.com" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" disabled={loading} required />
                <PasswordInput id="auth-password" label="Password" placeholder="Enter your password" minLength={6} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={mode === "login" ? "current-password" : "new-password"} disabled={loading} required />

                {mode === "login" && (
                  <div className="forgot-password-row"><button type="button" className="text-button" onClick={showForgotPassword} disabled={loading}>Forgot password?</button></div>
                )}

                {mode === "register" && (
                  <fieldset className="role-fieldset" disabled={loading}>
                    <legend>Workspace role <span className="required-mark" aria-hidden="true">*</span></legend>
                    <div className="role-options">
                      {roles.map((item) => (
                        <label className={`role-option ${role === item.value ? "selected" : ""}`} key={item.value}>
                          <input type="radio" name="workspace-role" value={item.value} checked={role === item.value} onChange={() => setRole(item.value)} />
                          <span className="role-option-icon"><Icon name={item.icon} size={18} /></span>
                          <span><strong>{item.label}</strong><small>{item.description}</small></span>
                          <span className="radio-mark" aria-hidden="true" />
                        </label>
                      ))}
                    </div>
                  </fieldset>
                )}

                <Button
                  type="submit"
                  iconAfter="arrowRight"
                  loading={pending === "login" || pending === "register"}
                  loadingLabel={mode === "login" ? "Signing in..." : "Creating account..."}
                  disabled={loading}
                  className="button-full"
                >
                  {mode === "login" ? "Enter workspace" : "Create account"}
                </Button>
              </>
            )}
          </form>

          {!forgotPassword && (
            <div className="auth-mode-switch">
              <span>{mode === "login" ? "New to RevertPay?" : "Already have an account?"}</span>
              <button type="button" className="text-button" disabled={loading} onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); setNotice(""); setPassword(""); }}>
                {mode === "login" ? "Create an account" : "Sign in"}
              </button>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

export default AuthScreen;
