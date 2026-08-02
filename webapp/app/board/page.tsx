"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { BoardHeader } from "@/components/board/board-header";
import { BulkMoveBar } from "@/components/board/bulk-move-bar";
import { CategoriesPanel } from "@/components/board/categories-panel";
import { ItemModal } from "@/components/board/item-modal";
import { MobileCategorySheet } from "@/components/board/mobile-category-sheet";
import { NewItemFeedback } from "@/components/board/new-item-feedback";
import { OfflineBanner } from "@/components/board/offline-banner";
import type { BoardItem } from "@/lib/api-client";
import { moveItem } from "@/lib/api/items";
import { useBoardPoll } from "@/lib/hooks/use-board-poll";
import { useSession } from "@/lib/auth-client";
import { useMediaQuery } from "@/lib/hooks/use-media-query";

const BoardDnd = dynamic(
  () => import("@/components/board/board-dnd").then((mod) => mod.BoardDnd),
  { ssr: false },
);

export default function BoardPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const isMobile = useMediaQuery("(max-width: 767px)");
  const [mounted, setMounted] = useState(false);
  const [activeCategoryId, setActiveCategoryId] = useState("");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [openItem, setOpenItem] = useState<BoardItem | null>(null);
  const [sheetItem, setSheetItem] = useState<BoardItem | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [pollNewItemIds, setPollNewItemIds] = useState<string[]>([]);

  const handleNewItems = useCallback((ids: string[]) => {
    setPollNewItemIds((prev) => [...prev, ...ids]);
  }, []);

  const {
    items,
    categories,
    setCategories,
    setItems,
    offline,
    loading,
    refresh,
  } = useBoardPoll({
    enabled: !isPending && !!session,
    onNewItems: handleNewItems,
  });

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (isPending) return;
    if (!session) {
      router.replace("/login");
    }
  }, [isPending, session, router]);

  useEffect(() => {
    if (!activeCategoryId && categories[0]) {
      setActiveCategoryId(categories[0].id);
    }
  }, [activeCategoryId, categories]);

  const selectedList = useMemo(() => Array.from(selectedIds), [selectedIds]);

  function handleSelect(id: string, selected: boolean) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (selected) next.add(id);
      else next.delete(id);
      return next;
    });
  }

  async function handleMoveToCategory(itemId: string, categoryId: string) {
    try {
      await moveItem(itemId, categoryId);
      toast.success("Eintrag verschoben.");
      refresh();
    } catch {
      toast.error("Verschieben fehlgeschlagen. Eintrag ist zurück.");
    }
  }

  if (isPending || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Einen Moment…
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <BoardHeader
        userEmail={session.user.email}
        onRefresh={refresh}
      />
      {offline ? <OfflineBanner onRetry={refresh} /> : null}
      <NewItemFeedback newItemIds={pollNewItemIds} />
      <div className="flex items-center gap-2 border-b border-border px-4 py-2">
        <CategoriesPanel categories={categories} onCategoriesChange={setCategories} />
      </div>
      <div className="flex-1 overflow-x-auto p-4 [scrollbar-gutter:stable]">
        {loading || !mounted ? (
          <p className="text-sm text-muted-foreground">Board wird geladen…</p>
        ) : (
          <BoardDnd
            categories={categories}
            items={items}
            isMobile={isMobile}
            activeCategoryId={activeCategoryId || categories[0]?.id || ""}
            selectedIds={selectedIds}
            onActiveCategoryChange={setActiveCategoryId}
            onSelect={handleSelect}
            onOpenItem={setOpenItem}
            onMoveToCategory={(itemId, categoryId) =>
              void handleMoveToCategory(itemId, categoryId)
            }
            onLongPress={(item) => {
              setSheetItem(item);
              setSheetOpen(true);
            }}
            onCategoryUpdated={(category) => {
              setCategories((prev) =>
                prev.map((entry) => (entry.id === category.id ? category : entry)),
              );
            }}
          />
        )}
      </div>

      <BulkMoveBar
        count={selectedList.length}
        categories={categories}
        selectedIds={selectedList}
        onMoved={refresh}
        onClear={() => setSelectedIds(new Set())}
      />

      <ItemModal
        item={openItem}
        categories={categories}
        open={openItem !== null}
        onClose={() => setOpenItem(null)}
        onDeleted={(id) => {
          setItems((prev) => prev.filter((item) => item.id !== id));
          setOpenItem(null);
        }}
        onUpdated={(item) => {
          setItems((prev) =>
            prev.map((entry) => (entry.id === item.id ? item : entry)),
          );
        }}
      />

      <MobileCategorySheet
        open={sheetOpen}
        item={sheetItem}
        categories={categories}
        onClose={() => setSheetOpen(false)}
        onMoved={refresh}
      />
    </div>
  );
}
