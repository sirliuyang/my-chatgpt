// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
'use client';

import {useEffect} from 'react';

export default function Error({
                                  error,
                                  reset,
                              }: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // 只在开发环境打印错误
        if (process.env.NODE_ENV === 'development') {
            console.error('Application error:', error);
        }
    }, [error]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
            <div className="max-w-md w-full text-center">
                <div className="size-16 bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-800">
                    <svg
                        className="size-8 text-red-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                </div>

                <h2 className="text-2xl font-bold text-white mb-2">
                    Something went wrong
                </h2>

                <p className="text-gray-400 mb-6">
                    We encountered an unexpected error. Please try again.
                </p>

                <button
                    type="button"
                    onClick={reset}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                    Try again
                </button>
            </div>
        </div>
    );
}