"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { useSession } from "@/lib/auth-client";

const WELCOME_KEY = "pb.welcome.seen";

export default function WelcomePage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending && !session) {
      router.replace("/login");
    }
  }, [isPending, session, router]);

  function handleStart() {
    window.localStorage.setItem(WELCOME_KEY, "true");
    router.push("/board");
  }

  if (isPending || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Einen Moment…
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 text-center">
      <Image
        src="/apollo-onboard.png"
        alt="Apollo begrüßt dich"
        width={200}
        height={200}
        className="h-48 w-auto"
        priority
      />
      <p className="max-w-md text-lg text-foreground">
        Hallo, ich bin Apollo. Lass uns das Chaos ordnen.
      </p>
      <Button type="button" onClick={handleStart}>
        Los geht&apos;s
      </Button>
    </div>
  );
}
