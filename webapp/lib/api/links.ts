import { apiFetch } from "@/lib/api-client";

export function rescrapeLink(linkId: string): Promise<{ id: string; scrape_status: string }> {
  return apiFetch<{ id: string; scrape_status: string }>(
    `/links/${encodeURIComponent(linkId)}/rescrape`,
    { method: "POST" },
  );
}
