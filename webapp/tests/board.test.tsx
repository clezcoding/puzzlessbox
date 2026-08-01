import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";

import BoardPage from "@/app/board/page";
import { getCategories, getBoardItems } from "@/lib/api-client";
import { useSession } from "@/lib/auth-client";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn(), refresh: vi.fn() }),
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

vi.mock("@/lib/api-client", () => ({
  getCategories: vi.fn(),
  getBoardItems: vi.fn(),
}));

vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(),
  authClient: {
    signOut: vi.fn(),
  },
}));

const mockCategories = [
  { id: "cat-inbox", owner_id: null, name: "Inbox", created_at: null },
  { id: "cat-notes", owner_id: null, name: "Notizen", created_at: null },
  { id: "cat-links", owner_id: null, name: "Links", created_at: null },
  { id: "cat-tasks", owner_id: null, name: "Tasks", created_at: null },
  { id: "cat-termine", owner_id: null, name: "Termine", created_at: null },
];

const baseItem = {
  owner_id: "user-1",
  summary: "",
  type: "note",
  created_at: "2026-08-01T10:00:00Z",
  updated_at: "2026-08-01T10:00:00Z",
  deleted_at: null,
};

beforeEach(() => {
  vi.mocked(useSession).mockReturnValue({
    data: { user: { email: "test@example.com" } },
    isPending: false,
  } as ReturnType<typeof useSession>);
  vi.mocked(getCategories).mockResolvedValue(mockCategories);
});

afterEach(() => {
  cleanup();
});

describe("BoardPage", () => {
  it("renders 5 default categories from GET /categories", async () => {
    vi.mocked(getBoardItems).mockResolvedValue([]);

    render(<BoardPage />);

    await waitFor(() => {
      expect(screen.getByText("Inbox")).toBeInTheDocument();
      expect(screen.getByText("Notizen")).toBeInTheDocument();
      expect(screen.getByText("Links")).toBeInTheDocument();
      expect(screen.getByText("Tasks")).toBeInTheDocument();
      expect(screen.getByText("Termine")).toBeInTheDocument();
    });
  });

  it("renders only auto_saved and confirmed items, not draft", async () => {
    vi.mocked(getBoardItems).mockResolvedValue([
      {
        ...baseItem,
        id: "item-visible",
        category_id: "cat-inbox",
        status: "auto_saved",
        title: "Sichtbarer Eintrag",
      },
      {
        ...baseItem,
        id: "item-draft",
        category_id: "cat-inbox",
        status: "draft",
        title: "Draft Eintrag",
      },
    ]);

    render(<BoardPage />);

    await waitFor(() => {
      expect(screen.getByText("Sichtbarer Eintrag")).toBeInTheDocument();
    });
    expect(screen.queryByText("Draft Eintrag")).not.toBeInTheDocument();
  });

  it("shows Apollo empty PNG and VOICE copy for empty Inbox column", async () => {
    vi.mocked(getBoardItems).mockResolvedValue([]);

    render(<BoardPage />);

    await waitFor(() => {
      expect(
        screen.getByText(
          "Apollo hat noch nichts gefangen. Sende eine Nachricht, um den ersten Eintrag zu stashen.",
        ),
      ).toBeInTheDocument();
      const inboxImage = screen
        .getAllByRole("img")
        .find((img) => img.getAttribute("src") === "/apollo-empty-inbox.png");
      expect(inboxImage).toBeDefined();
    });
  });
});
