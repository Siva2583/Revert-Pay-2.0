import { getErrorMessage, readResponse } from "../utils/formatters";

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function apiRequest(
  path,
  {
    token,
    method = "GET",
    body,
    headers = {},
    signal,
    fallbackMessage = "The request could not be completed.",
  } = {}
) {
  const requestHeaders = { ...headers };

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  let requestBody = body;

  if (body !== undefined && body !== null && typeof body !== "string") {
    requestHeaders["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  if (typeof body === "string") {
    requestHeaders["Content-Type"] = "application/json";
  }

  const response = await fetch(path, {
    method,
    headers: requestHeaders,
    body: requestBody,
    signal,
  });

  const data = await readResponse(response);

  if (!response.ok) {
    throw new ApiError(
      getErrorMessage(data, fallbackMessage, response.status),
      response.status,
      data
    );
  }

  return data;
}
