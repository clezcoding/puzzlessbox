"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import type { ItemUpdateFields } from "@/lib/api/items";
import { updateItem } from "@/lib/api/items";

const DEBOUNCE_MS = 300;

export function useItemAutosave(itemId: string) {
  const [pending, setPending] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingFieldsRef = useRef<ItemUpdateFields | null>(null);
  const forceRef = useRef(false);

  const flush = useCallback(async (force = false) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    const fields = pendingFieldsRef.current;
    if (!fields) return { ok: true as const };

    pendingFieldsRef.current = null;
    setPending(true);
    try {
      const result = await updateItem(itemId, fields, {
        force: force || forceRef.current,
      });
      forceRef.current = false;
      if (!result.ok) {
        return result;
      }
      return { ok: true as const };
    } catch {
      toast.error("Speichern hakte. Versuch's gleich nochmal.");
      return { ok: false as const, error: true };
    } finally {
      setPending(false);
    }
  }, [itemId]);

  const scheduleSave = useCallback(
    (fields: ItemUpdateFields) => {
      pendingFieldsRef.current = { ...pendingFieldsRef.current, ...fields };
      setPending(true);
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        void flush();
      }, DEBOUNCE_MS);
    },
    [flush],
  );

  const saveOnBlur = useCallback(
    async (fields: ItemUpdateFields) => {
      pendingFieldsRef.current = { ...pendingFieldsRef.current, ...fields };
      return flush();
    },
    [flush],
  );

  const saveWithForce = useCallback(
    async (fields: ItemUpdateFields) => {
      forceRef.current = true;
      pendingFieldsRef.current = { ...pendingFieldsRef.current, ...fields };
      return flush(true);
    },
    [flush],
  );

  useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    },
    [],
  );

  return {
    pending,
    scheduleSave,
    saveOnBlur,
    flush,
    saveWithForce,
  };
}
