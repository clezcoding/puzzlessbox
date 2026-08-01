import {
  apiFetch,
  ApiError,
  type BoardItem,
  type ConflictDetails,
  type ItemUpdateFields,
  type UpdateItemResult,
} from "@/lib/api-client";

const baseUrl = () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function moveItem(id: string, categoryId: string): Promise<{ id: string }> {
  return updateItem(id, { category_id: categoryId }).then((result) => {
    if (!result.ok) {
      throw new ApiError("CONFLICT", "Calendar conflict");
    }
    return { id };
  });
}

export async function updateItem(
  id: string,
  fields: ItemUpdateFields,
  options?: { force?: boolean },
): Promise<UpdateItemResult> {
  const headers = new Headers({ "Content-Type": "application/json" });
  if (options?.force) {
    headers.set("If-None-Match", "*");
  }

  const response = await fetch(`${baseUrl()}/items/${id}`, {
    method: "PATCH",
    credentials: "include",
    headers,
    body: JSON.stringify(fields),
  });

  if (response.status === 412) {
    const body = (await response.json()) as {
      error?: { details?: ConflictDetails };
      detail?: { details?: ConflictDetails };
    };
    const details = body.error?.details ?? body.detail?.details ?? {};
    return { ok: false, conflict: details };
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as {
      error?: { code: string; message: string };
      detail?: { code: string; message: string };
    };
    const shaped = body.error ?? body.detail;
    throw new ApiError(
      shaped?.code ?? "UNKNOWN",
      shaped?.message ?? "API request failed",
    );
  }

  return { ok: true };
}

export function deleteItem(id: string): Promise<void> {
  return apiFetch<void>(`/items/${id}`, { method: "DELETE" });
}

export function restoreItem(id: string): Promise<{ id: string; status: string }> {
  return apiFetch<{ id: string; status: string }>(`/items/${id}/restore`, {
    method: "POST",
  });
}

export type ReorderEntry = { id: string; sort_order: number };

export function reorderItems(items: ReorderEntry[]): Promise<{ status: string }> {
  return apiFetch<{ status: string }>("/items/reorder", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export type { BoardItem, ItemUpdateFields, ConflictDetails };
