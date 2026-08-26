import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: [
    "@everything-agentic/api",
    "@everything-agentic/database",
    "@everything-agentic/domain",
    "@everything-agentic/ui",
  ],
};

export default nextConfig;
