"use client";

import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useSound } from "@/lib/hooks/use-sound";
import { useTheme, type ThemeMode } from "@/lib/hooks/use-theme";

const THEME_OPTIONS: { value: ThemeMode; label: string }[] = [
  { value: "system", label: "System" },
  { value: "light", label: "Hell" },
  { value: "dark", label: "Dunkel" },
];

export function AppearanceSection() {
  const { theme, setTheme } = useTheme();
  const { enabled: soundEnabled, setEnabled: setSoundEnabled } = useSound();

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <p className="text-sm font-medium">Darstellung</p>
        <div className="flex flex-wrap gap-2">
          {THEME_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`rounded-md border px-3 py-1.5 text-sm ${
                theme === option.value
                  ? "border-primary bg-primary/10 text-foreground"
                  : "border-border text-muted-foreground"
              }`}
              onClick={() => setTheme(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between gap-4">
        <Label htmlFor="sound-toggle" className="text-sm font-medium">
          Sound bei neuem Eintrag
        </Label>
        <Switch
          id="sound-toggle"
          checked={soundEnabled}
          onCheckedChange={setSoundEnabled}
        />
      </div>
    </div>
  );
}
