import Logo from "./Logo";
import Icon from "./Icon";
import { jwtDecode } from "jwt-decode";

function Sidebar({ page, setPage, logout, token }) {
let role = "";

try {
if (token) {
const decodedToken = jwtDecode(token);
role = (decodedToken.role || "")
.replace(/^ROLE_/, "")
.toUpperCase();
}
} catch (error) {
console.error("Unable to decode authentication token:", error);
}

const isAdmin = role === "ADMIN";
const isBuyer = role === "BUYER";
const isSeller = role === "SELLER";

const items = [
  { key: "overview", label: "Overview", icon: "grid" },
];

if (isBuyer || isSeller) {
  items.push({
    key: "my-account",
    label: "My Account",
    icon: "wallet",
  });
}

if (isBuyer) {
items.push(
{ key: "escrow", label: "Initiate payment", icon: "shield" },
{ key: "buyer-escrows", label: "My Escrows", icon: "shield" }
);
}

if (isSeller) {
items.push({
key: "seller-escrows",
label: "Seller Escrows",
icon: "package",
});
}

if (isAdmin) {
items.push(
{ key: "accounts", label: "Account lookup", icon: "wallet" },
{ key: "create", label: "Create account", icon: "plus" },
{ key: "admin-escrows", label: "Admin Disputes", icon: "shield" },
{ key: "admin-ledger", label: "System Ledger", icon: "activity" }
);
}


return ( <aside className="sidebar"> <div className="sidebar-brand"> <Logo size={38} /> <div> <strong>RevertPay</strong> <span>CORE LEDGER</span> </div> </div>


  <div className="sidebar-section-label">WORKSPACE</div>

  <nav className="side-nav">
    {items.map((item) => (
      <button
        key={item.key}
        className={page === item.key ? "current" : ""}
        onClick={() => setPage(item.key)}
      >
        <Icon name={item.icon} />
        <span>{item.label}</span>
        {page === item.key && <i />}
      </button>
    ))}
  </nav>

  <div className="sidebar-bottom">
    <div className="integrity-box">
      <div className="integrity-dot" />
      <div>
        <span>System status</span>
        <strong>Ledger online</strong>
      </div>
    </div>

    <button className="sign-out" onClick={logout}>
      <Icon name="logout" />
      Sign out
    </button>
  </div>
</aside>


);
}

export default Sidebar;
