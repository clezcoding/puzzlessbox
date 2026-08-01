"use client";

import Image from "next/image";

import type { BoardItem, Category } from "@/lib/api-client";
import { getEmptyCopy } from "@/lib/empty-copy";
import { getCategoryAccent, getCategoryBg } from "@/lib/category-style";
import { cn } from "@/lib/utils";

import { BoardCard } from "./board-card";

type BoardColumnProps = {
  category: Category;
  items: BoardItem[];
};

export function BoardColumn({ category, items }: BoardColumnProps) {
  const accent = getCategoryAccent(category.name);
  const headerBg = getCategoryBg(category.name);
  const empty = getEmptyCopy(category.name);

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
        <h2
          className="truncate text-sm font-semibold text-foreground"
          title={category.name}
        >
          {category.name}
        </h2>
        <span className="shrink-0 font-mono text-xs text-muted-foreground">
          {items.length}
        </span>
      </header>

      <div className={cn("flex flex-1 flex-col gap-2 p-2", items.length === 0 && "items-center justify-center py-6")}>
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
              <p className="text-sm font-semibold text-foreground">{empty.heading}</p>
              <p className="text-xs text-muted-foreground">{empty.body}</p>
            </div>
          </div>
        ) : (
          items.map((item) => (
            <BoardCard key={item.id} item={item} accentColor={accent} />
          ))
        )}
      </div>
    </section>
  );
}
