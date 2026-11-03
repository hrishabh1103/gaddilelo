import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
    ];
  },
  images: {
    domains: [
      "images.unsplash.com",
      "lh3.googleusercontent.com",
      "avatars.githubusercontent.com",
      "imgd.aeplcdn.com",
    ],
  },
};

export default nextConfig;
