import { describe, it, expect } from "vitest";

import nextConfig from "./next.config";

describe("next.config", () => {
  it("config_disables_powered_by_header", () => {
    expect(nextConfig.poweredByHeader).toBe(false);
  });

  it("config_still_has_output_standalone", () => {
    expect(nextConfig.output).toBe("standalone");
  });
});
