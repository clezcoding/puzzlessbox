import { describe, expect, it, vi, beforeEach } from "vitest";

vi.mock("better-auth/db/migration", () => ({
  getMigrations: vi.fn(),
}));

vi.mock("./auth.config", () => ({
  auth: { options: { database: {} } },
}));

import { getMigrations } from "better-auth/db/migration";
import { ensureAuthSchema } from "./ensure-auth-schema";

describe("ensureAuthSchema", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.DATABASE_URL = "postgresql://test:test@localhost:5432/test";
    delete process.env.AUTH_MIGRATE_ON_START;
  });

  it("skips when AUTH_MIGRATE_ON_START=false", async () => {
    process.env.AUTH_MIGRATE_ON_START = "false";
    await ensureAuthSchema();
    expect(getMigrations).not.toHaveBeenCalled();
  });

  it("throws without DATABASE_URL", async () => {
    delete process.env.DATABASE_URL;
    await expect(ensureAuthSchema()).rejects.toThrow(/DATABASE_URL/);
  });

  it("no-ops when schema already matches", async () => {
    vi.mocked(getMigrations).mockResolvedValue({
      toBeCreated: [],
      toBeAdded: [],
      runMigrations: vi.fn(),
      compileMigrations: vi.fn(),
    });
    await ensureAuthSchema();
    expect(getMigrations).toHaveBeenCalledOnce();
  });

  it("runs migrations when tables missing", async () => {
    const runMigrations = vi.fn().mockResolvedValue(undefined);
    vi.mocked(getMigrations).mockResolvedValue({
      toBeCreated: [{ table: "user" }],
      toBeAdded: [],
      runMigrations,
      compileMigrations: vi.fn(),
    });
    await ensureAuthSchema();
    expect(runMigrations).toHaveBeenCalledOnce();
  });
});
