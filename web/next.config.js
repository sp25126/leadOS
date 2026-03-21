/** @type {import('next').NextConfig} */
const nextConfig = {
  // Required for Cloudflare Workers runtime
  // Do NOT use 'standalone' — that's for Docker/Node only
  output: undefined,

  // No rewrites needed as apiCall in lib/api.ts uses absolute BASE_URL

  // Image domains — whitelist your API domain
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "api.webrox.xyz",
      },
    ],
  },

  experimental: { optimizePackageImports: ["framer-motion"] },
  headers: async () => [{
    source: "/videos/:path*",
    headers: [{
      key: "Cache-Control",
      value: "public, max-age=31536000, immutable",
    }],
  }],

  // Silence Cloudflare-irrelevant warnings
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
}

module.exports = nextConfig
