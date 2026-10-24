import { jwtDecode } from "jwt-decode";

export function getRoleFromToken(token) {
  if (!token) return "";

  try {
    const decodedToken = jwtDecode(token);
    return String(decodedToken.role || "")
      .replace(/^ROLE_/, "")
      .toUpperCase();
  } catch {
    return "";
  }
}

export function getRoleLabel(role) {
  const labels = {
    ADMIN: "Administrator",
    BUYER: "Buyer",
    SELLER: "Seller",
  };

  return labels[role] || "Workspace member";
}
