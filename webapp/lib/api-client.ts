export class ApiError extends Error {
  readonly code: string;
  readonly details?: unknown;

  constructor(code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
  }
}

type ApiErrorBody = {
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  detail?: {
    code: string;
    message: string;
    details?: unknown;
  };
};

function parseApiError(body: ApiErrorBody): ApiError {
  const shaped = body.error ?? body.detail;
  if (shaped?.code && shaped?.message) {
    return new ApiError(shaped.code, shaped.message, shaped.details);
  }
  return new ApiError("UNKNOWN", "API request failed");
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const headers = new Headers(options.headers);

  if (options.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    credentials: "include",
    headers,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw parseApiError(body);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export interface Category {
  id: string;
  owner_id: string | null;
  name: string;
  color: string | null;
  sort_order: number;
  created_at: string | null;
}

export interface BoardItem {
  id: string;
  owner_id: string;
  category_id: string;
  status: string;
  title: string;
  summary: string;
  type: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export type ItemUpdateFields = {
  title?: string;
  body?: string;
  url?: string;
  due?: string;
  event_start?: string;
  event_end?: string;
  category_id?: string;
  sort_order?: number;
  type?: string;
};

export type ConflictDetails = {
  etag?: string;
  remote_state?: {
    title?: string;
    event_start?: string;
    event_end?: string;
    starts_at?: string;
    ends_at?: string;
  };
};

export type UpdateItemResult =
  | { ok: true }
  | { ok: false; conflict: ConflictDetails };

export function getCategories(): Promise<Category[]> {
  return apiFetch<Category[]>("/categories");
}

export function getBoardItems(): Promise<BoardItem[]> {
  return apiFetch<BoardItem[]>("/board-items");
}
