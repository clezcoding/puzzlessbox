import { apiFetch, type Category } from "@/lib/api-client";

export function listCategories(): Promise<Category[]> {
  return apiFetch<Category[]>("/categories");
}

export function createCategory(
  name: string,
  color?: string,
): Promise<{ id: string; name: string }> {
  return apiFetch<{ id: string; name: string }>("/categories", {
    method: "POST",
    body: JSON.stringify({ name, color }),
  });
}

export function updateCategory(
  id: string,
  fields: { name?: string; color?: string; sort_order?: number },
): Promise<Category> {
  return apiFetch<Category>(`/categories/${id}`, {
    method: "PATCH",
    body: JSON.stringify(fields),
  });
}

export function deleteCategory(id: string): Promise<void> {
  return apiFetch<void>(`/categories/${id}`, { method: "DELETE" });
}

export type CategoryReorderEntry = { id: string; sort_order: number };

export function reorderCategories(
  items: CategoryReorderEntry[],
): Promise<{ status: string }> {
  return apiFetch<{ status: string }>("/categories/reorder", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export type { Category };
