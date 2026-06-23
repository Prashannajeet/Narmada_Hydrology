/** @type {import('next').NextConfig} */
const isStaticExport = process.env.NEXT_OUTPUT === "export";

const nextConfig = {
  output: isStaticExport ? "export" : "standalone",
  images: {
    unoptimized: isStaticExport
  },
  eslint: {
    ignoreDuringBuilds: true
  }
};

export default nextConfig;
