"use client";

import { useEffect, useRef } from "react";
import { toast } from "sonner";

import { useSound } from "@/lib/hooks/use-sound";

const TOAST_MESSAGE =
  "Eintrag gesichert. Apollo hat es stibitzt und sortiert.";

type NewItemFeedbackProps = {
  newItemIds: string[];
};

export function NewItemFeedback({ newItemIds }: NewItemFeedbackProps) {
  const { playNewItemTick } = useSound();
  const seenRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    for (const id of newItemIds) {
      if (seenRef.current.has(id)) continue;
      seenRef.current.add(id);
      toast.success(TOAST_MESSAGE);
      playNewItemTick();
    }
  }, [newItemIds, playNewItemTick]);

  return null;
}

export { TOAST_MESSAGE };
