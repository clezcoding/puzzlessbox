"use client";

import Image from "next/image";
import { Link2 } from "lucide-react";

import type { BoardItem } from "@/lib/api-client";
import { cn } from "@/lib/utils";

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

type BoardCardProps = {
  item: BoardItem;
  accentColor: string;
};

export function BoardCard({ item, accentColor }: BoardCardProps) {
  const isLink = item.type === "link";
  const thumbnailUrl = isLink && item.summary.startsWith("http") ? item.summary : null;

  return (
    <article
      className="overflow-hidden rounded-lg border border-border bg-card shadow-sm"
      style={{ borderTopWidth: 2, borderTopColor: accentColor }}
    >
      {isLink && (
        <div className="relative aspect-[16/9] w-full bg-muted">
          {thumbnailUrl ? (
            <Image
              src={thumbnailUrl}
              alt=""
              fill
              className="object-cover"
              sizes="240px"
              unoptimized
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-muted">
              <Link2 className="size-5 text-muted-foreground" aria-hidden />
            </div>
          )}
        </div>
      )}
      <div className="space-y-1 p-3">
        <h3 className={cn("line-clamp-2 text-sm font-semibold text-foreground")}>
          {item.title}
        </h3>
        <p className="text-xs text-muted-foreground">
          {item.type} · {formatRelativeTime(item.created_at)}
        </p>
      </div>
    </article>
  );
}
