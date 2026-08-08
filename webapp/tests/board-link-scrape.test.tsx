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

const RAW_STATUS_TOKENS = ["pending", "scraping", "timed_out", "failed", "partial", "skipped"] as const;

function renderLinkCard(item: BoardItem) {
  const onSelect = vi.fn();
  const onOpen = vi.fn();
  const onMove = vi.fn();

  const view = render(
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

  return { onSelect, onOpen, onMove, ...view };
}

function expectNoRawStatusCopy(container: HTMLElement) {
  for (const token of RAW_STATUS_TOKENS) {
    expect(screen.queryByText(new RegExp(`\\b${token}\\b`, "i"))).toBeNull();
  }
  expect(container.textContent?.toLowerCase() ?? "").not.toMatch(
    /\b(pending|scraping|timed_out|failed|partial|skipped)\b/,
  );
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
    const { container } = renderLinkCard({
      ...baseLinkItem,
      image: null,
      scrape_status: "failed",
    });

    expect(document.querySelector("img")).toBeNull();
    expect(screen.getByText(/example\.com/)).toBeInTheDocument();
    expectNoRawStatusCopy(container);
  });

  it("shows spinner affordance when scrape_status is pending or scraping (D-22)", () => {
    const pending = renderLinkCard({
      ...baseLinkItem,
      scrape_status: "pending",
    });
    expect(pending.container.querySelector('[data-thumb-state="loading"]')).not.toBeNull();
    expect(pending.container.querySelector(".motion-safe\\:animate-spin")).not.toBeNull();

    cleanup();

    const scraping = renderLinkCard({
      ...baseLinkItem,
      scrape_status: "scraping",
    });
    expect(scraping.container.querySelector('[data-thumb-state="loading"]')).not.toBeNull();
    expect(scraping.container.querySelector(".motion-safe\\:animate-spin")).not.toBeNull();
  });

  it("never renders raw scrape_status code string in the DOM (D-20)", () => {
    for (const scrape_status of RAW_STATUS_TOKENS) {
      const { container } = renderLinkCard({
        ...baseLinkItem,
        scrape_status,
        image: scrape_status === "ok" ? "https://cdn.example.com/og.png" : null,
      });
      expectNoRawStatusCopy(container);
      cleanup();
    }
  });
});
