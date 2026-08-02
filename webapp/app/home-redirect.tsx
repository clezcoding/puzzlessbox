"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { getSafeNextPath } from "@/lib/redirect";

const WELCOME_KEY = "pb.welcome.seen";

export function HomeRedirect() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const safeNext = getSafeNextPath(searchParams.get("next"));
    if (safeNext) {
      router.replace(safeNext);
      return;
    }
    if (window.localStorage.getItem(WELCOME_KEY) !== "true") {
      router.replace("/welcome");
      return;
    }
    router.replace("/board");
  }, [router, searchParams]);

  return (
    <div className="flex min-h-screen items-center justify-center text-muted-foreground">
      Einen Moment…
    </div>
  );
}
