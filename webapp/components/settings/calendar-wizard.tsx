"use client";

import Image from "next/image";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import {
  disconnectCalendar,
  getCalendarStatus,
  listCalendars,
  selectCalendar,
  startCalendarConnect,
  type GoogleCalendar,
} from "@/lib/api/calendar";
import { ApiError } from "@/lib/api-client";

type WizardStep = 1 | 2 | 3;

export function CalendarWizard() {
  const searchParams = useSearchParams();
  const stepParam = searchParams.get("step");
  const [step, setStep] = useState<WizardStep>(1);
  const [calendars, setCalendars] = useState<GoogleCalendar[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [connectedCalendarId, setConnectedCalendarId] = useState<string | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [listLoading, setListLoading] = useState(false);
  const [disconnectOpen, setDisconnectOpen] = useState(false);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    try {
      const status = await getCalendarStatus();
      if (status.connected && status.selected_calendar_id) {
        setConnectedCalendarId(status.selected_calendar_id);
        setStep(3);
        return;
      }
      if (status.connected || stepParam === "2") {
        setStep(2);
        setListLoading(true);
        const result = await listCalendars();
        setCalendars(result.data);
        if (result.data[0]) {
          setSelectedId(result.data[0].id);
        }
        setListLoading(false);
        return;
      }
      setStep(1);
    } catch (error) {
      if (error instanceof ApiError && error.code === "CALENDAR_NOT_CONNECTED") {
        setStep(1);
      } else {
        toast.error("Kalender-Status konnte nicht geladen werden.");
      }
    } finally {
      setLoading(false);
      setListLoading(false);
    }
  }, [stepParam]);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  async function handleConnect() {
    try {
      await startCalendarConnect();
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error("Google-Verbindung konnte nicht gestartet werden.");
      } else {
        toast.error("Google-Verbindung konnte nicht gestartet werden.");
      }
    }
  }

  async function handleComplete() {
    if (!selectedId) return;
    try {
      await selectCalendar(selectedId);
      setConnectedCalendarId(selectedId);
      setStep(3);
      toast.success("Kalender verbunden.");
    } catch {
      toast.error("Verbindung konnte nicht abgeschlossen werden.");
    }
  }

  async function handleDisconnect() {
    try {
      await disconnectCalendar();
      setConnectedCalendarId(null);
      setStep(1);
      setDisconnectOpen(false);
      toast.success("Google-Kalender getrennt.");
    } catch {
      toast.error("Trennen fehlgeschlagen.");
    }
  }

  if (loading) {
    return <p className="text-sm text-muted-foreground">Kalender wird geladen…</p>;
  }

  if (step === 3 && connectedCalendarId) {
    const label =
      calendars.find((entry) => entry.id === connectedCalendarId)?.summary ??
      connectedCalendarId;

    return (
      <div className="space-y-4">
        <p className="text-sm font-medium text-foreground">Kalender verbunden</p>
        <p className="truncate text-sm text-muted-foreground" title={label}>
          {label}
        </p>
        <AlertDialog open={disconnectOpen} onOpenChange={setDisconnectOpen}>
          <AlertDialogTrigger asChild>
            <Button type="button" variant="destructive">
              Trennen
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Google-Kalender trennen?</AlertDialogTitle>
              <AlertDialogDescription>
                Trennen: Google-Kalender trennen? Lokale Termine bleiben; Sync
                stoppt.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Abbrechen</AlertDialogCancel>
              <AlertDialogAction onClick={() => void handleDisconnect()}>
                Trennen
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    );
  }

  if (step === 2) {
    return (
      <div className="space-y-4">
        <h3 className="text-sm font-medium">Kalender wählen</h3>
        {listLoading ? (
          <p className="text-sm text-muted-foreground">Kalender werden geladen…</p>
        ) : (
          <ul className="space-y-2">
            {calendars.map((calendar) => (
              <li key={calendar.id}>
                <label className="flex cursor-pointer items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="calendar"
                    value={calendar.id}
                    checked={selectedId === calendar.id}
                    onChange={() => setSelectedId(calendar.id)}
                  />
                  <span className="truncate" title={calendar.summary}>
                    {calendar.summary}
                  </span>
                </label>
              </li>
            ))}
          </ul>
        )}
        <Button type="button" onClick={() => void handleComplete()} disabled={!selectedId}>
          Verbindung abschließen
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <Image
        src="/apollo-empty-cal.png"
        alt="Leerer Kalender"
        width={160}
        height={160}
        className="h-40 w-auto"
      />
      <Button type="button" onClick={() => void handleConnect()}>
        Mit Google verbinden
      </Button>
    </div>
  );
}
