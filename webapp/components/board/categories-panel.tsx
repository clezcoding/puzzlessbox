"use client";

import { DragDropContext, Draggable, Droppable, type DropResult } from "@hello-pangea/dnd";
import { useEffect, useState } from "react";

import type { Category } from "@/lib/api-client";
import {
  createCategory,
  listCategories,
  reorderCategories,
  updateCategory,
} from "@/lib/api/categories";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

type CategoriesPanelProps = {
  categories: Category[];
  onCategoriesChange: (categories: Category[]) => void;
};

export function CategoriesPanel({
  categories,
  onCategoriesChange,
}: CategoriesPanelProps) {
  const [open, setOpen] = useState(false);
  const [localCategories, setLocalCategories] = useState(categories);
  const [newName, setNewName] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");

  useEffect(() => {
    setLocalCategories(categories);
  }, [categories]);

  async function refresh() {
    const next = await listCategories();
    setLocalCategories(next);
    onCategoriesChange(next);
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const name = newName.trim();
    if (!name) return;
    await createCategory(name);
    setNewName("");
    await refresh();
  }

  async function handleRename(category: Category) {
    const name = editName.trim().slice(0, 40);
    setEditingId(null);
    if (!name || name === category.name) return;
    await updateCategory(category.id, { name });
    await refresh();
  }

  async function onDragEnd(result: DropResult) {
    if (!result.destination) return;
    const reordered = Array.from(localCategories);
    const [removed] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, removed);
    const withOrder = reordered.map((category, index) => ({
      ...category,
      sort_order: index,
    }));
    setLocalCategories(withOrder);
    await reorderCategories(
      withOrder.map((category) => ({ id: category.id, sort_order: category.sort_order })),
    );
    await refresh();
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button type="button" variant="outline" size="sm" data-testid="categories-panel-trigger">
          Kategorien verwalten
        </Button>
      </SheetTrigger>
      <SheetContent side="right" data-testid="categories-panel">
        <SheetHeader>
          <SheetTitle>Kategorien verwalten</SheetTitle>
        </SheetHeader>

        <form onSubmit={(event) => void handleCreate(event)} className="mt-4 flex gap-2">
          <Input
            value={newName}
            onChange={(event) => setNewName(event.target.value)}
            placeholder="Neue Kategorie"
            maxLength={40}
          />
          <Button type="submit">Anlegen</Button>
        </form>

        <DragDropContext onDragEnd={(result) => void onDragEnd(result)}>
          <Droppable droppableId="categories-list">
            {(provided) => (
              <ul
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="mt-4 space-y-2"
              >
                {localCategories.map((category, index) => (
                  <Draggable key={category.id} draggableId={category.id} index={index}>
                    {(dragProvided) => (
                      <li
                        ref={dragProvided.innerRef}
                        {...dragProvided.draggableProps}
                        {...dragProvided.dragHandleProps}
                        className="flex items-center gap-2 rounded-md border p-2"
                      >
                        <span
                          className="size-4 shrink-0 rounded-full border"
                          style={{ backgroundColor: category.color ?? "#eaeaea" }}
                        />
                        {editingId === category.id ? (
                          <Input
                            value={editName}
                            maxLength={40}
                            autoFocus
                            className="h-8"
                            onChange={(event) => setEditName(event.target.value)}
                            onBlur={() => void handleRename(category)}
                            onKeyDown={(event) => {
                              if (event.key === "Escape") setEditingId(null);
                              if (event.key === "Enter") void handleRename(category);
                            }}
                          />
                        ) : (
                          <button
                            type="button"
                            className="min-w-0 flex-1 truncate text-left text-sm"
                            title={category.name}
                            onClick={() => {
                              setEditingId(category.id);
                              setEditName(category.name);
                            }}
                          >
                            {category.name}
                          </button>
                        )}
                      </li>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </ul>
            )}
          </Droppable>
        </DragDropContext>
      </SheetContent>
    </Sheet>
  );
}
