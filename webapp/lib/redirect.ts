/** Open-redirect guard: only same-origin relative paths (T-04-04). */
export function getSafeNextPath(next: string | null | undefined): string | null {
  if (!next) return null;
  if (/^https?:\/\//i.test(next)) return null;
  if (next.startsWith("//")) return null;
  if (!next.startsWith("/")) return null;
  if (next.includes("\\")) return null;
  return next;
}
