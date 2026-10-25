const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatMoney(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const amount = Number(value);

  if (!Number.isFinite(amount)) {
    return "—";
  }

  return currencyFormatter.format(amount);
}

export function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function formatStatus(value) {
  if (!value) return "Unknown";

  return String(value)
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function getLedgerTotals(ledger = []) {
  return ledger.reduce(
    (totals, entry) => {
      const amount = Number(entry.amount || 0);

      if (!Number.isFinite(amount)) return totals;

      if (entry.type === "CREDIT") {
        totals.credits += amount;
      } else if (entry.type === "DEBIT") {
        totals.debits += amount;
      }

      return totals;
    },
    { credits: 0, debits: 0 }
  );
}

export async function readResponse(response) {
  if (response.status === 204) return null;

  const contentType = response.headers.get("content-type") || "";
  const text = await response.text();

  if (!text) return null;

  if (contentType.includes("application/json")) {
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }

  return text;
}

export function getErrorMessage(data, fallback, status = 0) {
  // Server errors can contain implementation details. Keep those out of the UI.
  if (status >= 500) return fallback;

  if (typeof data === "string" && data.trim()) {
    return data;
  }

  if (data && typeof data === "object") {
    return data.message || data.error || fallback;
  }

  return fallback;
}
