export function getEscrowId(escrow) {
  return escrow?.id ?? escrow?.escrowid ?? escrow?.escrowId;
}

export function getParty(person, fallbackName) {
  return {
    name: person?.name || fallbackName || person?.email || "Not provided",
    email: person?.email || "",
  };
}
