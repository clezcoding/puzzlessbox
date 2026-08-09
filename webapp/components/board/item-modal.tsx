"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import type { BoardItem, Category, ConflictDetails } from "@/lib/api-client";
import { getBoardItems } from "@/lib/api-client";
import { getCalendarStatus } from "@/lib/api/calendar";
import { rescrapeLink } from "@/lib/api/links";
import { deleteItem, restoreItem, updateItem } from "@/lib/api/items";
import { useItemAutosave } from "@/lib/hooks/use-item-autosave";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const ITEM_TYPES = ["note", "link", "task", "event"] as const;

const SCRAPE_STATUS_LABELS: Record<string, string> = {
  pending: "Vorschau wird geladen…",
  scraping: "Vorschau wird geladen…",
  ok: "Vorschau bereit",
  partial: "Vorschau unvollständig",
  timed_out: "Vorschau fehlgeschlagen",
  failed: "Vorschau fehlgeschlagen",
  skipped: "Vorschau übersprungen",
};

const SCRAPE_RETRY_STATUSES = new Set(["failed", "timed_out", "partial"]);
const SCRAPE_TERMINAL_STATUSES = new Set([
  "ok",
  "partial",
  "failed",
  "timed_out",
  "skipped",
]);

function scrapeStatusLabel(status: string | null | undefined): string | null {
  if (!status) return null;
  return SCRAPE_STATUS_LABELS[status] ?? "Vorschau wird geladen…";
}

async function sleep(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

type ItemModalProps = {
  item: BoardItem | null;
  categories: Category[];
  open: boolean;
  onClose: () => void;
  onDeleted: (id: string) => void;
  onUpdated: (item: BoardItem) => void;
};

export function ItemModal({
  item,
  categories,
  open,
  onClose,
  onDeleted,
  onUpdated,
}: ItemModalProps) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [url, setUrl] = useState("");
  const [itemType, setItemType] = useState("note");
  const [categoryId, setCategoryId] = useState("");
  const [pendingType, setPendingType] = useState<string | null>(null);
  const [conflict, setConflict] = useState<ConflictDetails | null>(null);
  const [ogBroken, setOgBroken] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState<string | null>(null);
  const [rescrapePending, setRescrapePending] = useState(false);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [syncPending, setSyncPending] = useState(false);
  const { pending, scheduleSave, saveOnBlur, flush, saveWithForce } =
    useItemAutosave(item?.id ?? "");

  useEffect(() => {
    if (!item) return;
    setTitle(item.title);
    // Links: summary is URL (board VIEW); Notizen empty — body ignored server-side for links.
    setBody(item.type === "link" ? "" : item.summary);
    setUrl(item.type === "link" ? item.summary : "");
    setItemType(item.type);
    setCategoryId(item.category_id);
    setConflict(null);
    setOgBroken(false);
    setScrapeStatus(item.scrape_status ?? null);
  }, [item]);

  useEffect(() => {
    if (!open || item?.type !== "event") {
      setCalendarConnected(false);
      return;
    }
    void getCalendarStatus()
      .then((status) => {
        setCalendarConnected(
          status.connected && Boolean(status.selected_calendar_id),
        );
      })
      .catch(() => setCalendarConnected(false));
  }, [open, item?.type, item?.id]);

  if (!item) return null;

  const showScrapeRetry =
    itemType === "link" && scrapeStatus && SCRAPE_RETRY_STATUSES.has(scrapeStatus);
  const showSyncMiss =
    itemType === "event" && !item.google_event_id;
  const scrapeLabel = scrapeStatusLabel(scrapeStatus);

  async function handleClose() {
    await flush();
    onClose();
  }

  async function handleTitleBlur() {
    const result = await saveOnBlur({ title });
    if (!result.ok && "conflict" in result) {
      setConflict(result.conflict);
      return;
    }
    onUpdated({ ...item!, title });
  }

  async function handleBodyBlur() {
    const fields = itemType === "link" ? { url, body } : { body };
    const result = await saveOnBlur(fields);
    if (!result.ok && "conflict" in result) {
      setConflict(result.conflict);
    }
  }

  async function handleRescrape() {
    setRescrapePending(true);
    try {
      const result = await rescrapeLink(item!.id);
      setScrapeStatus(result.scrape_status);
      let latest = result.scrape_status;
      for (let i = 0; i < 24 && !SCRAPE_TERMINAL_STATUSES.has(latest); i++) {
        if (i > 0) await sleep(500);
        const items = await getBoardItems();
        const updated = items.find((row) => row.id === item!.id);
        if (!updated) break;
        latest = updated.scrape_status ?? latest;
        setScrapeStatus(latest);
        if (SCRAPE_TERMINAL_STATUSES.has(latest)) {
          setTitle(updated.title);
          setOgBroken(false);
          onUpdated({
            ...item!,
            title: updated.title,
            summary: updated.summary,
            image: updated.image,
            scrape_status: latest,
          });
          break;
        }
      }
    } catch {
      toast.error("Vorschau konnte nicht neu geladen werden.");
    } finally {
      setRescrapePending(false);
    }
  }

  async function handleGoogleSync() {
    setSyncPending(true);
    try {
      const result = await updateItem(item!.id, { title });
      if (!result.ok && "conflict" in result) {
        setConflict(result.conflict);
        return;
      }
      onUpdated({ ...item!, title });
    } catch {
      toast.error("Synchronisation mit Google fehlgeschlagen.");
    } finally {
      setSyncPending(false);
    }
  }

  async function handleSoftDelete() {
    await flush();
    await deleteItem(item!.id);
    onDeleted(item!.id);
    onClose();
    toast("Eintrag verstaut.", {
      duration: 5000,
      action: {
        label: "Rückgängig",
        onClick: () => {
          void restoreItem(item!.id).then(() => onUpdated(item!));
        },
      },
    });
  }

  async function confirmTypeChange() {
    if (!pendingType) return;
    setItemType(pendingType);
    setPendingType(null);
    const result = await saveOnBlur({ type: pendingType });
    if (!result.ok && "conflict" in result) {
      setConflict(result.conflict);
    }
  }

  async function acceptRemote() {
    const remote = conflict?.remote_state;
    if (remote?.title) setTitle(remote.title);
    setConflict(null);
    onUpdated({
      ...item!,
      title: remote?.title ?? item!.title,
    });
  }

  async function keepLocal() {
    const result = await saveWithForce({ title, body });
    if (result.ok) {
      setConflict(null);
      toast.success("Eintrag gesichert.");
    } else if ("conflict" in result) {
      setConflict(result.conflict);
    }
  }

  const remote = conflict?.remote_state;
  const ogImage = item.image;

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (!next) void handleClose();
        }}
      >
        <DialogContent
          className="max-w-[560px]"
          data-testid="item-modal"
          onEscapeKeyDown={(event) => {
            event.preventDefault();
            void handleClose();
          }}
        >
          <DialogHeader>
            <DialogTitle>Eintrag bearbeiten</DialogTitle>
          </DialogHeader>

          {conflict ? (
            <div data-testid="conflict-panel" className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2 rounded-md border p-3">
                  <p className="text-sm font-semibold">Google hat:</p>
                  <p className="text-sm">{remote?.title ?? "—"}</p>
                  <p className="text-xs text-muted-foreground">
                    {remote?.starts_at ?? remote?.event_start ?? "—"} –{" "}
                    {remote?.ends_at ?? remote?.event_end ?? "—"}
                  </p>
                </div>
                <div className="space-y-2 rounded-md border p-3">
                  <p className="text-sm font-semibold">Du hast:</p>
                  <p className="text-sm">{title}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button type="button" onClick={() => void acceptRemote()}>
                  Übernehmen
                </Button>
                <Button type="button" variant="secondary" onClick={() => void keepLocal()}>
                  Behalten
                </Button>
                <Button type="button" variant="outline" onClick={() => setConflict(null)}>
                  Abbrechen
                </Button>
              </div>
            </div>
          ) : (
            <div className="max-h-[60vh] space-y-4 overflow-y-auto">
              {itemType === "link" ? (
                <div className="space-y-2 rounded-md border p-3" data-testid="og-preview">
                  <div className="relative aspect-[16/9] w-full overflow-hidden rounded bg-muted">
                    {ogImage && !ogBroken ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={ogImage}
                        alt=""
                        className="h-full w-full object-cover"
                        referrerPolicy="no-referrer"
                        onError={() => setOgBroken(true)}
                      />
                    ) : null}
                  </div>
                  <p className="text-sm font-semibold">{title}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2">{body}</p>
                  {scrapeLabel ? (
                    <p className="text-xs text-muted-foreground" data-testid="scrape-status-line">
                      {scrapeLabel}
                    </p>
                  ) : null}
                  {showScrapeRetry ? (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      disabled={rescrapePending}
                      onClick={() => void handleRescrape()}
                    >
                      Vorschau erneut laden
                    </Button>
                  ) : null}
                </div>
              ) : null}

              {showSyncMiss ? (
                <div className="space-y-2 rounded-md border border-dashed p-3" data-testid="sync-miss-panel">
                  <p className="text-xs text-muted-foreground">
                    Noch nicht mit Google Kalender synchronisiert.
                  </p>
                  {calendarConnected ? (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      disabled={syncPending}
                      onClick={() => void handleGoogleSync()}
                    >
                      Mit Google synchronisieren
                    </Button>
                  ) : (
                    <p className="text-xs">
                      <Link href="/settings" className="text-primary underline-offset-4 hover:underline">
                        Google Kalender in den Einstellungen verbinden
                      </Link>
                    </p>
                  )}
                </div>
              ) : null}

              <div className="space-y-2">
                <Label htmlFor="item-title">Titel</Label>
                <Input
                  id="item-title"
                  value={title}
                  onChange={(event) => {
                    setTitle(event.target.value);
                    scheduleSave({ title: event.target.value });
                  }}
                  onBlur={() => void handleTitleBlur()}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="item-body">Notizen</Label>
                <Textarea
                  id="item-body"
                  value={body}
                  onChange={(event) => {
                    setBody(event.target.value);
                    scheduleSave({ body: event.target.value });
                  }}
                  onBlur={() => void handleBodyBlur()}
                />
              </div>

              {itemType === "link" ? (
                <div className="space-y-2">
                  <Label htmlFor="item-url">URL</Label>
                  <Input
                    id="item-url"
                    value={url}
                    onChange={(event) => {
                      setUrl(event.target.value);
                      scheduleSave({ url: event.target.value });
                    }}
                    onBlur={() => void handleBodyBlur()}
                  />
                </div>
              ) : null}

              <div className="flex flex-wrap gap-2">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button type="button" variant="outline" size="sm">
                      Kategorie: {categories.find((c) => c.id === categoryId)?.name}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    {categories.map((category) => (
                      <DropdownMenuItem
                        key={category.id}
                        onClick={() => {
                          setCategoryId(category.id);
                          void saveOnBlur({ category_id: category.id });
                        }}
                      >
                        {category.name}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button type="button" variant="outline" size="sm">
                      Typ: {itemType}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    {ITEM_TYPES.map((type) => (
                      <DropdownMenuItem
                        key={type}
                        onClick={() => {
                          if (type !== itemType) setPendingType(type);
                        }}
                      >
                        {type}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <Button
                type="button"
                variant="destructive"
                onClick={() => void handleSoftDelete()}
              >
                Verstauen
              </Button>

              {pending ? (
                <p className="text-xs text-muted-foreground">Speichert…</p>
              ) : null}
            </div>
          )}
        </DialogContent>
      </Dialog>

      <AlertDialog open={pendingType !== null} onOpenChange={() => setPendingType(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Typ ändern?</AlertDialogTitle>
            <AlertDialogDescription>
              Typ ändern? Manche Felder gehen verloren.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={() => void confirmTypeChange()}>
              Ändern
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
