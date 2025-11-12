// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
'use client';

import type {Conversation} from '@/lib/api';

interface ConversationListProps {
    conversations: Conversation[];
    currentConversationId: number | null;
    onSelectConversation: (id: number) => void;
    onNewConversation: () => void;
    loading?: boolean;
}

export default function ConversationList({
                                             conversations,
                                             currentConversationId,
                                             onSelectConversation,
                                             onNewConversation,
                                             loading = false,
                                         }: ConversationListProps) {
    return (
        <div className="w-64 bg-gray-900 flex flex-col h-screen border-r border-gray-700">
            {/* Header with New Chat Button */}
            <div className="p-3">
                <button
                    type="button"
                    onClick={onNewConversation}
                    className="w-full flex items-center gap-3 px-3 py-3 text-sm text-white border border-gray-700 rounded-lg hover:bg-gray-800 transition-colors"
                >
                    <svg className="size-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
                    </svg>
                    <span className="font-medium">New chat</span>
                </button>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto px-2">
                {loading ? (
                    <div className="flex items-center justify-center py-8">
                        <div className="size-5 border-2 border-gray-600 border-t-white rounded-full animate-spin"/>
                    </div>
                ) : conversations.length === 0 ? (
                    <div className="text-center py-8 text-gray-500 text-sm">
                        No conversations yet
                    </div>
                ) : (
                    <div className="space-y-1">
                        {conversations.map((conv) => {
                            const isActive = currentConversationId === conv.id;
                            return (
                                <button
                                    type="button"
                                    key={conv.id}
                                    onClick={() => onSelectConversation(conv.id)}
                                    className={`w-full text-left px-3 py-3 rounded-lg transition-colors group ${
                                        isActive
                                            ? 'bg-gray-800 text-white'
                                            : 'text-gray-300 hover:bg-gray-800'
                                    }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <svg className="size-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                                            />
                                        </svg>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium truncate">
                                                Chat {conv.id}
                                            </p>
                                            <p className="text-xs text-gray-500 truncate">
                                                {new Date(conv.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="border-t border-gray-700 p-3">
                <div className="text-xs text-gray-500 text-center">
                    Leon AI
                </div>
            </div>
        </div>
    );
}