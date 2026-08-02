import { describe, it, expect } from "vitest";

import { GET } from "./route";

describe("GET /api/health", () => {
  it("returns 200 with JSON body { status: 'ok' }", async () => {
    const res = await GET();
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ status: "ok" });
  });

  it("does not require auth", async () => {
    const res = await GET();
    expect(res.status).toBe(200);
    expect(res.headers.get("www-authenticate")).toBeNull();
  });

  it("is lightweight — no db field in response", async () => {
    const res = await GET();
    const body = await res.json();
    expect(body).not.toHaveProperty("db");
    expect(Object.keys(body)).toEqual(["status"]);
  });
});
