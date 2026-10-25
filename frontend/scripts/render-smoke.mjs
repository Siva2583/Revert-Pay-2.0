import assert from "node:assert/strict";
import React from "react";
import { renderToString } from "react-dom/server";
import { createServer } from "vite";

const server = await createServer({
  root: process.cwd(),
  logLevel: "silent",
  server: { middlewareMode: true },
  appType: "custom",
});

const noop = () => {};
const cases = [
  ["AuthScreen", { onLogin: noop }, "Welcome back"],
  ["ResetPassword", { token: "render-token", onBackToLogin: noop }, "Choose a new password"],
  ["Sidebar", { page: "overview", setPage: noop, logout: noop, role: "ADMIN", open: false, onClose: noop }, "System ledger"],
  ["Header", { page: "overview", role: "ADMIN", onOpenNavigation: noop }, "Secure session"],
  ["Overview", { token: "render-token", role: "ADMIN", setPage: noop }, "Loading page content"],
  ["AccountLookup", { token: "render-token", setToast: noop }, "Find a ledger account"],
  ["CreateAccount", { token: "render-token", setToast: noop, setPage: noop }, "New ledger account"],
  ["EscrowInitiate", { token: "render-token", setToast: noop, setPage: noop }, "Payment details"],
  ["MyAccount", { token: "render-token" }, "Loading page content"],
  ["BuyerEscrows", { token: "render-token", setToast: noop, setPage: noop }, "Loading escrow records"],
  ["SellerEscrows", { token: "render-token", setToast: noop }, "Loading escrow records"],
  ["AdminEscrows", { token: "render-token", setToast: noop }, "Loading escrow records"],
  ["AdminLedger", { token: "render-token" }, "Loading page content"],
  ["LedgerTable", { ledger: [], token: "render-token" }, "No ledger activity yet"],
  ["EscrowLifecycle", { status: "FUNDED" }, "Funded"],
];

try {
  for (const [name, props, expectedText] of cases) {
    const module = await server.ssrLoadModule(`/src/components/${name}.jsx`);
    const Component = module.default;
    const html = renderToString(React.createElement(Component, props));

    assert.ok(
      html.includes(expectedText),
      `${name} did not render expected text: ${expectedText}`
    );
    console.log(`PASS ${name}`);
  }

  console.log(`\n${cases.length} render smoke checks passed.`);
} finally {
  await server.close();
}
