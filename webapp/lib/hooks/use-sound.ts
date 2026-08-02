"use client";

import { useCallback, useEffect, useState } from "react";

const SOUND_KEY = "pb.sound";

function readSoundEnabled(): boolean {
  if (typeof window === "undefined" || !window.localStorage) return false;
  return window.localStorage.getItem(SOUND_KEY) === "true";
}

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function useSound() {
  const [enabled, setEnabledState] = useState(false);

  useEffect(() => {
    setEnabledState(readSoundEnabled());
  }, []);

  const setEnabled = useCallback((value: boolean) => {
    window.localStorage?.setItem(SOUND_KEY, value ? "true" : "false");
    setEnabledState(value);
  }, []);

  const playNewItemTick = useCallback(() => {
    if (!enabled || prefersReducedMotion()) return;
    try {
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.value = 0.04;
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.08);
      osc.onended = () => void ctx.close();
    } catch {
      // WebAudio unavailable in test env
    }
  }, [enabled]);

  return { enabled, setEnabled, playNewItemTick };
}
