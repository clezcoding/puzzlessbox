"use client";

import { useState } from "react";
import { GripVertical, Link2, Loader2, MoreHorizontal } from "lucide-react";
import { Draggable } from "@hello-pangea/dnd";

import type { BoardItem, Category } from "@/lib/api-client";
import { cn } from "@/lib/utils";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  const diffMs = Date.now() - date.getTime();
  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "gerade eben";
  if (minutes < 60) return `vor ${minutes} Min.`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `vor ${hours} Std.`;
  const days = Math.floor(hours / 24);
  return `vor ${days} Tg.`;
}

function linkHostname(summary: string): string {
  try {
    return new URL(summary).hostname;
  } catch {
    return summary.length > 40 ? `${summary.slice(0, 37)}…` : summary;
  }
}

type LinkThumbState = "loading" | "placeholder" | "image";

function linkThumbState(item: BoardItem, thumbBroken: boolean): LinkThumbState {
  const status = item.scrape_status;
  if (status === "pending" || status === "scraping") {
    return "loading";
  }
  if (status === "failed" || status === "timed_out") {
    return "placeholder";
  }
  if (item.image && !thumbBroken) {
    return "image";
  }
  return "placeholder";
}

export type BoardCardProps = {
  item: BoardItem;
  accentColor: string;
  index: number;
  isSelected: boolean;
  isNew: boolean;
  isMobile: boolean;
  categories: Category[];
  onSelect: (id: string, selected: boolean) => void;
  onOpen: (item: BoardItem) => void;
  onMoveToCategory: (itemId: string, categoryId: string) => void;
  onLongPress?: (item: BoardItem) => void;
};

export function BoardCard({
  item,
  accentColor,
  index,
  isSelected,
  isNew,
  isMobile,
  categories,
  onSelect,
  onOpen,
  onMoveToCategory,
  onLongPress,
}: BoardCardProps) {
  const isLink = item.type === "link";
  const [thumbBroken, setThumbBroken] = useState(false);
  const thumbState = isLink ? linkThumbState(item, thumbBroken) : null;
  const longPressTimer = { current: null as ReturnType<typeof setTimeout> | null };

  function handleTouchStart() {
    if (!isMobile || !onLongPress) return;
    longPressTimer.current = setTimeout(() => onLongPress(item), 500);
  }

  function handleTouchEnd() {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }
  }

  const metaLine = isLink
    ? `${linkHostname(item.summary)} · ${formatRelativeTime(item.created_at)}`
    : `${item.type} · ${formatRelativeTime(item.created_at)}`;

  return (
    <Draggable draggableId={item.id} index={index}>
      {(provided, snapshot) => (
        <article
          ref={provided.innerRef}
          {...provided.draggableProps}
          data-testid={`board-card-${item.id}`}
          data-dragging={snapshot.isDragging ? "true" : "false"}
          className={cn(
            "overflow-hidden rounded-lg border border-border bg-card shadow-sm",
            snapshot.isDragging && "board-card-ghost opacity-95 shadow-lg",
            isNew && "animate-pulse border-brand/60 bg-brand-soft/30",
          )}
          style={{
            borderTopWidth: 2,
            borderTopColor: accentColor,
            ...provided.draggableProps.style,
          }}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          onTouchMove={handleTouchEnd}
        >
          {isLink && (
            <div
              className="relative aspect-[16/9] w-full bg-muted transition-opacity duration-200 ease-out motion-reduce:transition-none"
              data-thumb-state={thumbState ?? undefined}
            >
              {thumbState === "image" ? (
                <img
                  src={item.image!}
                  alt=""
                  className="h-full w-full object-cover"
                  referrerPolicy="no-referrer"
                  onError={() => setThumbBroken(true)}
                />
              ) : thumbState === "loading" ? (
                <div className="flex h-full items-center justify-center bg-muted">
                  <Loader2
                    className="size-5 text-muted-foreground motion-safe:animate-spin"
                    aria-hidden
                  />
                  <span className="sr-only">Vorschau wird geladen</span>
                </div>
              ) : (
                <div className="flex h-full items-center justify-center bg-muted">
                  <Link2 className="size-5 text-muted-foreground" aria-hidden />
                </div>
              )}
            </div>
          )}
          <div className="flex items-start gap-2 p-3">
            <Checkbox
              checked={isSelected}
              onCheckedChange={(checked) => onSelect(item.id, checked === true)}
              aria-label={`${item.title} auswählen`}
              onClick={(event) => event.stopPropagation()}
              onPointerDown={(event) => event.stopPropagation()}
            />
            <button
              type="button"
              className="min-w-0 flex-1 space-y-1 text-left"
              onClick={() => onOpen(item)}
            >
              <h3 className="line-clamp-2 text-sm font-semibold text-foreground">
                {item.title}
              </h3>
              <p className="text-xs text-muted-foreground">{metaLine}</p>
            </button>
            <div className="flex shrink-0 items-center gap-1">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    type="button"
                    className="rounded p-1 text-muted-foreground hover:bg-accent"
                    aria-label="In Kategorie verschieben"
                  >
                    <MoreHorizontal className="size-4" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {categories.map((category) => (
                    <DropdownMenuItem
                      key={category.id}
                      onClick={() => onMoveToCategory(item.id, category.id)}
                    >
                      {category.name}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
              {!isMobile ? (
                <button
                  type="button"
                  className="cursor-grab rounded p-1 text-muted-foreground hover:bg-accent active:cursor-grabbing"
                  aria-label="Ziehen"
                  {...provided.dragHandleProps}
                >
                  <GripVertical className="size-4" />
                </button>
              ) : null}
            </div>
          </div>
        </article>
      )}
    </Draggable>
  );
}
