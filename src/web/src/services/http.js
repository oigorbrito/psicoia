import { API_BASE } from "../config/api";

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function requestJson(
  path,
  { method = "GET", body, token, onUnauthorized, headers = {} } = {}
) {
  const requestHeaders = { ...headers };

  if (!(body instanceof FormData)) {
    requestHeaders["Content-Type"] = "application/json";
  }

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers: requestHeaders,
      body:
        body === undefined
          ? undefined
          : body instanceof FormData
          ? body
          : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("Não foi possível conectar à API local. Verifique se o backend está em execução.", 0, null);
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (response.status === 401 && onUnauthorized) {
    onUnauthorized();
  }

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.find((item) => typeof item?.msg === "string")?.msg || "Os dados informados são inválidos."
      : typeof detail === "string"
      ? detail
      : `Falha na solicitação (status ${response.status}).`;
    throw new ApiError(message, response.status, data);
  }

  return data;
}
