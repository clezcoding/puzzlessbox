"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { BoardColumn } from "@/components/board/board-column";
import { BoardHeader } from "@/components/board/board-header";
import {
  getBoardItems,
  getCategories,
  type BoardItem,
  type Category,
} from "@/lib/api-client";
import { useSession } from "@/lib/auth-client";

const VISIBLE_STATUSES = new Set(["auto_saved", "confirmed"]);

export default function BoardPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<BoardItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadBoard = useCallback(async () => {
    setLoading(true);
    try {
      const [cats, boardItems] = await Promise.all([
        getCategories(),
        getBoardItems(),
      ]);
      setCategories(cats);
      setItems(boardItems.filter((item) => VISIBLE_STATUSES.has(item.status)));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isPending) return;
    if (!session) {
      router.replace("/login");
      return;
    }
    void loadBoard();
  }, [isPending, session, router, loadBoard]);

  const itemsByCategory = useMemo(() => {
    const map = new Map<string, BoardItem[]>();
    for (const category of categories) {
      map.set(category.id, []);
    }
    for (const item of items) {
      const list = map.get(item.category_id);
      if (list) list.push(item);
    }
    return map;
  }, [categories, items]);

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
        onRefresh={() => void loadBoard()}
      />
      <div className="flex-1 overflow-x-auto p-4 [scrollbar-gutter:stable]">
        {loading ? (
          <p className="text-sm text-muted-foreground">Board wird geladen…</p>
        ) : (
          <div
            className="grid min-h-[60vh] gap-4"
            style={{
              gridTemplateColumns: `repeat(${Math.max(categories.length, 1)}, minmax(0, 1fr))`,
            }}
          >
            {categories.map((category) => (
              <BoardColumn
                key={category.id}
                category={category}
                items={itemsByCategory.get(category.id) ?? []}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
