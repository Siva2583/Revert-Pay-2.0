export const pageMeta = {
  overview: {
    title: "Overview",
    description: "A clear view of your RevertPay financial workspace.",
  },
  "my-account": {
    title: "My account",
    description: "Your profile, derived balance, and immutable ledger activity.",
  },
  accounts: {
    title: "Account lookup",
    description: "Inspect a ledger account and its recorded entries.",
  },
  create: {
    title: "Create account",
    description: "Provision an account using the existing ledger contract.",
  },
  escrow: {
    title: "Initiate payment",
    description: "Create, review, and fund a protected escrow payment.",
  },
  "buyer-escrows": {
    title: "My escrows",
    description: "Track purchases, delivery, disputes, and protected funds.",
  },
  "seller-escrows": {
    title: "Seller escrows",
    description: "Manage funded orders, shipment, and dispute responses.",
  },
  "admin-escrows": {
    title: "Dispute resolution",
    description: "Review evidence and resolve protected escrow payments.",
  },
  "admin-ledger": {
    title: "System ledger",
    description: "Monitor the escrow holding account and recent entries.",
  },
};

export function getNavigation(role) {
  const workspace = [
    { key: "overview", label: "Overview", icon: "grid" },
  ];

  if (role === "BUYER" || role === "SELLER") {
    workspace.push({
      key: "my-account",
      label: "My account",
      icon: "wallet",
    });
  }

  const groups = [{ label: "Workspace", items: workspace }];

  if (role === "BUYER") {
    groups.push({
      label: "Escrow",
      items: [
        { key: "escrow", label: "Initiate payment", icon: "plus" },
        { key: "buyer-escrows", label: "My escrows", icon: "shield" },
      ],
    });
  }

  if (role === "SELLER") {
    groups.push({
      label: "Escrow",
      items: [
        { key: "seller-escrows", label: "Seller escrows", icon: "package" },
      ],
    });
  }

  if (role === "ADMIN") {
    groups.push({
      label: "Administration",
      items: [
        { key: "accounts", label: "Account lookup", icon: "search" },
        { key: "create", label: "Create account", icon: "plus" },
        { key: "admin-escrows", label: "Dispute resolution", icon: "shield" },
        { key: "admin-ledger", label: "System ledger", icon: "book" },
      ],
    });
  }

  return groups;
}

export function getAllowedPages(role) {
  return getNavigation(role).flatMap((group) =>
    group.items.map((item) => item.key)
  );
}
