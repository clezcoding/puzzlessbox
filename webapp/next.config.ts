import type { NextConfig } from "next";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  // webapp lives under repo root; brand/tokens.css is imported from globals.css.
  turbopack: {
    root: repoRoot,
  },
  outputFileTracingRoot: repoRoot,
  experimental: {
    // TypeScript 7 has no JS compiler API yet; next build must use local tsc CLI.
    useTypeScriptCli: true,
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.googleusercontent.com" },
      { protocol: "https", hostname: "**.ggpht.com" },
      { protocol: "https", hostname: "**.ytimg.com" },
      { protocol: "https", hostname: "**.githubusercontent.com" },
      { protocol: "https", hostname: "**.cloudfront.net" },
      { protocol: "https", hostname: "**.amazonaws.com" },
      { protocol: "https", hostname: "**.opengraph.xyz" },
      { protocol: "https", hostname: "**.notion.so" },
      { protocol: "https", hostname: "**.notion-static.com" },
    ],
  },
};

export default nextConfig;
