import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { CalendarWizard } from "@/components/settings/calendar-wizard";
import {
  disconnectCalendar,
  getCalendarStatus,
  listCalendars,
  selectCalendar,
  startCalendarConnect,
} from "@/lib/api/calendar";

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

let mockSearchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useSearchParams: () => mockSearchParams,
}));

vi.mock("next/image", () => ({
  default: ({ alt, src }: { alt?: string; src: string }) => (
    <img alt={alt ?? ""} src={src} />
  ),
}));

vi.mock("@/lib/api/calendar", () => ({
  startCalendarConnect: vi.fn(async () => {
    window.location.href = "https://accounts.google.com/o/oauth2/auth?mock=1";
  }),
  getCalendarStatus: vi.fn(),
  listCalendars: vi.fn(),
  selectCalendar: vi.fn(),
  disconnectCalendar: vi.fn(),
}));

const mockCalendars = {
  data: [
    { id: "cal-primary", summary: "Persönlich", primary: true },
    { id: "cal-work", summary: "Arbeit" },
  ],
};

beforeEach(() => {
  mockSearchParams = new URLSearchParams();
  vi.mocked(getCalendarStatus).mockResolvedValue({
    connected: false,
    selected_calendar_id: null,
  });
  vi.mocked(listCalendars).mockResolvedValue(mockCalendars);
  vi.mocked(selectCalendar).mockResolvedValue({ selected_calendar_id: "cal-primary" });
  vi.mocked(disconnectCalendar).mockResolvedValue({ status: "disconnected" });
  Object.defineProperty(window, "location", {
    configurable: true,
    value: { href: "" },
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("CalendarWizard", () => {
  it("shows apollo-empty-cal and Mit Google verbinden before connect", async () => {
    render(<CalendarWizard />);

    await waitFor(() => {
      expect(screen.getByAltText("Leerer Kalender")).toHaveAttribute(
        "src",
        "/apollo-empty-cal.png",
      );
      expect(
        screen.getByRole("button", { name: "Mit Google verbinden" }),
      ).toBeInTheDocument();
    });
  });

  it("starts calendar connect via apiFetch then redirects to Google", async () => {
    render(<CalendarWizard />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Mit Google verbinden" }),
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Mit Google verbinden" }));

    await waitFor(() => {
      expect(startCalendarConnect).toHaveBeenCalled();
    });
    expect(window.location.href).toBe(
      "https://accounts.google.com/o/oauth2/auth?mock=1",
    );
  });

  it("loads calendar list on step 2 after OAuth return", async () => {
    mockSearchParams = new URLSearchParams("step=2");
    vi.mocked(getCalendarStatus).mockResolvedValue({
      connected: true,
      selected_calendar_id: null,
    });

    render(<CalendarWizard />);

    await waitFor(() => {
      expect(screen.getByText("Kalender wählen")).toBeInTheDocument();
      expect(listCalendars).toHaveBeenCalled();
      expect(screen.getByLabelText("Persönlich")).toBeInTheDocument();
    });
  });

  it("selects calendar and completes connection", async () => {
    mockSearchParams = new URLSearchParams("step=2");
    vi.mocked(getCalendarStatus).mockResolvedValue({
      connected: true,
      selected_calendar_id: null,
    });

    render(<CalendarWizard />);

    await waitFor(() => {
      expect(screen.getByText("Kalender wählen")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Verbindung abschließen" }));

    await waitFor(() => {
      expect(selectCalendar).toHaveBeenCalledWith("cal-primary");
      expect(screen.getByText("Kalender verbunden")).toBeInTheDocument();
    });
  });

  it("shows disconnect confirm dialog and calls disconnect API", async () => {
    vi.mocked(getCalendarStatus).mockResolvedValue({
      connected: true,
      selected_calendar_id: "cal-primary",
    });
    vi.mocked(listCalendars).mockResolvedValue(mockCalendars);

    render(<CalendarWizard />);

    await waitFor(() => {
      expect(screen.getByText("Kalender verbunden")).toBeInTheDocument();
    });

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Trennen" }));

    await waitFor(() => {
      expect(
        screen.getByText(
          "Trennen: Google-Kalender trennen? Lokale Termine bleiben; Sync stoppt.",
        ),
      ).toBeInTheDocument();
    });

    await user.click(screen.getAllByRole("button", { name: "Trennen" }).at(-1)!);

    await waitFor(() => {
      expect(disconnectCalendar).toHaveBeenCalled();
      expect(
        screen.getByRole("button", { name: "Mit Google verbinden" }),
      ).toBeInTheDocument();
    });
  });
});
