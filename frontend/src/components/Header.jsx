import React from "react";

function Header({ page }) {
const titles = {
overview: [
"Overview",
"Monitor account balances and ledger activity."
],

accounts: [
  "Account lookup",
  "Inspect a ledger account and its immutable entries."
],

create: [
  "Create account",
  "Provision a new account in the ledger workspace."
],

transfer: [
  "Ledger transfer",
  "Move funds through a balanced double-entry record."
],

escrow: [
  "Initiate payment",
  "Review seller, item, and amount before confirmation."
],

"seller-escrows": [
  "Seller Escrows",
  "Review orders, shipments, and escrow activity."
],

"buyer-escrows": [
  "My Escrows",
  "Track your purchases, delivery, and escrow status."
],

"admin-escrows": [
  "Admin Disputes",
  "Review and resolve marketplace disputes."
],

"my-account": [
  "My Account",
  "View your RevertPay identity, account, balance, and ledger activity."
],


};

const [title, description] = titles[page] || titles.overview;

return ( <header className="topbar"> <div> <p className="breadcrumb">
REVERTPAY / {(page || "overview").toUpperCase()} </p>


    <h1>{title}</h1>

    <span>{description}</span>
  </div>

  <div className="topbar-status">
    <span className="pulse-dot" />
    Secure session
  </div>
</header>


);
}

export default Header;
