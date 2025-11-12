// app/not-found.tsx
import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
            <div className="max-w-md w-full text-center">
                <div className="size-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg
                        className="size-8 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                </div>

                <h2 className="text-2xl font-bold text-white mb-2">
                    Page not found
                </h2>

                <p className="text-gray-400 mb-6">
                    The page you are looking for does not exist.
                </p>

                <Link
                    href="/"
                    className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                    Go back home
                </Link>
            </div>
        </div>
    );
}