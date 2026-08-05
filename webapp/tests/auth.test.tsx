import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { LoginForm, isSignupLockedError } from "@/app/login/login-form";
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
  { id: "cat-inbox", owner_id: null, name: "Inbox", color: null, sort_order: 0, created_at: null },
  { id: "cat-notes", owner_id: null, name: "Notizen", color: null, sort_order: 1, created_at: null },
  { id: "cat-links", owner_id: null, name: "Links", color: null, sort_order: 2, created_at: null },
  { id: "cat-tasks", owner_id: null, name: "Tasks", color: null, sort_order: 3, created_at: null },
  { id: "cat-termine", owner_id: null, name: "Termine", color: null, sort_order: 4, created_at: null },
];

beforeEach(() => {
  mockPush.mockReset();
  mockRefresh.mockReset();
  mockSearchParams = new URLSearchParams();
  sessionStorage.clear();
  vi.mocked(authClient.signIn.email).mockReset();
  vi.mocked(authClient.signUp.email).mockReset();
  vi.mocked(authClient.signOut).mockReset();
  vi.mocked(getCategories).mockResolvedValue(mockCategories);
  vi.mocked(getBoardItems).mockResolvedValue([]);
});

afterEach(() => {
  cleanup();
});

describe("isSignupLockedError envelope shapes", () => {
  it("detects flat message field", () => {
    expect(
      isSignupLockedError({ message: "SIGNUP_LOCKED", status: 409, statusText: "Conflict" }),
    ).toBe(true);
  });

  it("detects code field instead of message", () => {
    expect(isSignupLockedError({ code: "SIGNUP_LOCKED", status: 409 })).toBe(true);
  });

  it("detects nested body.message", () => {
    expect(isSignupLockedError({ status: 409, body: { message: "SIGNUP_LOCKED" } })).toBe(
      true,
    );
  });

  it("detects response-wrapped body.message", () => {
    expect(
      isSignupLockedError({
        status: 409,
        response: { body: { message: "SIGNUP_LOCKED" } },
      }),
    ).toBe(true);
  });

  it("detects json field variant", () => {
    expect(isSignupLockedError({ status: 409, json: { message: "SIGNUP_LOCKED" } })).toBe(
      true,
    );
  });

  it("detects plain string SIGNUP_LOCKED", () => {
    expect(isSignupLockedError("SIGNUP_LOCKED")).toBe(true);
  });

  it("detects deep stringify fallback for uncommon nesting", () => {
    expect(
      isSignupLockedError({ status: 409, data: { error: { reason: "SIGNUP_LOCKED" } } }),
    ).toBe(true);
  });

  it("detects nested body on circular refs without throwing", () => {
    const error: Record<string, unknown> = {
      status: 409,
      body: { message: "SIGNUP_LOCKED" },
    };
    error.self = error;
    expect(isSignupLockedError(error)).toBe(true);
  });

  it("returns false for null", () => {
    expect(isSignupLockedError(null)).toBe(false);
  });

  it("returns false for undefined", () => {
    expect(isSignupLockedError(undefined)).toBe(false);
  });

  it("returns false for empty object", () => {
    expect(isSignupLockedError({})).toBe(false);
  });

  it("returns false for INVALID_PASSWORD", () => {
    expect(isSignupLockedError({ message: "INVALID_PASSWORD" })).toBe(false);
  });

  it("returns false for status 500 without SIGNUP_LOCKED", () => {
    expect(isSignupLockedError({ status: 500, message: "Internal Server Error" })).toBe(false);
  });
});

describe("LoginPage", () => {
  it("shows Anmelden and Registrieren tabs with register always visible", () => {
    render(<LoginForm />);

    expect(screen.getByRole("tab", { name: "Anmelden" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Registrieren" })).toBeInTheDocument();
  });

  it("shows SIGNUP_LOCKED VOICE copy when registration is locked", async () => {
    vi.mocked(authClient.signUp.email).mockResolvedValue({
      data: null,
      error: { message: "SIGNUP_LOCKED", status: 409, statusText: "Conflict" },
    } as Awaited<ReturnType<typeof authClient.signUp.email>>);

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
    expect(mockPush).not.toHaveBeenCalled();
    expect(sessionStorage.getItem("pb.signup_locked")).toBe("1");
  });

  it("keeps SIGNUP_LOCKED copy sticky across remount via sessionStorage", async () => {
    sessionStorage.setItem("pb.signup_locked", "1");
    render(<LoginForm />);

    await waitFor(() => {
      expect(
        screen.getByText(
          "Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.",
        ),
      ).toBeInTheDocument();
    });
    expect(screen.getByRole("tab", { name: "Registrieren" })).toHaveAttribute(
      "data-state",
      "active",
    );
  });

  it("does not redirect on failed login error object", async () => {
    vi.mocked(authClient.signIn.email).mockResolvedValue({
      data: null,
      error: { message: "INVALID_PASSWORD", status: 401, statusText: "Unauthorized" },
    } as Awaited<ReturnType<typeof authClient.signIn.email>>);

    render(<LoginForm />);

    fireEvent.change(document.getElementById("login-email")!, {
      target: { value: "test@example.com" },
    });
    fireEvent.change(document.getElementById("login-password")!, {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Anmelden" }));

    await waitFor(() => {
      expect(screen.getByText("Anmeldung fehlgeschlagen.")).toBeInTheDocument();
    });
    expect(mockPush).not.toHaveBeenCalled();
  });

  it("redirects to / after successful login (HomeRedirect → welcome|board)", async () => {
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
      expect(mockPush).toHaveBeenCalledWith("/");
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
      expect(mockPush).toHaveBeenCalledWith("/");
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
