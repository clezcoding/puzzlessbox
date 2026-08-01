"use client";

import { useCallback, useEffect, useState } from "react";

export type ThemeMode = "system" | "light" | "dark";

const THEME_KEY = "pb.theme";

function readTheme(): ThemeMode {
  if (typeof window === "undefined") return "system";
  const stored = window.localStorage.getItem(THEME_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }
  return "system";
}

function resolveDark(mode: ThemeMode): boolean {
  if (mode === "dark") return true;
  if (mode === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(mode: ThemeMode) {
  document.documentElement.classList.toggle("dark", resolveDark(mode));
}

export function useTheme() {
  const [theme, setThemeState] = useState<ThemeMode>("system");

  useEffect(() => {
    const initial = readTheme();
    setThemeState(initial);
    applyTheme(initial);

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if (readTheme() === "system") {
        applyTheme("system");
      }
    };
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  const setTheme = useCallback((mode: ThemeMode) => {
    window.localStorage.setItem(THEME_KEY, mode);
    setThemeState(mode);
    applyTheme(mode);
  }, []);

  const toggleTheme = useCallback(() => {
    const next =
      theme === "system"
        ? resolveDark("system")
          ? "light"
          : "dark"
        : theme === "dark"
          ? "light"
          : "dark";
    setTheme(next);
  }, [setTheme, theme]);

  return { theme, setTheme, toggleTheme };
}
