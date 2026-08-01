"use client";

import type { BoardItem, Category } from "@/lib/api-client";
import { moveItem } from "@/lib/api/items";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

type MobileCategorySheetProps = {
  open: boolean;
  item: BoardItem | null;
  categories: Category[];
  onClose: () => void;
  onMoved: () => void;
};

export function MobileCategorySheet({
  open,
  item,
  categories,
  onClose,
  onMoved,
}: MobileCategorySheetProps) {
  async function selectCategory(categoryId: string) {
    if (!item) return;
    await moveItem(item.id, categoryId);
    onMoved();
    onClose();
  }

  return (
    <Sheet open={open} onOpenChange={(next) => !next && onClose()}>
      <SheetContent side="bottom" data-testid="mobile-category-sheet">
        <SheetHeader>
          <SheetTitle>Kategorie wählen</SheetTitle>
        </SheetHeader>
        <div className="flex flex-col gap-2">
          {categories.map((category) => (
            <Button
              key={category.id}
              type="button"
              variant="outline"
              className="justify-start"
              onClick={() => void selectCategory(category.id)}
            >
              {category.name}
            </Button>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}
