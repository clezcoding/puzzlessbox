import { apiFetch } from "@/lib/api-client";

export type GoogleCalendar = {
  id: string;
  summary: string;
  primary?: boolean;
};

export type CalendarStatus = {
  connected: boolean;
  selected_calendar_id: string | null;
};

const apiBase = () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getCalendarConnectUrl(): string {
  return `${apiBase()}/auth/google/connect`;
}

export function getCalendarStatus(): Promise<CalendarStatus> {
  return apiFetch<CalendarStatus>("/auth/google/status");
}

export function listCalendars(): Promise<{ data: GoogleCalendar[] }> {
  return apiFetch<{ data: GoogleCalendar[] }>("/calendars");
}

export function selectCalendar(calendarId: string): Promise<{ selected_calendar_id: string }> {
  return apiFetch<{ selected_calendar_id: string }>(
    `/calendars/${encodeURIComponent(calendarId)}/select`,
    { method: "POST" },
  );
}

export function disconnectCalendar(): Promise<{ status: string }> {
  return apiFetch<{ status: string }>("/auth/google/disconnect", {
    method: "POST",
  });
}
