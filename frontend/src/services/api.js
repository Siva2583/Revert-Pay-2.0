const API = {
  login: "/api/auth/login",
  me: "/api/me",
  register: "/api/auth/register",
  resetPassword: "/api/auth/reset-password",
  forgotPassword: "/api/auth/forgot-password",
  createAccount: "/api/accounts/new",

  getAccount: (accountNumber) =>
    `/api/accounts/${encodeURIComponent(accountNumber)}`,

  getBalance: (accountNumber) =>
    `/api/accounts/${encodeURIComponent(accountNumber)}/balance`,

  getLedger: (accountNumber) =>
    `/api/accounts/${encodeURIComponent(accountNumber)}/ledger`,

  transfer: "/api/auth/transfer",
  sellerEscrows: "/api/escrow/seller",
  buyerEscrows: "/api/escrow/buyer",
  adminEscrows: "/api/escrow/admin",
  adminLedger: "/api/admin/ledger/holding",
  escrowInitiate: "/api/escrow/initiate",
  escrowAction: (id, action) => `/api/escrow/${id}/${action}`,
  getDispute: (id) => `/api/escrow/${id}/dispute`,
  raiseDispute: (id) => `/api/escrow/${id}/dispute`,
  respondToDispute: (disputeId) =>
    `/api/escrow/${disputeId}/respond`,
  resolveDispute: (disputeId) =>
    `/api/escrow/${disputeId}/resolve`,
  getEscrowLedgerDetails: (id) =>
    `/api/escrow/${id}/ledger-details`,
};

export default API;
