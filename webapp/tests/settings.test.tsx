import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import SettingsPage from "@/app/settings/page";
import { AppearanceSection } from "@/app/settings/appearance";
import WelcomePage from "@/app/welcome/page";
import { HomeRedirect } from "@/app/home-redirect";
import { BoardHeader } from "@/components/board/board-header";
import { authClient, useSession } from "@/lib/auth-client";

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

const mockPush = vi.fn();
const mockReplace = vi.fn();
let mockSearchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace, refresh: vi.fn() }),
  useSearchParams: () => mockSearchParams,
}));

vi.mock("next/image", () => ({
  default: ({ alt, src }: { alt?: string; src: string }) => (
    <img alt={alt ?? ""} src={src} />
  ),
}));

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    signOut: vi.fn(),
    changePassword: vi.fn(),
  },
  useSession: vi.fn(),
}));

vi.mock("@/components/settings/calendar-wizard", () => ({
  CalendarWizard: () => <div data-testid="calendar-wizard-stub">Calendar Wizard</div>,
}));

beforeEach(() => {
  mockPush.mockReset();
  mockReplace.mockReset();
  mockSearchParams = new URLSearchParams();
  vi.mocked(useSession).mockReturnValue({
    data: { user: { email: "long.email.address@example.com" } },
    isPending: false,
  } as ReturnType<typeof useSession>);
  vi.mocked(authClient.changePassword).mockResolvedValue({} as never);
  vi.mocked(authClient.signOut).mockResolvedValue({} as never);
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
});

describe("SettingsPage", () => {
  it("renders Account, Google Calendar, and Appearance sections", async () => {
    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Account" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Google Calendar" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Darstellung" })).toBeInTheDocument();
    });
  });

  it("shows email with truncate and password change + logout in Account", async () => {
    render(<SettingsPage />);

    await waitFor(() => {
      const email = screen.getByTitle("long.email.address@example.com");
      expect(email).toHaveClass("truncate");
      expect(screen.getByLabelText("Aktuelles Passwort")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Abmelden" })).toBeInTheDocument();
    });
  });

  it("calls authClient.changePassword and shows success toast on submit", async () => {
    const { toast } = await import("sonner");
    render(<SettingsPage />);

    fireEvent.change(screen.getByLabelText("Aktuelles Passwort"), {
      target: { value: "old-pass-123" },
    });
    fireEvent.change(screen.getByLabelText("Neues Passwort"), {
      target: { value: "new-pass-1234" },
    });
    fireEvent.change(screen.getByLabelText("Passwort bestätigen"), {
      target: { value: "new-pass-1234" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Passwort ändern" }));

    await waitFor(() => {
      expect(authClient.changePassword).toHaveBeenCalledWith({
        currentPassword: "old-pass-123",
        newPassword: "new-pass-1234",
      });
      expect(toast.success).toHaveBeenCalledWith("Passwort geändert.");
    });
  });

  it("Appearance defaults sound off and offers theme modes", async () => {
    render(<AppearanceSection />);

    expect(screen.getByRole("button", { name: "System" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hell" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dunkel" })).toBeInTheDocument();
    expect(screen.getByLabelText("Sound bei neuem Eintrag")).not.toBeChecked();
  });

  it("theme toggle in board header updates document class", async () => {
    document.documentElement.classList.remove("dark");
    render(<BoardHeader userEmail="test@example.com" />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Darstellung umschalten" }));

    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });
});

describe("Welcome flow", () => {
  it("first login routes to welcome then board and sets pb.welcome.seen", async () => {
    render(<WelcomePage />);

    await waitFor(() => {
      expect(
        screen.getByText("Hallo, ich bin Apollo. Lass uns das Chaos ordnen."),
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Los geht's" }));

    await waitFor(() => {
      expect(window.localStorage.getItem("pb.welcome.seen")).toBe("true");
      expect(mockPush).toHaveBeenCalledWith("/board");
    });
  });

  it("subsequent home visit goes directly to board", async () => {
    window.localStorage.setItem("pb.welcome.seen", "true");
    render(<HomeRedirect />);

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/board");
    });
  });

  it("?next= wins over welcome redirect", async () => {
    mockSearchParams = new URLSearchParams("next=/settings");
    render(<HomeRedirect />);

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/settings");
    });
  });
});
