/**
 * Next.js server startup hook — runs once before the app accepts traffic.
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
 */
export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME !== "nodejs") {
    return;
  }

  const { ensureAuthSchema } = await import("./lib/ensure-auth-schema");
  await ensureAuthSchema();
}
