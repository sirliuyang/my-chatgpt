const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/v1/:path*',
                destination: `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.yourdomain.com'}/api/v1/:path*`,
            },
        ];
    }
};

module.exports = nextConfig;