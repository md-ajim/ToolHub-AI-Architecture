import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  async rewrites() {
    // Docker: `backend` resolves via compose networking. Host `next dev`:
    // set BACKEND_URL=http://localhost:8000 (DNS `backend` is unreachable
    // on the host, which previously made every /api + /media call fail).
    const backendTarget =
      process.env.BACKEND_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://backend:8000';
    return [
      {
        source: '/api/:path*/',
        destination: `${backendTarget}/api/:path*/`,
      },
      {
        source: '/api/:path*',
        destination: `${backendTarget}/api/:path*`,
      },
      {
        source: '/media/:path*',
        destination: `${backendTarget}/media/:path*`,
      },
    ];
  },
};

export default nextConfig;
