import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent, cleanup } from "@testing-library/react";

import { LoginForm } from "@/app/login/login-form";
import { authClient } from "@/lib/auth-client";

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

beforeEach(() => {
  mockPush.mockReset();
  mockRefresh.mockReset();
  mockSearchParams = new URLSearchParams();
  vi.mocked(authClient.signIn.email).mockReset();
  vi.mocked(authClient.signUp.email).mockReset();
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
});
