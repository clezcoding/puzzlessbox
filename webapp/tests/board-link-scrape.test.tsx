import { describe, it, expect, vi, afterEach } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";

import { BoardCard } from "@/components/board/board-card";
import type { BoardItem, Category } from "@/lib/api-client";

vi.mock("@hello-pangea/dnd", () => ({
  Draggable: ({
    children,
  }: {
    children: (provided: unknown, snapshot: { isDragging: boolean }) => React.ReactNode;
  }) =>
    children(
      {
        innerRef: () => {},
        draggableProps: { style: {} },
        dragHandleProps: {},
      },
      { isDragging: false },
    ),
}));

afterEach(() => cleanup());

const category: Category = {
  id: "cat-1",
  owner_id: null,
  name: "Links",
  color: null,
  sort_order: 2,
  created_at: null,
};

const baseLinkItem: BoardItem = {
  id: "link-1",
  owner_id: "owner-1",
  category_id: "cat-1",
  status: "confirmed",
  title: "Example page",
  summary: "https://example.com/some/long/path",
  type: "link",
  sort_order: 0,
  created_at: "2026-08-08T12:00:00.000Z",
  updated_at: "2026-08-08T12:00:00.000Z",
  deleted_at: null,
};

function renderLinkCard(item: BoardItem) {
  const onSelect = vi.fn();
  const onOpen = vi.fn();
  const onMove = vi.fn();

  render(
    <BoardCard
      item={item}
      accentColor="#c45c3e"
      index={0}
      isSelected={false}
      isNew={false}
      isMobile={false}
      categories={[category]}
      onSelect={onSelect}
      onOpen={onOpen}
      onMoveToCategory={onMove}
    />,
  );

  return { onSelect, onOpen, onMove };
}

describe("BoardCard link scrape states", () => {
  it("uses item.image for thumbnail src when scrape_status is ok (D-06)", () => {
    renderLinkCard({
      ...baseLinkItem,
      image: "https://cdn.example.com/og.png",
      scrape_status: "ok",
    });

    const img = document.querySelector("img[referrerpolicy='no-referrer']");
    expect(img).not.toBeNull();
    expect(img).toHaveAttribute("src", "https://cdn.example.com/og.png");
  });

  it("shows hostname meta from summary, not summary URL as image src", () => {
    renderLinkCard({
      ...baseLinkItem,
      image: null,
      scrape_status: "failed",
    });

    expect(document.querySelector("img")).toBeNull();
    expect(screen.getByText(/example\.com/)).toBeInTheDocument();
  });

  it.todo(
    "shows spinner affordance when scrape_status is pending or scraping (D-22)",
  );

  it.todo("never renders raw scrape_status code string in the DOM (D-20)");
});
