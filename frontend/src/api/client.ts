import axios, { AxiosError } from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
  headers: { "Content-Type": "application/json" },
});

export interface ApiErrorBody {
  error_code: string;
  detail: string;
}

export function isApiErrorBody(data: unknown): data is ApiErrorBody {
  return (
    typeof data === "object" &&
    data !== null &&
    "error_code" in data &&
    "detail" in data
  );
}

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data;
    if (isApiErrorBody(data)) return data.detail;
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

export function getApiErrorCode(error: unknown): string | null {
  if (error instanceof AxiosError) {
    const data = error.response?.data;
    if (isApiErrorBody(data)) return data.error_code;
  }
  return null;
}
