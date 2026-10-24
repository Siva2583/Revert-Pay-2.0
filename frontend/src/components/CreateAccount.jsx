import { useState } from "react";
import Icon from "./Icon";
import API from "../services/api";
import { apiRequest } from "../services/request";
import useAsyncAction from "../hooks/useAsyncAction";
import Button from "./Button";
import { FormField, Input } from "./Input";
import { Alert } from "./Feedback";
import { formatDate } from "../utils/formatters";

function CreateAccount({ token, setToast, setPage }) {
  const [ownerType, setOwnerType] = useState("USER");
  const [ownerId, setOwnerId] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const { pending, run } = useAsyncAction();
  const loading = pending === "create-account";

  const submit = async (event) => {
    event.preventDefault();
    if (pending) return;

    await run("create-account", async () => {
      setError("");
      setResult(null);

      try {
        const data = await apiRequest(API.createAccount, {
          token,
          method: "POST",
          body: {
            ownerType,
            ownerId: Number(ownerId),
            accountNumber: accountNumber.trim(),
          },
          fallbackMessage: "The account could not be created.",
        });

        setResult(data);
        setOwnerId("");
        setAccountNumber("");
        setOwnerType("USER");
        setToast({
          type: "success",
          title: "Account created",
          message: `${data.accountNumber || "The ledger account"} was created successfully.`,
        });
      } catch (createError) {
        setError(createError.message || "The account could not be created.");
      }
    });
  };

  return (
    <div className="form-layout">
      <section className="surface-card form-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">New ledger account</p>
            <h2>Account details</h2>
            <p>Provide the owner and unique account reference for this record.</p>
          </div>
          <span className="section-icon"><Icon name="wallet" size={21} /></span>
        </div>

        {error && (
          <Alert tone="error" title="Account creation failed">
            <p>{error}</p>
          </Alert>
        )}

        <form onSubmit={submit} className="standard-form">
          <FormField
            id="account-owner-type"
            label="Owner type"
            hint="Choose the owner category supported by the existing account model."
            required
          >
            <select
              id="account-owner-type"
              value={ownerType}
              onChange={(event) => setOwnerType(event.target.value)}
              disabled={loading}
              aria-describedby="account-owner-type-hint"
              required
            >
              <option value="USER">User</option>
              <option value="SYSTEM">System</option>
            </select>
          </FormField>

          <Input
            id="account-owner-id"
            label="Owner ID"
            type="number"
            step="1"
            inputMode="numeric"
            placeholder="Enter owner identifier"
            hint="Use the numeric identifier of the account owner."
            value={ownerId}
            onChange={(event) => setOwnerId(event.target.value)}
            disabled={loading}
            required
          />

          <Input
            id="new-account-number"
            label="Account number"
            placeholder="Enter a unique account number"
            hint="This reference is used for account lookup and ledger requests."
            autoComplete="off"
            spellCheck={false}
            value={accountNumber}
            onChange={(event) => setAccountNumber(event.target.value)}
            disabled={loading}
            required
          />

          <div className="form-actions">
            <Button
              type="submit"
              icon="plus"
              loading={loading}
              loadingLabel="Creating account..."
            >
              Create account
            </Button>
          </div>
        </form>
      </section>

      <aside className="guidance-panel">
        <p className="eyebrow">Before you create</p>
        <h2>A precise account record starts here.</h2>
        <p>
          RevertPay uses this account reference to organize permanent debit and credit entries.
        </p>
        <ol className="guidance-list">
          <li>
            <span>01</span>
            <div><strong>Verify the owner</strong><p>Confirm the owner type and numeric identifier.</p></div>
          </li>
          <li>
            <span>02</span>
            <div><strong>Use a unique reference</strong><p>The backend enforces account-number uniqueness.</p></div>
          </li>
          <li>
            <span>03</span>
            <div><strong>Confirm the server result</strong><p>A created account appears only after a successful response.</p></div>
          </li>
        </ol>
        <div className="guidance-note">
          <Icon name="shield" size={18} />
          <p>No balance is assumed or displayed for a newly created account.</p>
        </div>
      </aside>

      {result && (
        <section className="surface-card confirmation-card form-layout-full">
          <Alert tone="success" title="Account created successfully">
            <p>The server returned the following account record.</p>
          </Alert>
          <dl className="confirmation-details">
            <div><dt>Account number</dt><dd className="mono-value">{result.accountNumber || "—"}</dd></div>
            <div><dt>Account ID</dt><dd>{result.id ?? "—"}</dd></div>
            <div><dt>Owner type</dt><dd>{result.ownerType || "—"}</dd></div>
            <div><dt>Owner ID</dt><dd>{result.ownerId ?? "—"}</dd></div>
            {result.createdAt && <div><dt>Created</dt><dd>{formatDate(result.createdAt)}</dd></div>}
          </dl>
          <Button variant="secondary" icon="search" onClick={() => setPage("accounts")}>
            Go to account lookup
          </Button>
        </section>
      )}
    </div>
  );
}

export default CreateAccount;
