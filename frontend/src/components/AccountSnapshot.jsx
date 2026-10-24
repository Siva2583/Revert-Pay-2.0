import Icon from "./Icon";
import { formatDate, formatMoney, getLedgerTotals } from "../utils/formatters";
import { StatusBadge } from "./Feedback";

function AccountSnapshot({ account, balance, ledger, profile }) {
  const totals = getLedgerTotals(ledger);

  return (
    <div className="account-snapshot">
      <section className="account-summary-card">
        <div className="account-balance-block">
          <p className="eyebrow">Derived balance</p>
          <strong className="account-balance">{formatMoney(balance)}</strong>
          <p className="balance-explanation">
            Total credits minus total debits, calculated from ledger entries.
          </p>
        </div>

        <div className="account-identity-block">
          {profile ? (
            <div className="account-profile-heading">
              <div>
                <p className="eyebrow">My RevertPay profile</p>
                <h2>{profile.name || "Account holder"}</h2>
                <p>{profile.email || "—"}</p>
              </div>
              <StatusBadge status={profile.role} />
            </div>
          ) : (
            <div className="account-profile-heading">
              <div>
                <p className="eyebrow">Ledger account</p>
                <h2 className="mono-value">{account.accountNumber || "—"}</h2>
              </div>
              <span className="account-active-badge">
                <Icon name="book" size={15} />
                Ledger backed
              </span>
            </div>
          )}

          <dl className="account-detail-list">
            {profile && (
              <div>
                <dt>Account number</dt>
                <dd className="mono-value">{account.accountNumber || "—"}</dd>
              </div>
            )}
            <div>
              <dt>Account ID</dt>
              <dd>{account.id ?? "—"}</dd>
            </div>
            <div>
              <dt>Owner</dt>
              <dd>
                {account.ownerType || "—"}
                {account.ownerId !== null && account.ownerId !== undefined
                  ? ` · ID ${account.ownerId}`
                  : ""}
              </dd>
            </div>
            {account.createdAt && (
              <div>
                <dt>Created</dt>
                <dd>{formatDate(account.createdAt)}</dd>
              </div>
            )}
          </dl>
        </div>
      </section>

      <section className="metrics-grid metrics-three" aria-label="Account ledger totals">
        <article className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Incoming credits</span>
            <span className="metric-icon metric-icon-success"><Icon name="arrowDownLeft" size={18} /></span>
          </div>
          <strong className="metric-value">{formatMoney(totals.credits)}</strong>
          <p>All recorded CREDIT entries</p>
        </article>

        <article className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Outgoing debits</span>
            <span className="metric-icon"><Icon name="arrowUpRight" size={18} /></span>
          </div>
          <strong className="metric-value">{formatMoney(totals.debits)}</strong>
          <p>All recorded DEBIT entries</p>
        </article>

        <article className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Ledger records</span>
            <span className="metric-icon"><Icon name="book" size={18} /></span>
          </div>
          <strong className="metric-value">{ledger.length}</strong>
          <p>Immutable transaction entries</p>
        </article>
      </section>
    </div>
  );
}

export default AccountSnapshot;
