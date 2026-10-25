import { useEffect, useRef, useState } from "react";
import Icon from "./Icon";
import AccountSnapshot from "./AccountSnapshot";
import LedgerTable from "./LedgerTable";
import API from "../services/api";
import { apiRequest } from "../services/request";
import Button from "./Button";
import { Input } from "./Input";
import { Alert, EmptyState } from "./Feedback";
import { MetricsSkeleton, TableSkeleton } from "./LoadingSpinner";

function AccountLookup({ token, setToast, onLoaded }) {
  const [accountNumber, setAccountNumber] = useState("");
  const [account, setAccount] = useState(null);
  const [balance, setBalance] = useState(null);
  const [ledger, setLedger] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const requestRef = useRef({ id: 0, controller: null });

  useEffect(() => {
    return () => {
      requestRef.current.id += 1;
      requestRef.current.controller?.abort();
    };
  }, []);

  const findAccount = async (event) => {
    event?.preventDefault();

    if (loading) return;

    const number = accountNumber.trim();

    if (!number) {
      setError({
        title: "Account number required",
        message: "Enter an account number before searching.",
      });
      return;
    }

    const requestId = requestRef.current.id + 1;
    requestRef.current.controller?.abort();
    const controller = new AbortController();
    requestRef.current = { id: requestId, controller };

    setLoading(true);
    setError(null);
    setAccount(null);
    setBalance(null);
    setLedger([]);

    try {
      const accountData = await apiRequest(API.getAccount(number), {
        token,
        signal: controller.signal,
        fallbackMessage: "The account lookup could not be completed.",
      });

      if (requestRef.current.id !== requestId) return;

      if (!accountData) {
        setError({
          title: "Account not found",
          message: `No account was returned for ${number}. Check the number and try again.`,
        });
        return;
      }

      const [balanceData, ledgerData] = await Promise.all([
        apiRequest(API.getBalance(number), {
          token,
          signal: controller.signal,
          fallbackMessage: "The account balance could not be loaded.",
        }),
        apiRequest(API.getLedger(number), {
          token,
          signal: controller.signal,
          fallbackMessage: "The account ledger could not be loaded.",
        }),
      ]);

      if (requestRef.current.id !== requestId) return;

      if (!Array.isArray(ledgerData)) {
        throw new Error("The ledger response was incomplete. Please try again.");
      }

      setAccount(accountData);
      setBalance(balanceData);
      setLedger(ledgerData);
      onLoaded?.(accountData, balanceData, ledgerData);

      setToast({
        type: "success",
        title: "Account loaded",
        message: `Balance and ledger data for ${number} are ready.`,
      });
    } catch (lookupError) {
      if (
        lookupError.name === "AbortError" ||
        requestRef.current.id !== requestId
      ) {
        return;
      }

      setError({
        title: lookupError.status === 404 ? "Account not found" : "Lookup failed",
        message:
          lookupError.status === 404
            ? `No account was found for ${number}. Check the number and try again.`
            : lookupError.message || "The account could not be loaded.",
      });
    } finally {
      if (requestRef.current.id === requestId) {
        setLoading(false);
      }
    }
  };

  return (
    <div className="page-stack">
      <section className="surface-card lookup-command">
        <div className="section-heading lookup-heading">
          <div className="section-heading-with-icon">
            <span className="section-icon"><Icon name="search" size={21} /></span>
            <div>
              <p className="eyebrow">Account explorer</p>
              <h2>Find a ledger account</h2>
              <p>Search with the exact account number assigned by RevertPay.</p>
            </div>
          </div>
        </div>

        <form onSubmit={findAccount} className="lookup-form">
          <Input
            id="account-lookup-number"
            label="Account number"
            hint="For example, use an existing account reference such as ACC1001."
            placeholder="Enter account number"
            autoComplete="off"
            autoCapitalize="characters"
            spellCheck={false}
            value={accountNumber}
            onChange={(event) => setAccountNumber(event.target.value)}
            disabled={loading}
            required
          />
          <Button
            type="submit"
            icon="search"
            loading={loading}
            loadingLabel="Searching..."
          >
            Look up account
          </Button>
        </form>
      </section>

      {error && (
        <Alert tone="error" title={error.title}>
          <p>{error.message}</p>
        </Alert>
      )}

      {loading && (
        <div className="page-stack" aria-busy="true">
          <span className="sr-only">Loading account, balance, and ledger</span>
          <MetricsSkeleton count={3} />
          <div className="surface-card"><TableSkeleton rows={5} /></div>
        </div>
      )}

      {!account && !loading && !error && (
        <div className="surface-card">
          <EmptyState
            icon="wallet"
            title="Ready for account lookup"
            description="An account’s derived balance, owner details, and complete ledger history will appear here."
          />
        </div>
      )}

      {account && !loading && (
        <>
          <AccountSnapshot account={account} balance={balance} ledger={ledger} />

          <section className="surface-card data-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Immutable records</p>
                <h2>Complete ledger history</h2>
                <p>Debit and credit entries for {account.accountNumber}.</p>
              </div>
              <span className="record-count">{ledger.length} {ledger.length === 1 ? "entry" : "entries"}</span>
            </div>
            <LedgerTable ledger={ledger} token={token} />
          </section>
        </>
      )}
    </div>
  );
}

export default AccountLookup;
