import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderHook } from "@testing-library/react";
import { toast } from "sonner";

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

import BoardPage from "@/app/board/page";
import {
  getBoardItems,
  getCategories,
  type BoardItem,
} from "@/lib/api-client";
import { useSession } from "@/lib/auth-client";
import {
  intervalWithJitter,
  POLL_INTERVAL_MS,
  useBoardPoll,
} from "@/lib/hooks/use-board-poll";
import { useSound } from "@/lib/hooks/use-sound";
import { TOAST_MESSAGE } from "@/components/board/new-item-feedback";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("next/dynamic", () => ({
  default: () => {
    const React = require("react");
    return function BoardDndStub({
      items,
    }: {
      items: Array<{ id: string; title: string }>;
    }) {
      return React.createElement(
        "div",
        { "data-testid": "board-dnd-stub" },
        items.map((item) =>
          React.createElement("div", { key: item.id }, item.title),
        ),
      );
    };
  },
}));

vi.mock("@/lib/hooks/use-media-query", () => ({
  useMediaQuery: () => false,
}));

vi.mock("@/components/board/categories-panel", () => ({
  CategoriesPanel: () => <div data-testid="categories-panel-stub" />,
}));

vi.mock("@/components/board/bulk-move-bar", () => ({
  BulkMoveBar: () => null,
}));

vi.mock("@/components/board/item-modal", () => ({
  ItemModal: () => null,
}));

vi.mock("@/components/board/mobile-category-sheet", () => ({
  MobileCategorySheet: () => null,
}));

vi.mock("next/image", () => ({
  default: ({ alt, src }: { alt?: string; src: string }) => (
    <img alt={alt ?? ""} src={src} />
  ),
}));

vi.mock("@/lib/api-client", () => ({
  getCategories: vi.fn(),
  getBoardItems: vi.fn(),
}));

vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(),
  authClient: { signOut: vi.fn() },
}));

const mockCategories = [
  {
    id: "cat-inbox",
    owner_id: null,
    name: "Inbox",
    color: null,
    sort_order: 0,
    created_at: null,
  },
];

const baseItem: BoardItem = {
  id: "item-1",
  owner_id: "user-1",
  category_id: "cat-inbox",
  status: "auto_saved",
  title: "Bestehender Eintrag",
  summary: "",
  type: "note",
  sort_order: 0,
  created_at: "2026-08-01T10:00:00Z",
  updated_at: "2026-08-01T10:00:00Z",
  deleted_at: null,
};

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  vi.spyOn(Math, "random").mockReturnValue(0.5);
  vi.mocked(useSession).mockReturnValue({
    data: { user: { email: "test@example.com" } },
    isPending: false,
  } as ReturnType<typeof useSession>);
  vi.mocked(getCategories).mockResolvedValue(mockCategories);
  vi.mocked(getBoardItems).mockResolvedValue([baseItem]);
  localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.clearAllMocks();
  vi.restoreAllMocks();
});

describe("useBoardPoll", () => {
  it("polls getBoardItems and getCategories every ~10s while enabled", async () => {
    const { unmount } = renderHook(() =>
      useBoardPoll({ enabled: true }),
    );

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(1);
      expect(getCategories).toHaveBeenCalledTimes(1);
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS);
    });

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(2);
      expect(getCategories).toHaveBeenCalledTimes(2);
    });

    unmount();
  });

  it("merges new items into existing board state", async () => {
    const onNewItems = vi.fn();
    const { result, unmount } = renderHook(() =>
      useBoardPoll({ enabled: true, onNewItems }),
    );

    await waitFor(() => {
      expect(result.current.items).toHaveLength(1);
    });

    vi.mocked(getBoardItems).mockResolvedValue([
      baseItem,
      {
        ...baseItem,
        id: "item-new",
        title: "Neuer Eintrag",
      },
    ]);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS);
    });

    await waitFor(() => {
      expect(result.current.items).toHaveLength(2);
      expect(result.current.items.some((item) => item.id === "item-new")).toBe(
        true,
      );
      expect(onNewItems).toHaveBeenCalledWith(["item-new"]);
    });

    unmount();
  });

  it("backs off 10s to 20s to 40s to 60s cap with jitter on errors", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0.5);
    vi.mocked(getBoardItems).mockRejectedValue(new Error("network"));

    const { unmount } = renderHook(() =>
      useBoardPoll({ enabled: true }),
    );

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(1);
    });

    const intervals = [20_000, 40_000, 60_000, 60_000];
    for (let i = 0; i < intervals.length; i += 1) {
      await act(async () => {
        vi.advanceTimersByTime(intervals[i]!);
      });
      await waitFor(() => {
        expect(getBoardItems).toHaveBeenCalledTimes(i + 2);
      });
    }

    unmount();
  });

  it("resets backoff to 10s after success", async () => {
    vi.mocked(getBoardItems)
      .mockRejectedValueOnce(new Error("fail"))
      .mockResolvedValue([baseItem]);

    const { unmount } = renderHook(() =>
      useBoardPoll({ enabled: true }),
    );

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(1);
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(2);
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 1.2);
    });

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(3);
    });

    unmount();
  });

  it("refresh triggers immediate fetch and resets backoff", async () => {
    vi.mocked(getBoardItems).mockRejectedValue(new Error("fail"));

    const { result, unmount } = renderHook(() =>
      useBoardPoll({ enabled: true }),
    );

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(1);
    });

    vi.mocked(getBoardItems).mockResolvedValue([baseItem]);

    await act(async () => {
      result.current.refresh();
    });

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(2);
      expect(result.current.offline).toBe(false);
    });

    unmount();
  });
});

describe("intervalWithJitter", () => {
  it("applies ±20% jitter around base interval", () => {
    vi.mocked(Math.random).mockReturnValue(0);
    expect(intervalWithJitter(0)).toBe(POLL_INTERVAL_MS * 0.8);
    vi.mocked(Math.random).mockReturnValue(1);
    expect(intervalWithJitter(0)).toBe(POLL_INTERVAL_MS * 1.2);
  });
});

describe("BoardPage poll integration", () => {
  it("shows offline banner with retry while keeping last data visible", async () => {
    render(<BoardPage />);

    await waitFor(() => {
      expect(screen.getByText("Bestehender Eintrag")).toBeInTheDocument();
    });

    vi.mocked(getBoardItems).mockRejectedValue(new Error("offline"));

    await act(async () => {
      await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 1.2);
    });

    await waitFor(() => {
      expect(
        screen.getByText("Keine Verbindung. Apollo sucht nach dem Signal…"),
      ).toBeInTheDocument();
      expect(screen.getByText("Bestehender Eintrag")).toBeInTheDocument();
    });
  });

  it("shows new-item toast when poll discovers a new item", async () => {
    render(<BoardPage />);

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalled();
    });

    vi.mocked(getBoardItems).mockResolvedValue([
      baseItem,
      { ...baseItem, id: "item-new", title: "Frisch gestasht" },
    ]);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 1.2);
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(TOAST_MESSAGE);
      expect(screen.getByText("Frisch gestasht")).toBeInTheDocument();
    });
  });

  it("manual refresh button triggers immediate fetch", async () => {
    render(<BoardPage />);

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(1);
    });

    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await user.click(screen.getByRole("button", { name: "Board aktualisieren" }));

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(2);
    });
  });

  it("keeps polling when document is hidden", async () => {
    Object.defineProperty(document, "visibilityState", {
      configurable: true,
      get: () => "hidden",
    });

    render(<BoardPage />);

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(1);
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 1.2);
    });

    await waitFor(() => {
      expect(getBoardItems).toHaveBeenCalledTimes(2);
    });
  });
});

describe("useSound", () => {
  it("defaults sound off and respects localStorage toggle", async () => {
    const { result, unmount } = renderHook(() => useSound());

    await waitFor(() => {
      expect(result.current.enabled).toBe(false);
    });

    act(() => {
      result.current.setEnabled(true);
    });

    expect(result.current.enabled).toBe(true);
    expect(localStorage.getItem("pb.sound")).toBe("true");

    unmount();
  });
});
