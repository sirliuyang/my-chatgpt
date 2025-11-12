// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
'use client';

export default function LoadingIndicator() {
    return (
        <div className="w-full border-b border-gray-700 bg-gray-900">
            <div className="max-w-3xl mx-auto px-4 py-6 flex gap-6">
                <div className="shrink-0">
                    <div className="size-8 rounded-sm flex items-center justify-center text-white font-semibold bg-green-600">
                        AI
                    </div>
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-1 py-2">
                        <div
                            className="size-2 bg-gray-400 rounded-full animate-bounce"
                            style={{animationDelay: '0ms'}}
                        />
                        <div
                            className="size-2 bg-gray-400 rounded-full animate-bounce"
                            style={{animationDelay: '150ms'}}
                        />
                        <div
                            className="size-2 bg-gray-400 rounded-full animate-bounce"
                            style={{animationDelay: '300ms'}}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}