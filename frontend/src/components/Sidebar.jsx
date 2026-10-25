import { useEffect, useRef } from "react";
import Logo from "./Logo";
import Icon from "./Icon";
import { getRoleLabel } from "../utils/auth";
import { getNavigation } from "../utils/navigation";

function Sidebar({ page, setPage, logout, role, open, onClose }) {
  const groups = getNavigation(role);
  const closeButtonRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;

    const previousFocus = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeButtonRef.current?.focus();

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
      previousFocus?.focus?.();
    };
  }, [open, onClose]);

  return (
    <>
      {open && (
        <button
          type="button"
          className="sidebar-overlay"
          onClick={onClose}
          aria-label="Close navigation"
        />
      )}

      <aside
        id="application-sidebar"
        className={`sidebar ${open ? "sidebar-open" : ""}`}
        aria-label="Application navigation"
      >
        <div className="sidebar-brand">
          <Logo size={38} />
          <div className="sidebar-brand-copy">
            <strong>RevertPay</strong>
            <span>Financial operations</span>
          </div>
          <button
            ref={closeButtonRef}
            type="button"
            className="icon-button sidebar-close"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <Icon name="close" size={20} />
          </button>
        </div>

        <nav className="sidebar-navigation">
          {groups.map((group) => (
            <div className="sidebar-group" key={group.label}>
              <p className="sidebar-section-label">{group.label}</p>
              <div className="side-nav">
                {group.items.map((item) => {
                  const current = page === item.key;

                  return (
                    <button
                      type="button"
                      key={item.key}
                      className={current ? "current" : ""}
                      onClick={() => setPage(item.key)}
                      aria-current={current ? "page" : undefined}
                    >
                      <Icon name={item.icon} size={19} />
                      <span>{item.label}</span>
                      {current && <span className="nav-current-mark" aria-hidden="true" />}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="workspace-identity">
            <div className="workspace-avatar" aria-hidden="true">
              <Icon name="user" size={18} />
            </div>
            <div>
              <span>Signed in as</span>
              <strong>{getRoleLabel(role)}</strong>
            </div>
            <Icon name="lock" size={14} className="workspace-lock" />
          </div>

          <button type="button" className="sign-out" onClick={logout}>
            <Icon name="logout" size={18} />
            Sign out
          </button>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
