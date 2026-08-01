"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import type { BoardItem, Category, ConflictDetails } from "@/lib/api-client";
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
  const { pending, scheduleSave, saveOnBlur, flush, saveWithForce } =
    useItemAutosave(item?.id ?? "");

  useEffect(() => {
    if (!item) return;
    setTitle(item.title);
    setBody(item.summary);
    setUrl(item.type === "link" ? item.summary : "");
    setItemType(item.type);
    setCategoryId(item.category_id);
    setConflict(null);
  }, [item]);

  if (!item) return null;

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
                    {url ? (
                      <Image
                        src={url}
                        alt=""
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    ) : null}
                  </div>
                  <p className="text-sm font-semibold">{title}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2">{body}</p>
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
