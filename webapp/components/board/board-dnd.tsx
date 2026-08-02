"use client";

import { DragDropContext } from "@hello-pangea/dnd";
import { useEffect, useMemo, useRef } from "react";

import type { BoardItem, Category } from "@/lib/api-client";
import { useOptimisticMove } from "@/lib/hooks/use-optimistic-move";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { BoardColumn } from "./board-column";

export type BoardDndProps = {
  categories: Category[];
  items: BoardItem[];
  isMobile: boolean;
  activeCategoryId: string;
  selectedIds: Set<string>;
  onActiveCategoryChange: (id: string) => void;
  onSelect: (id: string, selected: boolean) => void;
  onOpenItem: (item: BoardItem) => void;
  onMoveToCategory: (itemId: string, categoryId: string) => void;
  onLongPress?: (item: BoardItem) => void;
  onCategoryUpdated?: (category: Category) => void;
};

export function BoardDnd({
  categories,
  items: externalItems,
  isMobile,
  activeCategoryId,
  selectedIds,
  onActiveCategoryChange,
  onSelect,
  onOpenItem,
  onMoveToCategory,
  onLongPress,
  onCategoryUpdated,
}: BoardDndProps) {
  const { items, setItems, onDragEnd } = useOptimisticMove(externalItems);
  const prevIdsRef = useRef<Set<string>>(new Set());
  const newItemIds = useMemo(() => {
    const current = new Set(items.map((item) => item.id));
    const appeared = new Set<string>();
    for (const id of current) {
      if (!prevIdsRef.current.has(id)) appeared.add(id);
    }
    return appeared;
  }, [items]);

  useEffect(() => {
    prevIdsRef.current = new Set(items.map((item) => item.id));
    const timer = setTimeout(() => {
      prevIdsRef.current = new Set(items.map((item) => item.id));
    }, 2000);
    return () => clearTimeout(timer);
  }, [items]);

  useEffect(() => {
    setItems(externalItems);
  }, [externalItems, setItems]);

  const itemsByCategory = useMemo(() => {
    const map = new Map<string, BoardItem[]>();
    for (const category of categories) {
      map.set(category.id, []);
    }
    for (const item of items) {
      const list = map.get(item.category_id);
      if (list) list.push(item);
    }
    for (const [, list] of map) {
      list.sort((a, b) => {
        if (a.sort_order !== b.sort_order) return a.sort_order - b.sort_order;
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
    }
    return map;
  }, [categories, items]);

  const visibleCategories = isMobile
    ? categories.filter((category) => category.id === activeCategoryId)
    : categories;

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      {isMobile ? (
        <Tabs
          value={activeCategoryId}
          onValueChange={onActiveCategoryChange}
          className="mb-4"
        >
          <TabsList className="h-auto w-full justify-start overflow-x-auto">
            {categories.map((category) => (
              <TabsTrigger
                key={category.id}
                value={category.id}
                className="max-w-[8rem] truncate"
                title={category.name}
              >
                {category.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      ) : null}

      <div
        className={
          isMobile
            ? "flex min-h-[60vh] flex-col"
            : "grid min-h-[60vh] gap-4"
        }
        style={
          isMobile
            ? undefined
            : {
                gridTemplateColumns: `repeat(${Math.max(categories.length, 1)}, minmax(0, 1fr))`,
              }
        }
      >
        {visibleCategories.map((category) => (
          <BoardColumn
            key={category.id}
            category={category}
            items={itemsByCategory.get(category.id) ?? []}
            categories={categories}
            selectedIds={selectedIds}
            newItemIds={newItemIds}
            isMobile={isMobile}
            onSelect={onSelect}
            onOpenItem={onOpenItem}
            onMoveToCategory={onMoveToCategory}
            onLongPress={onLongPress}
            onCategoryUpdated={onCategoryUpdated}
          />
        ))}
      </div>
    </DragDropContext>
  );
}
