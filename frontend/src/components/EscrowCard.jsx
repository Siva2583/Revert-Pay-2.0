import Icon from "./Icon";
import EscrowLifecycle from "./EscrowLifecycle";
import { StatusBadge } from "./Feedback";
import { formatDate, formatMoney } from "../utils/formatters";
import { getEscrowId } from "../utils/escrow";

export function EscrowContext({
  icon = "info",
  tone = "info",
  title,
  description,
  meta,
}) {
  return (
    <div className={`escrow-context escrow-context-${tone}`}>
      <span className="escrow-context-icon"><Icon name={icon} size={19} /></span>
      <div>
        <strong>{title}</strong>
        {description && <p>{description}</p>}
      </div>
      {meta && <div className="escrow-context-meta">{meta}</div>}
    </div>
  );
}

export default function EscrowCard({
  escrow,
  parties = [],
  icon = "shield",
  children,
}) {
  const escrowId = getEscrowId(escrow);

  return (
    <article className="escrow-card">
      <header className="escrow-card-header">
        <div className="section-heading-with-icon">
          <span className="section-icon"><Icon name={icon} size={20} /></span>
          <div>
            <p className="eyebrow">Escrow #{escrowId ?? "—"}</p>
            <h2>{escrow.itemName || "Unnamed item"}</h2>
          </div>
        </div>
        <StatusBadge status={escrow.status} />
      </header>

      <div className="escrow-card-body">
        <dl className="escrow-facts">
          <div className="escrow-amount-fact">
            <dt>Escrow amount</dt>
            <dd>{formatMoney(escrow.amount)}</dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd>{formatDate(escrow.createdAt)}</dd>
          </div>
          {parties.map((party) => (
            <div key={party.label}>
              <dt>{party.label}</dt>
              <dd>
                {party.name || "Not provided"}
                {party.email && <span>{party.email}</span>}
              </dd>
            </div>
          ))}
        </dl>

        <EscrowLifecycle status={escrow.status} />
        {children}
      </div>
    </article>
  );
}
