
import { useEffect, useState } from "react";
import "./App.css";

import AuthScreen from "./components/AuthScreen";
import ResetPassword from "./components/ResetPassword";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Overview from "./components/Overview";
import AccountLookup from "./components/AccountLookup";
import CreateAccount from "./components/CreateAccount";
import EscrowInitiate from "./components/EscrowInitiate";
import MyAccount from "./components/MyAccount";
import Toast from "./components/Toast";
import SellerEscrows from "./components/SellerEscrows";
import BuyerEscrows from "./components/BuyerEscrows";
import AdminEscrows from "./components/AdminEscrows";
import AdminLedger from "./components/AdminLedger";

function App() {
  const [token, setToken] = useState(
    localStorage.getItem("token")
  );
  const [page, setPage] = useState("overview");
  const [toast, setToast] = useState(null);

  // Detect password-reset links before checking login status.
  const isResetPasswordPage =
    window.location.pathname === "/reset-password";

  const resetToken = new URLSearchParams(
    window.location.search
  ).get("token");

  useEffect(() => {
    if (!toast) return;

    const timer = setTimeout(() => setToast(null), 4500);

    return () => clearTimeout(timer);
  }, [toast]);

  const login = (newToken) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setPage("overview");
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setPage("overview");
  };

  // A reset link must work even when the user is already logged in.
  if (isResetPasswordPage) {
    return (
      <ResetPassword
        token={resetToken}
        onBackToLogin={() => {
          localStorage.removeItem("token");
          window.location.replace("/");
        }}
      />
    );
  }

  if (!token) {
    return <AuthScreen onLogin={login} />;
  }

  return (
    <div className="app-shell">
      <Sidebar
        page={page}
        setPage={setPage}
        logout={logout}
        token={token}
      />

      <main className="main-workspace">
        {page !== "admin-ledger" && (
          <Header page={page} />
        )}

        <div className="workspace-content">
          {page === "overview" && (
            <Overview setPage={setPage} />
          )}

          {page === "accounts" && (
            <AccountLookup
              token={token}
              setToast={setToast}
            />
          )}

          {page === "create" && (
            <CreateAccount
              token={token}
              setToast={setToast}
            />
          )}

          {page === "escrow" && (
            <EscrowInitiate
              token={token}
              setToast={setToast}
            />
          )}

          {page === "seller-escrows" && (
            <SellerEscrows
              token={token}
              setToast={setToast}
            />
          )}

          {page === "buyer-escrows" && (
            <BuyerEscrows
              token={token}
              setToast={setToast}
            />
          )}

          {page === "admin-escrows" && (
            <AdminEscrows
              token={token}
              setToast={setToast}
            />
          )}

          {page === "admin-ledger" && (
            <AdminLedger token={token} />
          )}

          {page === "my-account" && (
            <MyAccount token={token} />
          )}
        </div>
      </main>

      <Toast
        toast={toast}
        closeToast={() => setToast(null)}
      />
    </div>
  );
}

export default App;

