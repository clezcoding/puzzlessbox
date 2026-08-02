import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
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
