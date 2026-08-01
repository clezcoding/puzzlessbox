import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { LoginForm } from "@/app/login/login-form";
import BoardPage from "@/app/board/page";
import { BoardHeader } from "@/components/board/board-header";
import { getBoardItems, getCategories } from "@/lib/api-client";
import { authClient, useSession } from "@/lib/auth-client";

const mockPush = vi.fn();
const mockRefresh = vi.fn();
let mockSearchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, refresh: mockRefresh, replace: vi.fn() }),
  useSearchParams: () => mockSearchParams,
}));

vi.mock("next/image", () => ({
  default: ({
    alt,
    src,
  }: {
    alt?: string;
    src: string | { src: string };
  }) => (
    <img
      alt={alt ?? ""}
      src={typeof src === "string" ? src : src.src}
    />
  ),
}));

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    signIn: { email: vi.fn() },
    signUp: { email: vi.fn() },
    signOut: vi.fn(),
  },
  useSession: vi.fn(),
}));

vi.mock("@/lib/api-client", () => ({
  getCategories: vi.fn(),
  getBoardItems: vi.fn(),
}));

const mockCategories = [
  { id: "cat-inbox", owner_id: null, name: "Inbox", created_at: null },
  { id: "cat-notes", owner_id: null, name: "Notizen", created_at: null },
  { id: "cat-links", owner_id: null, name: "Links", created_at: null },
  { id: "cat-tasks", owner_id: null, name: "Tasks", created_at: null },
  { id: "cat-termine", owner_id: null, name: "Termine", created_at: null },
];

beforeEach(() => {
  mockPush.mockReset();
  mockRefresh.mockReset();
  mockSearchParams = new URLSearchParams();
  vi.mocked(authClient.signIn.email).mockReset();
  vi.mocked(authClient.signUp.email).mockReset();
  vi.mocked(authClient.signOut).mockReset();
  vi.mocked(getCategories).mockResolvedValue(mockCategories);
  vi.mocked(getBoardItems).mockResolvedValue([]);
});

afterEach(() => {
  cleanup();
});

describe("LoginPage", () => {
  it("shows Anmelden and Registrieren tabs with register always visible", () => {
    render(<LoginForm />);

    expect(screen.getByRole("tab", { name: "Anmelden" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Registrieren" })).toBeInTheDocument();
  });

  it("shows SIGNUP_LOCKED VOICE copy when registration is locked", async () => {
    vi.mocked(authClient.signUp.email).mockRejectedValue({
      message: "SIGNUP_LOCKED",
    });

    render(<LoginForm />);

    fireEvent.click(screen.getByRole("tab", { name: "Registrieren" }));
    await waitFor(() => {
      expect(document.getElementById("register-email")).toBeTruthy();
    });
    fireEvent.change(document.getElementById("register-email")!, {
      target: { value: "new@example.com" },
    });
    fireEvent.change(document.getElementById("register-password")!, {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Konto anlegen" }));

    await waitFor(() => {
      expect(
        screen.getByText(
          "Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.",
        ),
      ).toBeInTheDocument();
    });
  });

  it("redirects to /board after successful login", async () => {
    vi.mocked(authClient.signIn.email).mockResolvedValue({
      data: { user: { email: "test@example.com" } },
    } as Awaited<ReturnType<typeof authClient.signIn.email>>);

    render(<LoginForm />);

    fireEvent.change(document.getElementById("login-email")!, {
      target: { value: "test@example.com" },
    });
    fireEvent.change(document.getElementById("login-password")!, {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Anmelden" }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/board");
    });
  });

  it("redirects to safe ?next= path after successful login", async () => {
    mockSearchParams = new URLSearchParams("next=/settings");
    vi.mocked(authClient.signIn.email).mockResolvedValue({
      data: { user: { email: "test@example.com" } },
    } as Awaited<ReturnType<typeof authClient.signIn.email>>);

    render(<LoginForm />);

    fireEvent.change(document.getElementById("login-email")!, {
      target: { value: "test@example.com" },
    });
    fireEvent.change(document.getElementById("login-password")!, {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Anmelden" }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/settings");
    });
  });

  it("rejects absolute ?next= URLs on login success (open-redirect guard)", async () => {
    mockSearchParams = new URLSearchParams("next=https://evil.com");
    vi.mocked(authClient.signIn.email).mockResolvedValue({
      data: { user: { email: "test@example.com" } },
    } as Awaited<ReturnType<typeof authClient.signIn.email>>);

    render(<LoginForm />);

    fireEvent.change(document.getElementById("login-email")!, {
      target: { value: "test@example.com" },
    });
    fireEvent.change(document.getElementById("login-password")!, {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Anmelden" }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/board");
    });
  });
});

describe("Session survival", () => {
  it("keeps session after router.refresh()", async () => {
    const session = { user: { email: "test@example.com" } };
    vi.mocked(useSession).mockReturnValue({
      data: session,
      isPending: false,
    } as ReturnType<typeof useSession>);

    render(<BoardPage />);

    await waitFor(() => {
      expect(screen.getByText("Inbox")).toBeInTheDocument();
    });

    mockRefresh();
    expect(screen.getByText("Inbox")).toBeInTheDocument();
  });
});

describe("BoardHeader", () => {
  it("logs out via avatar menu and redirects to /login", async () => {
    const user = userEvent.setup();
    vi.mocked(authClient.signOut).mockResolvedValue(undefined);

    render(<BoardHeader userEmail="test@example.com" onRefresh={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Konto-Menü" }));
    await user.click(await screen.findByRole("menuitem", { name: "Abmelden" }));

    await waitFor(() => {
      expect(authClient.signOut).toHaveBeenCalled();
      expect(mockPush).toHaveBeenCalledWith("/login");
    });
  });

  it("shows user email with truncate and title tooltip", async () => {
    const user = userEvent.setup();
    const longEmail = "very.long.email.address@example.com";

    render(<BoardHeader userEmail={longEmail} onRefresh={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Konto-Menü" }));

    const emailEl = await screen.findByTitle(longEmail);
    expect(emailEl).toHaveClass("truncate");
    expect(emailEl).toHaveTextContent(longEmail);
  });
});
