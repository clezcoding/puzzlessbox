"use client";

import Image from "next/image";
import { Droppable } from "@hello-pangea/dnd";
import { useState } from "react";

import type { BoardItem, Category } from "@/lib/api-client";
import { getEmptyCopy } from "@/lib/empty-copy";
import { getCategoryAccent, getCategoryBg } from "@/lib/category-style";
import { updateCategory } from "@/lib/api/categories";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

import { BoardCard } from "./board-card";

export type BoardColumnProps = {
  category: Category;
  items: BoardItem[];
  categories: Category[];
  selectedIds: Set<string>;
  newItemIds: Set<string>;
  isMobile: boolean;
  onSelect: (id: string, selected: boolean) => void;
  onOpenItem: (item: BoardItem) => void;
  onMoveToCategory: (itemId: string, categoryId: string) => void;
  onLongPress?: (item: BoardItem) => void;
  onCategoryUpdated?: (category: Category) => void;
};

export function BoardColumn({
  category,
  items,
  categories,
  selectedIds,
  newItemIds,
  isMobile,
  onSelect,
  onOpenItem,
  onMoveToCategory,
  onLongPress,
  onCategoryUpdated,
}: BoardColumnProps) {
  const accent = category.color ?? getCategoryAccent(category.name);
  const headerBg = getCategoryBg(category.name);
  const empty = getEmptyCopy(category.name);
  const [editing, setEditing] = useState(false);
  const [nameDraft, setNameDraft] = useState(category.name);

  async function commitRename() {
    const trimmed = nameDraft.trim().slice(0, 40);
    setEditing(false);
    if (!trimmed || trimmed === category.name) {
      setNameDraft(category.name);
      return;
    }
    const updated = await updateCategory(category.id, { name: trimmed });
    onCategoryUpdated?.(updated);
  }

  return (
    <section
      role="region"
      className="flex min-w-0 flex-col rounded-lg border border-border"
      aria-label={category.name}
    >
      <header
        className="flex items-center justify-between gap-2 border-b border-border px-3 py-2"
        style={{ backgroundColor: headerBg }}
      >
        {editing ? (
          <Input
            value={nameDraft}
            maxLength={40}
            className="h-7 text-sm"
            autoFocus
            onChange={(event) => setNameDraft(event.target.value)}
            onBlur={() => void commitRename()}
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                setNameDraft(category.name);
                setEditing(false);
              }
              if (event.key === "Enter") void commitRename();
            }}
          />
        ) : (
          <button
            type="button"
            className="flex min-w-0 items-center gap-2 text-left"
            onClick={() => setEditing(true)}
          >
            <span
              className="size-3 shrink-0 rounded-full border border-border"
              style={{ backgroundColor: accent }}
              aria-hidden
            />
            <h2
              className="truncate text-sm font-semibold text-foreground"
              title={category.name}
            >
              {category.name}
            </h2>
          </button>
        )}
        <span className="shrink-0 font-mono text-xs text-muted-foreground">
          {items.length}
        </span>
      </header>

      <Droppable droppableId={category.id}>
        {(provided) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={cn(
              "flex max-h-[70vh] flex-1 flex-col gap-2 overflow-y-auto p-2",
              items.length === 0 && "items-center justify-center py-6",
            )}
          >
            {items.length === 0 ? (
              <div className="flex flex-col items-center gap-3 px-2 text-center">
                <Image
                  src={empty.image}
                  alt={`Leerer Zustand ${category.name}`}
                  width={120}
                  height={120}
                  className="h-auto w-24"
                />
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-foreground">
                    {empty.heading}
                  </p>
                  <p className="text-xs text-muted-foreground">{empty.body}</p>
                </div>
              </div>
            ) : (
              items.map((item, index) => (
                <BoardCard
                  key={item.id}
                  item={item}
                  index={index}
                  accentColor={accent}
                  isSelected={selectedIds.has(item.id)}
                  isNew={newItemIds.has(item.id)}
                  isMobile={isMobile}
                  categories={categories}
                  onSelect={onSelect}
                  onOpen={onOpenItem}
                  onMoveToCategory={onMoveToCategory}
                  onLongPress={onLongPress}
                />
              ))
            )}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </section>
  );
}
