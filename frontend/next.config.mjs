/** @type {import('next').NextConfig} */
const nextConfig = {
    experimental: {
        allowedDevOrigins: ['*']
    },
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    images: {
        unoptimized: true,
    },
    output: 'standalone',
}

export default nextConfig
