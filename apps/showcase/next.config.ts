import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@everything-agentic/design-tokens"],
};

export default nextConfig;
