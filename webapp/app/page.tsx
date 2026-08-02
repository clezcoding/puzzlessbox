import { Suspense } from "react";

import { HomeRedirect } from "./home-redirect";

export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center text-muted-foreground">
          Einen Moment…
        </div>
      }
    >
      <HomeRedirect />
    </Suspense>
  );
}
