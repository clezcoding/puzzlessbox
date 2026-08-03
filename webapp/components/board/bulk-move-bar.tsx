"use client";

import { toast } from "sonner";

import type { Category } from "@/lib/api-client";
import { moveItem } from "@/lib/api/items";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type BulkMoveBarProps = {
  count: number;
  categories: Category[];
  selectedIds: string[];
  onMoved: () => void;
  onClear: () => void;
};

export function BulkMoveBar({
  count,
  categories,
  selectedIds,
  onMoved,
  onClear,
}: BulkMoveBarProps) {
  if (count === 0) return null;

  async function handleBulkMove(categoryId: string) {
    const total = selectedIds.length;
    let done = 0;
    const toastId =
      total > 5 ? toast.loading(`Verschiebe ${done}/${total}…`) : undefined;

    try {
      for (const id of selectedIds) {
        await moveItem(id, categoryId);
        done += 1;
        if (toastId) toast.loading(`Verschiebe ${done}/${total}…`, { id: toastId });
      }
      toast.success(
        total > 1 ? "Einträge verschoben." : "Eintrag verschoben.",
        toastId ? { id: toastId } : undefined,
      );
      onMoved();
      onClear();
    } catch {
      if (toastId) toast.dismiss(toastId);
      if (done > 0) onMoved();
      toast.error(
        done > 0
          ? `${done}/${total} verschoben, Rest fehlgeschlagen.`
          : "Verschieben fehlgeschlagen. Eintrag ist zurück.",
      );
    }
  }

  return (
    <div
      data-testid="bulk-move-bar"
      className="fixed bottom-6 left-1/2 z-40 flex -translate-x-1/2 items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 shadow-lg"
    >
      <span className="text-sm font-medium">{count} ausgewählt</span>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button type="button" size="sm" data-testid="bulk-move-trigger">
            In Kategorie verschieben
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          {categories.map((category) => (
            <DropdownMenuItem
              key={category.id}
              data-testid={`bulk-move-destination-${category.id}`}
              onClick={() => void handleBulkMove(category.id)}
            >
              {category.name}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
      <Button type="button" variant="ghost" size="sm" onClick={onClear}>
        Abbrechen
      </Button>
    </div>
  );
}
