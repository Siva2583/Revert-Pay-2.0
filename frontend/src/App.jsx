import { useCallback, useEffect, useState } from "react";
import "./App.css";
import "./styles/editorial.css";

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
import { getRoleFromToken } from "./utils/auth";
import { getAllowedPages } from "./utils/navigation";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [page, setPage] = useState("overview");
  const [toast, setToast] = useState(null);
  const [navigationOpen, setNavigationOpen] = useState(false);

  const isResetPasswordPage = window.location.pathname === "/reset-password";
  const resetToken = new URLSearchParams(window.location.search).get("token");
  const role = getRoleFromToken(token);
  const allowedPages = getAllowedPages(role);
  const activePage = allowedPages.includes(page) ? page : "overview";

  useEffect(() => {
    if (!toast) return undefined;

    const timer = setTimeout(() => setToast(null), 6000);
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
    setToast(null);
    setNavigationOpen(false);
  };

  const closeNavigation = useCallback(() => {
    setNavigationOpen(false);
  }, []);

  const navigate = useCallback((nextPage) => {
    setPage(nextPage);
    setNavigationOpen(false);
  }, []);

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
      <a className="skip-link" href="#main-content">Skip to main content</a>

      <Sidebar
        page={activePage}
        setPage={navigate}
        logout={logout}
        role={role}
        open={navigationOpen}
        onClose={closeNavigation}
      />

      <main className="main-workspace" id="main-content" tabIndex={-1}>
        <Header
          page={activePage}
          role={role}
          onOpenNavigation={() => setNavigationOpen(true)}
        />

        <div className="workspace-content">
          {activePage === "overview" && (
            <Overview token={token} role={role} setPage={navigate} />
          )}

          {activePage === "accounts" && (
            <AccountLookup token={token} setToast={setToast} />
          )}

          {activePage === "create" && (
            <CreateAccount token={token} setToast={setToast} setPage={navigate} />
          )}

          {activePage === "escrow" && (
            <EscrowInitiate token={token} setToast={setToast} setPage={navigate} />
          )}

          {activePage === "seller-escrows" && (
            <SellerEscrows token={token} setToast={setToast} />
          )}

          {activePage === "buyer-escrows" && (
            <BuyerEscrows token={token} setToast={setToast} setPage={navigate} />
          )}

          {activePage === "admin-escrows" && (
            <AdminEscrows token={token} setToast={setToast} />
          )}

          {activePage === "admin-ledger" && <AdminLedger token={token} />}

          {activePage === "my-account" && <MyAccount token={token} />}
        </div>
      </main>

      <Toast toast={toast} closeToast={() => setToast(null)} />
    </div>
  );
}

export default App;
