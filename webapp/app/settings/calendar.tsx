"use client";

import { Suspense } from "react";

import { CalendarWizard } from "@/components/settings/calendar-wizard";

export function CalendarSection() {
  return (
    <Suspense fallback={<p className="text-sm text-muted-foreground">Kalender wird geladen…</p>}>
      <CalendarWizard />
    </Suspense>
  );
}
