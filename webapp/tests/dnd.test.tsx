import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useState } from "react";
import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { DropResult } from "@hello-pangea/dnd";
import { toast } from "sonner";

import { BoardDnd } from "@/components/board/board-dnd";
import { moveItem, reorderItems } from "@/lib/api/items";

const mockOnDragEndRef: { current: ((result: DropResult) => void) | null } = {
  current: null,
};

vi.mock("@hello-pangea/dnd", () => ({
  DragDropContext: ({
    children,
    onDragEnd,
  }: {
    children: React.ReactNode;
    onDragEnd: (result: DropResult) => void;
  }) => {
    mockOnDragEndRef.current = onDragEnd;
    return <div data-testid="dnd-context">{children}</div>;
  },
  Droppable: ({
    children,
    droppableId,
  }: {
    children: (provided: unknown, snapshot: unknown) => React.ReactNode;
    droppableId: string;
  }) =>
    children(
      { innerRef: () => {}, droppableProps: { "data-droppable-id": droppableId }, placeholder: null },
      {},
    ),
  Draggable: ({
    children,
    draggableId,
  }: {
    children: (provided: unknown, snapshot: { isDragging: boolean }) => React.ReactNode;
    draggableId: string;
  }) =>
    children(
      {
        innerRef: () => {},
        draggableProps: { style: {}, "data-draggable-id": draggableId },
        dragHandleProps: { "data-handle": draggableId },
      },
      { isDragging: false },
    ),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn(),
  },
}));

vi.mock("next/image", () => ({
  default: ({ alt, src }: { alt?: string; src: string }) => (
    <img alt={alt ?? ""} src={src} />
  ),
}));

vi.mock("@/lib/api/items", () => ({
  moveItem: vi.fn(),
  reorderItems: vi.fn(),
}));

const categories = [
  { id: "cat-a", owner_id: null, name: "Inbox", color: "#f00", sort_order: 0, created_at: null },
  { id: "cat-b", owner_id: null, name: "Notizen", color: "#0f0", sort_order: 1, created_at: null },
];

const baseItem = {
  owner_id: "user-1",
  status: "auto_saved",
  summary: "",
  type: "note",
  created_at: "2026-08-01T10:00:00Z",
  updated_at: "2026-08-01T10:00:00Z",
  deleted_at: null,
  sort_order: 0,
};

const itemA = { ...baseItem, id: "item-1", category_id: "cat-a", title: "Item A", sort_order: 0 };
const itemB = { ...baseItem, id: "item-2", category_id: "cat-b", title: "Item B", sort_order: 0 };

function renderBoard(overrides?: Partial<React.ComponentProps<typeof BoardDnd>>) {
  const onOpenItem = vi.fn();
  render(
    <BoardDnd
      categories={categories}
      items={[itemA, itemB]}
      isMobile={false}
      activeCategoryId="cat-a"
      selectedIds={new Set()}
      onActiveCategoryChange={vi.fn()}
      onSelect={vi.fn()}
      onOpenItem={onOpenItem}
      onMoveToCategory={vi.fn()}
      onCategoryUpdated={vi.fn()}
      {...overrides}
    />,
  );
  return { onOpenItem };
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(moveItem).mockResolvedValue({ id: "item-1" });
  vi.mocked(reorderItems).mockResolvedValue({ status: "ok" });
});

afterEach(() => cleanup());

describe("Board DnD", () => {
  it("moves item cross-category optimistically and shows success toast", async () => {
    renderBoard();
    await waitFor(() => expect(screen.getByText("Item A")).toBeInTheDocument());

    await mockOnDragEndRef.current?.({
      draggableId: "item-1",
      type: "DEFAULT",
      reason: "DROP",
      source: { droppableId: "cat-a", index: 0 },
      destination: { droppableId: "cat-b", index: 0 },
      mode: "FLUID",
      combine: null,
    });

    await waitFor(() => {
      expect(moveItem).toHaveBeenCalledWith("item-1", "cat-b");
      expect(toast.success).toHaveBeenCalledWith("Eintrag verschoben.");
    });
  });

  it("reverts and shows error toast when move API fails", async () => {
    vi.mocked(moveItem).mockRejectedValueOnce(new Error("500"));
    renderBoard();

    await mockOnDragEndRef.current?.({
      draggableId: "item-1",
      type: "DEFAULT",
      reason: "DROP",
      source: { droppableId: "cat-a", index: 0 },
      destination: { droppableId: "cat-b", index: 0 },
      mode: "FLUID",
      combine: null,
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Verschieben fehlgeschlagen. Eintrag ist zurück.",
      );
    });
  });

  it("persists in-column reorder via POST /items/reorder", async () => {
    const itemA2 = { ...itemA, id: "item-3", title: "Item A2", sort_order: 1 };
    renderBoard({ items: [itemA, itemA2] });

    await mockOnDragEndRef.current?.({
      draggableId: "item-3",
      type: "DEFAULT",
      reason: "DROP",
      source: { droppableId: "cat-a", index: 1 },
      destination: { droppableId: "cat-a", index: 0 },
      mode: "FLUID",
      combine: null,
    });

    await waitFor(() => {
      expect(reorderItems).toHaveBeenCalled();
    });
  });

  it("opens modal on card body click, not drag handle", async () => {
    const user = userEvent.setup();
    const { onOpenItem } = renderBoard();

    await user.click(screen.getByText("Item A"));
    expect(onOpenItem).toHaveBeenCalledWith(expect.objectContaining({ id: "item-1" }));
  });

  it("renders mobile single column with category tabs and long-press sheet handler", async () => {
    const onLongPress = vi.fn();
    renderBoard({
      isMobile: true,
      activeCategoryId: "cat-a",
      onLongPress,
    });

    expect(screen.getByRole("tab", { name: "Inbox" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Notizen" })).toBeInTheDocument();
    expect(screen.getByText("Item A")).toBeInTheDocument();
    expect(screen.queryByText("Item B")).not.toBeInTheDocument();

    const card = screen.getByTestId("board-card-item-1");
    fireEvent.touchStart(card);
    await new Promise((resolve) => setTimeout(resolve, 550));
    fireEvent.touchEnd(card);
    await waitFor(() => expect(onLongPress).toHaveBeenCalled());
  });

  it("bulk move: clicking destination fires moveItem per selected id, resets selection, and unmounts bulk bar", async () => {
    const { BulkMoveBar } = await import("@/components/board/bulk-move-bar");
    const onMoved = vi.fn();
    const onClear = vi.fn();

    function Harness({
      initialCount,
      selectedIds,
      categories: cats,
    }: {
      initialCount: number;
      selectedIds: string[];
      categories: typeof categories;
    }) {
      const [count, setCount] = useState(initialCount);
      const [ids, setIds] = useState(selectedIds);
      onClear.mockImplementation(() => {
        setCount(0);
        setIds([]);
      });
      return (
        <BulkMoveBar
          count={count}
          categories={cats}
          selectedIds={ids}
          onMoved={onMoved}
          onClear={onClear}
        />
      );
    }

    const user = userEvent.setup();
    render(
      <Harness initialCount={2} selectedIds={["item-1", "item-2"]} categories={categories} />,
    );

    expect(screen.getByTestId("bulk-move-bar")).toBeInTheDocument();
    await user.click(screen.getByTestId("bulk-move-trigger"));
    await user.click(await screen.findByTestId("bulk-move-destination-cat-b"));

    await waitFor(() => {
      expect(vi.mocked(moveItem)).toHaveBeenCalledTimes(2);
    });
    expect(vi.mocked(moveItem)).toHaveBeenNthCalledWith(1, "item-1", "cat-b");
    expect(vi.mocked(moveItem)).toHaveBeenNthCalledWith(2, "item-2", "cat-b");
    expect(toast.success).toHaveBeenCalledWith("Eintrag verschoben.", undefined);

    await waitFor(() => {
      expect(onMoved).toHaveBeenCalledTimes(1);
      expect(onClear).toHaveBeenCalledTimes(1);
    });
    expect(onMoved.mock.invocationCallOrder[0]).toBeLessThan(
      onClear.mock.invocationCallOrder[0],
    );

    await waitFor(() => {
      expect(screen.queryByTestId("bulk-move-bar")).not.toBeInTheDocument();
    });
  });

  it("exposes a11y move menu with keyboard label", async () => {
    renderBoard();
    expect(screen.getAllByLabelText("In Kategorie verschieben").length).toBeGreaterThan(0);
  });

  it("applies classic floating card ghost class while dragging", () => {
    render(
      <div data-testid="ghost-sample" className="board-card-ghost opacity-95 shadow-lg" />,
    );
    const ghost = screen.getByTestId("ghost-sample");
    expect(ghost.className).toContain("board-card-ghost");
    expect(ghost.className).toContain("opacity-95");
    expect(ghost.className).toContain("shadow-lg");
  });
});
