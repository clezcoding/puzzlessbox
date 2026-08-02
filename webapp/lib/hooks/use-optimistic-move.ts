"use client";

import { useCallback, useState } from "react";
import type { DropResult } from "@hello-pangea/dnd";
import { toast } from "sonner";

import type { BoardItem } from "@/lib/api-client";
import { moveItem, reorderItems } from "@/lib/api/items";

function sortItems(items: BoardItem[]): BoardItem[] {
  return [...items].sort((a, b) => {
    if (a.category_id !== b.category_id) {
      return a.category_id.localeCompare(b.category_id);
    }
    if (a.sort_order !== b.sort_order) return a.sort_order - b.sort_order;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
}

export function useOptimisticMove(initialItems: BoardItem[]) {
  const [items, setItems] = useState<BoardItem[]>(() => sortItems(initialItems));

  const syncItems = useCallback((next: BoardItem[]) => {
    setItems(sortItems(next));
  }, []);

  const onDragEnd = useCallback(async (result: DropResult) => {
    const { destination, source, draggableId } = result;
    if (!destination) return;
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const previous = items;
    const moved = items.find((item) => item.id === draggableId);
    if (!moved) return;

    const sameColumn = destination.droppableId === source.droppableId;

    const withoutMoved = items.filter((item) => item.id !== draggableId);
    const destColumn = withoutMoved
      .filter((item) => item.category_id === destination.droppableId)
      .sort((a, b) => a.sort_order - b.sort_order);

    const updatedMoved: BoardItem = {
      ...moved,
      category_id: destination.droppableId,
    };
    destColumn.splice(destination.index, 0, updatedMoved);
    const destWithSort = destColumn.map((item, index) => ({
      ...item,
      sort_order: index,
    }));

    const optimistic = [
      ...withoutMoved.filter((item) => item.category_id !== destination.droppableId),
      ...destWithSort,
    ];

    if (!sameColumn) {
      const sourceColumn = withoutMoved
        .filter((item) => item.category_id === source.droppableId)
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((item, index) => ({ ...item, sort_order: index }));
      const destIds = new Set(destWithSort.map((item) => item.id));
      optimistic.splice(
        0,
        optimistic.length,
        ...withoutMoved.filter(
          (item) =>
            item.category_id !== source.droppableId &&
            item.category_id !== destination.droppableId,
        ),
        ...sourceColumn,
        ...destWithSort.filter((item) => destIds.has(item.id)),
      );
    }

    setItems(sortItems(optimistic));

    try {
      if (sameColumn) {
        await reorderItems(
          destWithSort.map((item, index) => ({ id: item.id, sort_order: index })),
        );
      } else {
        await moveItem(draggableId, destination.droppableId);
        if (destWithSort.length > 1) {
          await reorderItems(
            destWithSort.map((item, index) => ({ id: item.id, sort_order: index })),
          );
        }
      }
      toast.success("Eintrag verschoben.");
    } catch {
      setItems(previous);
      toast.error("Verschieben fehlgeschlagen. Eintrag ist zurück.");
    }
  }, [items]);

  return { items, setItems: syncItems, onDragEnd };
}
