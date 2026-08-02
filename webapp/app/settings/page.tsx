"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { AccountSection } from "./account";
import { AppearanceSection } from "./appearance";
import { CalendarSection } from "./calendar";
import { useSession } from "@/lib/auth-client";

export default function SettingsPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending && !session) {
      router.replace("/login");
    }
  }, [isPending, session, router]);

  if (isPending || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Einen Moment…
      </div>
    );
  }

  return (
    <div className="mx-auto min-h-screen max-w-2xl bg-background px-4 py-8">
      <div className="mb-8 flex items-center justify-between gap-4">
        <h1 className="font-display text-2xl text-foreground">Einstellungen</h1>
        <Link href="/board" className="text-sm text-muted-foreground hover:text-foreground">
          Zum Board
        </Link>
      </div>

      <section className="mb-10 space-y-4 border-b border-border pb-10">
        <h2 className="text-lg font-semibold">Account</h2>
        <AccountSection email={session.user.email} />
      </section>

      <section className="mb-10 space-y-4 border-b border-border pb-10">
        <h2 className="text-lg font-semibold">Google Calendar</h2>
        <CalendarSection />
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Darstellung</h2>
        <AppearanceSection />
      </section>
    </div>
  );
}
