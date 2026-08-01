"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  getBoardItems,
  getCategories,
  type BoardItem,
  type Category,
} from "@/lib/api-client";

export const POLL_INTERVAL_MS = 10_000;

const VISIBLE_STATUSES = new Set(["auto_saved", "confirmed"]);

export type UseBoardPollOptions = {
  enabled: boolean;
  onNewItems?: (ids: string[]) => void;
};

function mergeById(existing: BoardItem[], incoming: BoardItem[]): BoardItem[] {
  const map = new Map(existing.map((item) => [item.id, item]));
  for (const item of incoming) {
    map.set(item.id, item);
  }
  return Array.from(map.values());
}

export function intervalWithJitter(errorCount: number): number {
  const base =
    errorCount === 0
      ? POLL_INTERVAL_MS
      : Math.min(POLL_INTERVAL_MS * 2 ** errorCount, 60_000);
  return base * (Math.random() * 0.4 - 0.2 + 1);
}

export function useBoardPoll({ enabled, onNewItems }: UseBoardPollOptions) {
  const [items, setItems] = useState<BoardItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [offline, setOffline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorCount, setErrorCount] = useState(0);

  const knownIdsRef = useRef<Set<string>>(new Set());
  const errorCountRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);
  const onNewItemsRef = useRef(onNewItems);
  onNewItemsRef.current = onNewItems;

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const runPollRef = useRef<() => Promise<void>>(async () => {});

  const scheduleNext = useCallback(
    (nextErrorCount: number) => {
      clearTimer();
      if (!mountedRef.current || !enabled) return;
      timerRef.current = setTimeout(() => {
        void runPollRef.current();
      }, intervalWithJitter(nextErrorCount));
    },
    [clearTimer, enabled],
  );

  const runPoll = useCallback(async (): Promise<void> => {
    if (!mountedRef.current || !enabled) return;

    try {
      const [cats, boardItems] = await Promise.all([
        getCategories(),
        getBoardItems(),
      ]);
      const visible = boardItems.filter((item) => VISIBLE_STATUSES.has(item.status));
      const newIds = visible
        .filter((item) => !knownIdsRef.current.has(item.id))
        .map((item) => item.id);
      for (const item of visible) {
        knownIdsRef.current.add(item.id);
      }

      setCategories(cats);
      setItems((prev) => mergeById(prev, visible));
      setOffline(false);
      setLoading(false);
      errorCountRef.current = 0;
      setErrorCount(0);

      if (newIds.length > 0) {
        onNewItemsRef.current?.(newIds);
      }

      scheduleNext(0);
    } catch {
      setOffline(true);
      setLoading(false);
      errorCountRef.current = Math.min(errorCountRef.current + 1, 3);
      setErrorCount(errorCountRef.current);
      scheduleNext(errorCountRef.current);
    }
  }, [enabled, scheduleNext]);

  runPollRef.current = runPoll;

  const refresh = useCallback(() => {
    errorCountRef.current = 0;
    setErrorCount(0);
    clearTimer();
    void runPoll();
  }, [clearTimer, runPoll]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      clearTimer();
    };
  }, [clearTimer]);

  useEffect(() => {
    if (!enabled) {
      clearTimer();
      return;
    }
    void runPoll();
    return clearTimer;
  }, [enabled, runPoll, clearTimer]);

  return {
    items,
    categories,
    setCategories,
    setItems,
    offline,
    loading,
    refresh,
    errorCount,
  };
}
