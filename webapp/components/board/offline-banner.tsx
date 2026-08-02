"use client";

import Image from "next/image";

import { Button } from "@/components/ui/button";

type OfflineBannerProps = {
  onRetry: () => void;
};

export function OfflineBanner({ onRetry }: OfflineBannerProps) {
  return (
    <div
      role="alert"
      className="flex items-center justify-between gap-3 border-b border-destructive/30 bg-destructive/10 px-4 py-2 text-sm"
    >
      <div className="flex min-w-0 items-center gap-2">
        <Image
          src="/apollo-avatar.png"
          alt=""
          width={24}
          height={24}
          className="size-6 shrink-0 opacity-60"
          aria-hidden
        />
        <p className="text-foreground">
          Keine Verbindung. Apollo sucht nach dem Signal…
        </p>
      </div>
      <Button type="button" variant="outline" size="sm" onClick={onRetry}>
        Erneut versuchen
      </Button>
    </div>
  );
}
