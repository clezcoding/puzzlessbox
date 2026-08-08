import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { toast } from "sonner";

import { ItemModal } from "@/components/board/item-modal";
import { getCalendarStatus } from "@/lib/api/calendar";
import { rescrapeLink } from "@/lib/api/links";
import { deleteItem, restoreItem, updateItem } from "@/lib/api/items";

vi.mock("sonner", () => ({
  toast: Object.assign(vi.fn(), {
    success: vi.fn(),
    error: vi.fn(),
  }),
}));

vi.mock("next/image", () => ({
  default: ({ alt, src }: { alt?: string; src: string }) => (
    <img alt={alt ?? ""} src={src} />
  ),
}));

vi.mock("@/lib/api/items", () => ({
  updateItem: vi.fn(),
  deleteItem: vi.fn(),
  restoreItem: vi.fn(),
}));

vi.mock("@/lib/api/links", () => ({
  rescrapeLink: vi.fn(),
}));

vi.mock("@/lib/api/calendar", () => ({
  getCalendarStatus: vi.fn(),
}));

const categories = [
  { id: "cat-a", owner_id: null, name: "Inbox", color: null, sort_order: 0, created_at: null },
];

const item = {
  id: "item-1",
  owner_id: "user-1",
  category_id: "cat-a",
  status: "auto_saved",
  title: "Test Item",
  summary: "Body text",
  type: "note",
  sort_order: 0,
  created_at: "2026-08-01T10:00:00Z",
  updated_at: "2026-08-01T10:00:00Z",
  deleted_at: null,
};

const linkItem = {
  ...item,
  id: "item-link",
  type: "link",
  title: "Link Title",
  summary: "https://example.com",
  image: "https://example.com/og.png",
  scrape_status: "failed",
};

const eventItem = {
  ...item,
  id: "item-event",
  type: "event",
  google_event_id: null,
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(updateItem).mockResolvedValue({ ok: true });
  vi.mocked(deleteItem).mockResolvedValue(undefined);
  vi.mocked(restoreItem).mockResolvedValue({ id: "item-1", status: "restored" });
  vi.mocked(rescrapeLink).mockResolvedValue({ id: "item-link", scrape_status: "pending" });
  vi.mocked(getCalendarStatus).mockResolvedValue({
    connected: true,
    selected_calendar_id: "primary",
  });
});

afterEach(() => cleanup());

describe("ItemModal", () => {
  it("opens centered modal with dimmed overlay", () => {
    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );
    expect(screen.getByTestId("item-modal")).toBeInTheDocument();
    expect(screen.getByText("Eintrag bearbeiten")).toBeInTheDocument();
  });

  it("autosaves title on blur without save button", async () => {
    const user = userEvent.setup();
    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    const input = screen.getByLabelText("Titel");
    await user.clear(input);
    await user.type(input, "Neuer Titel");
    await user.tab();

    await waitFor(() => {
      expect(updateItem).toHaveBeenCalled();
    });
    expect(screen.queryByRole("button", { name: /speichern/i })).not.toBeInTheDocument();
  });

  it("shows autosave error toast on failure", async () => {
    vi.mocked(updateItem).mockRejectedValueOnce(new Error("fail"));
    const user = userEvent.setup();
    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    await user.click(screen.getByLabelText("Titel"));
    await user.tab();

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Speichern hakte. Versuch's gleich nochmal.",
      );
    });
  });

  it("soft-deletes with undo toast and no confirm dialog", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const onDeleted = vi.fn();
    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={onClose}
        onDeleted={onDeleted}
        onUpdated={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Verstauen" }));

    await waitFor(() => {
      expect(deleteItem).toHaveBeenCalledWith("item-1");
      expect(onClose).toHaveBeenCalled();
      expect(toast).toHaveBeenCalledWith(
        "Eintrag verstaut.",
        expect.objectContaining({
          action: expect.objectContaining({ label: "Rückgängig" }),
        }),
      );
    });
    expect(screen.queryByText(/unwiderruflich/i)).not.toBeInTheDocument();
  });

  it("restores item when undo clicked within toast", async () => {
    const user = userEvent.setup();
    let undoFn: (() => void) | undefined;
    vi.mocked(toast).mockImplementation((_msg, opts) => {
      undoFn = (opts as { action?: { onClick: () => void } })?.action?.onClick;
      return 0;
    });

    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Verstauen" }));
    await waitFor(() => expect(undoFn).toBeDefined());
    undoFn?.();
    await waitFor(() => expect(restoreItem).toHaveBeenCalledWith("item-1"));
  });

  it("shows type-change warning dialog", async () => {
    const user = userEvent.setup();
    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: /Typ:/ }));
    await user.click(screen.getByRole("menuitem", { name: "task" }));

    expect(
      screen.getByText("Typ ändern? Manche Felder gehen verloren."),
    ).toBeInTheDocument();
  });

  it("shows OG preview block for link type", () => {
    render(
      <ItemModal
        item={linkItem}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );
    expect(screen.getByTestId("og-preview")).toBeInTheDocument();
    expect(screen.getByText("Link Title")).toBeInTheDocument();
  });

  it("closes via X button and flushes pending autosave", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <ItemModal
        item={item}
        categories={categories}
        open
        onClose={onClose}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    const input = screen.getByLabelText("Titel");
    await user.clear(input);
    await user.type(input, "Changed");
    await user.click(screen.getByRole("button", { name: "Schließen" }));

    await waitFor(() => {
      expect(updateItem).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });

  it("shows 412 conflict panel with three CTAs", async () => {
    const user = userEvent.setup();
    const onUpdated = vi.fn();

    async function triggerConflict() {
      vi.mocked(updateItem).mockResolvedValueOnce({
        ok: false,
        conflict: {
          remote_state: {
            title: "Remote Title",
            starts_at: "2026-08-02T10:00:00Z",
            ends_at: "2026-08-02T11:00:00Z",
          },
        },
      });
      const input = screen.getByLabelText("Titel");
      await user.clear(input);
      await user.type(input, "Local Title");
      await user.tab();
      await waitFor(() => {
        expect(screen.getByTestId("conflict-panel")).toBeInTheDocument();
      });
    }

    render(
      <ItemModal
        item={{ ...item, type: "event" }}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={onUpdated}
      />,
    );

    await triggerConflict();
    expect(screen.getByRole("button", { name: "Übernehmen" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Behalten" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Abbrechen" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Abbrechen" }));
    expect(screen.queryByTestId("conflict-panel")).not.toBeInTheDocument();

    await triggerConflict();
    vi.mocked(updateItem).mockResolvedValueOnce({ ok: true });
    await user.click(screen.getByRole("button", { name: "Behalten" }));
    await waitFor(() =>
      expect(toast.success).toHaveBeenCalledWith("Eintrag gesichert."),
    );

    await triggerConflict();
    await user.click(screen.getByRole("button", { name: "Übernehmen" }));
    await waitFor(() => expect(onUpdated).toHaveBeenCalled());
  });

  it("shows scrape retry CTA with German label for failed links", async () => {
    const user = userEvent.setup();
    render(
      <ItemModal
        item={linkItem}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    expect(screen.getByText("Vorschau fehlgeschlagen")).toBeInTheDocument();
    const retry = screen.getByRole("button", { name: "Vorschau erneut laden" });
    await user.click(retry);
    await waitFor(() => expect(rescrapeLink).toHaveBeenCalledWith("item-link"));
    expect(toast.error).not.toHaveBeenCalled();
  });

  it("toasts only on manual scrape retry failure", async () => {
    vi.mocked(rescrapeLink).mockRejectedValueOnce(new Error("fail"));
    const user = userEvent.setup();
    render(
      <ItemModal
        item={linkItem}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Vorschau erneut laden" }));
    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith("Vorschau konnte nicht neu geladen werden."),
    );
  });

  it("shows Google sync CTA when calendar connected and event unsynced", async () => {
    const user = userEvent.setup();
    render(
      <ItemModal
        item={eventItem}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Mit Google synchronisieren" })).toBeInTheDocument(),
    );
    await user.click(screen.getByRole("button", { name: "Mit Google synchronisieren" }));
    await waitFor(() => expect(updateItem).toHaveBeenCalled());
    expect(toast.error).not.toHaveBeenCalled();
  });

  it("uses native img with no-referrer in OG preview", () => {
    render(
      <ItemModal
        item={linkItem}
        categories={categories}
        open
        onClose={vi.fn()}
        onDeleted={vi.fn()}
        onUpdated={vi.fn()}
      />,
    );
    const img = screen.getByTestId("og-preview").querySelector("img");
    expect(img).not.toBeNull();
    expect(img).toHaveAttribute("referrerPolicy", "no-referrer");
    expect(img).toHaveAttribute("src", "https://example.com/og.png");
  });
});
