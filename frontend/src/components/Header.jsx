import Icon from "./Icon";
import { getRoleLabel } from "../utils/auth";
import { pageMeta } from "../utils/navigation";

function Header({ page, role, onOpenNavigation }) {
  const meta = pageMeta[page] || pageMeta.overview;

  return (
    <header className="topbar">
      <div className="topbar-leading">
        <button
          type="button"
          id="mobile-navigation-trigger"
          className="icon-button mobile-menu-button"
          onClick={onOpenNavigation}
          aria-label="Open navigation"
          aria-controls="application-sidebar"
        >
          <Icon name="menu" size={21} />
        </button>

        <div className="topbar-copy">
          <p className="breadcrumb">
            <span>RevertPay</span>
            <Icon name="chevron" size={12} />
            <span>{meta.title}</span>
          </p>
          <h1>{meta.title}</h1>
          <p className="topbar-description">{meta.description}</p>
        </div>
      </div>

      <div className="topbar-context">
        <span className="session-badge">
          <Icon name="lock" size={14} />
          Secure session
        </span>
        <span className="role-badge">{getRoleLabel(role)}</span>
      </div>
    </header>
  );
}

export default Header;
