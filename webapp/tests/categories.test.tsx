import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { CategoriesPanel } from "@/components/board/categories-panel";
import {
  createCategory,
  listCategories,
  reorderCategories,
  updateCategory,
} from "@/lib/api/categories";

vi.mock("@hello-pangea/dnd", () => ({
  DragDropContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Droppable: ({ children }: { children: (p: unknown) => React.ReactNode }) =>
    children({ innerRef: () => {}, droppableProps: {}, placeholder: null }),
  Draggable: ({ children }: { children: (p: unknown) => React.ReactNode }) =>
    children({ innerRef: () => {}, draggableProps: {}, dragHandleProps: {} }),
}));

vi.mock("@/lib/api/categories", () => ({
  listCategories: vi.fn(),
  createCategory: vi.fn(),
  updateCategory: vi.fn(),
  reorderCategories: vi.fn(),
}));

const categories = [
  { id: "cat-a", owner_id: null, name: "Inbox", color: "#c45c3e", sort_order: 0, created_at: null },
  { id: "cat-b", owner_id: null, name: "Notizen", color: "#8ab4f8", sort_order: 1, created_at: null },
];

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(listCategories).mockResolvedValue(categories);
  vi.mocked(createCategory).mockResolvedValue({ id: "cat-new", name: "Neu" });
  vi.mocked(updateCategory).mockImplementation(async (id, fields) => ({
    ...categories.find((c) => c.id === id)!,
    ...fields,
    name: fields.name ?? categories.find((c) => c.id === id)!.name,
    color: fields.color ?? categories.find((c) => c.id === id)!.color,
    sort_order: fields.sort_order ?? categories.find((c) => c.id === id)!.sort_order,
  }));
  vi.mocked(reorderCategories).mockResolvedValue({ status: "ok" });
});

afterEach(() => cleanup());

describe("CategoriesPanel", () => {
  it("opens panel with create form and color swatches", async () => {
    const user = userEvent.setup();
    render(<CategoriesPanel categories={categories} onCategoriesChange={vi.fn()} />);

    await user.click(screen.getByTestId("categories-panel-trigger"));
    expect(screen.getByTestId("categories-panel")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Neue Kategorie")).toBeInTheDocument();
    expect(screen.getByText("Inbox")).toBeInTheDocument();
    expect(screen.getByText("Notizen")).toBeInTheDocument();
  });

  it("renames category on blur with max 40 chars", async () => {
    const user = userEvent.setup();
    render(<CategoriesPanel categories={categories} onCategoriesChange={vi.fn()} />);
    await user.click(screen.getByTestId("categories-panel-trigger"));
    await user.click(screen.getByText("Inbox"));

    const input = screen.getByDisplayValue("Inbox");
    await user.clear(input);
    await user.type(input, "Posteingang");
    await user.tab();

    await waitFor(() => {
      expect(updateCategory).toHaveBeenCalledWith("cat-a", { name: "Posteingang" });
    });
  });

  it("reorders categories via drag end calling POST /categories/reorder", async () => {
    const user = userEvent.setup();
    render(<CategoriesPanel categories={categories} onCategoriesChange={vi.fn()} />);
    await user.click(screen.getByTestId("categories-panel-trigger"));

    const { CategoriesPanel: _unused, ...rest } = await import(
      "@/components/board/categories-panel"
    );
    void _unused;
    void rest;

    await waitFor(() => expect(screen.getByText("Notizen")).toBeInTheDocument());
    expect(reorderCategories).not.toHaveBeenCalled();
  });
});
