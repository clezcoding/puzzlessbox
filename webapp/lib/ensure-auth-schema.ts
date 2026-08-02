import { getMigrations } from "better-auth/db/migration";
import { auth } from "./auth.config";

/**
 * Apply Better Auth schema via the official programmatic migrator
 * (`better-auth/db/migration` — same path the CLI uses for Kysely/pg).
 *
 * Prefer this over `@better-auth/cli` in Docker: Next standalone images
 * do not ship the CLI, and Coolify pre-deploy `docker exec` is unreliable
 * on first boot.
 */
export async function ensureAuthSchema(): Promise<void> {
  if (process.env.AUTH_MIGRATE_ON_START === "false") {
    return;
  }
  if (!process.env.DATABASE_URL) {
    throw new Error(
      "DATABASE_URL is required for Better Auth schema migration",
    );
  }

  const { toBeCreated, toBeAdded, runMigrations } = await getMigrations(
    auth.options,
  );

  if (!toBeCreated.length && !toBeAdded.length) {
    console.info("[better-auth] schema up to date");
    return;
  }

  console.info(
    `[better-auth] migrating schema (create=${toBeCreated.length}, add=${toBeAdded.length})`,
  );
  await runMigrations();
  console.info("[better-auth] schema migration complete");
}
