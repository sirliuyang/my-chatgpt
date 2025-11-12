// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
'use client';

import {useEffect, useRef, useState, type UIEvent} from 'react';
import ChatBubble from './ChatBubble';
import InputField from './InputField';
import ToolCallPanel from './ToolCallPanel';
import type {Message} from '@/lib/api';

type ToolCall = {
    toolCallId: string;
    toolName: string;
    argsRaw: string;
    parentMessageId?: string | null;
};

interface ChatProps {
    messages: Message[];
    onSendMessage: (message: string) => void;
    isLoading: boolean;
    streamingContent: string;
    error: string | null;
    onDismissError?: () => void;
    toolCall?: ToolCall | null;
    onApproveToolCall?: (toolCallId: string, resultContent: string) => void;
    onRejectToolCall?: (toolCallId: string) => void;
    onCloseToolCall?: () => void;
}

// helper: format timestamp (if timestamp missing, return empty)
const formatTime = (ts?: string) => {
    try {
        if (!ts) return '';
        const d = new Date(ts);
        return d.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    } catch {
        return '';
    }
};

export default function Chat({
                                 messages,
                                 onSendMessage,
                                 isLoading,
                                 streamingContent,
                                 error,
                                 onDismissError,
                                 toolCall,
                                 onApproveToolCall,
                                 onRejectToolCall,
                                 onCloseToolCall,
                             }: ChatProps) {
    const scrollContainerRef = useRef<HTMLDivElement | null>(null);
    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    const [autoScroll, setAutoScroll] = useState(true);
    const [criticalErrors, setCriticalErrors] = useState<Array<{timestamp: string, details: any}>>([]);
    const prevMessagesLengthRef = useRef(messages.length);

    // 监控 messages 数组的变化，检测异常清空 - 增强版
    useEffect(() => {
        if (prevMessagesLengthRef.current > 0 && messages.length === 0 && !isLoading) {
            setCriticalErrors(prev => [...prev, {
                timestamp: new Date().toISOString(),
                details: {
                    prevLength: prevMessagesLengthRef.current,
                    currentLength: messages.length,
                    isLoading,
                    hasStreamingContent: !!streamingContent
                }
            }]);
        }
        prevMessagesLengthRef.current = messages.length;
    }, [messages.length, isLoading, streamingContent]);

    // 清理函数：组件卸载时重置状态
    useEffect(() => {
        return () => {
            console.debug('[Chat] Component unmounting, cleaning up...');
        };
    }, []);

    // scroll to bottom helper (smooth)
    const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
        try {
            messagesEndRef.current?.scrollIntoView({behavior, block: 'end'});
        } catch {
            // ignore
        }
    };

    // When messages or streaming content change, auto-scroll if user is at bottom
    useEffect(() => {
        if (autoScroll) {
            scrollToBottom('smooth');
        }
    }, [messages.length, streamingContent, autoScroll]);

    // detect if user scrolled up
    const handleScroll = (e: UIEvent<HTMLDivElement>) => {
        const el = e.currentTarget;
        const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 72; // tolerance
        setAutoScroll(isAtBottom);
    };

    // Determine empty state: only show welcome when truly nothing is happening
    const showEmptyState = messages.length === 0 && !isLoading && !error && !streamingContent && !toolCall;

    return (
        <div className="flex flex-col h-full bg-gray-900 text-sm text-white relative">
            {/* Inline styles for typing cursor animation */}
            <style>{`
        @keyframes typing-cursor {
          0% { opacity: 1; }
          50% { opacity: 0.15; }
          100% { opacity: 1; }
        }
        .typing-caret {
          display: inline-block;
          width: 8px;
          height: 18px;
          margin-left: 6px;
          background-color: rgba(255,255,255,0.85);
          border-radius: 2px;
          animation: typing-cursor 1s steps(2, start) infinite;
          vertical-align: text-bottom;
        }
      `}</style>

            {/* Messages container */}
            <div
                ref={scrollContainerRef}
                onScroll={handleScroll}
                className="flex-1 overflow-y-auto px-4 py-6"
                aria-live="polite"
            >
                <div className="mx-auto max-w-3xl">
                    {/* Empty / Welcome */}
                    {showEmptyState && (
                        <div className="flex items-center justify-center h-72">
                            <div className="text-center">
                                <div
                                    className="mx-auto mb-6 w-16 h-16 rounded-full bg-gradient-to-br from-indigo-700 to-indigo-500 flex items-center justify-center shadow-lg">
                                    <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
                                              d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                                    </svg>
                                </div>
                                <h3 className="text-2xl font-semibold mb-2">How can I help you today?</h3>
                                <p className="text-gray-300">Ask anything — code, questions, or requests. Press Enter to send.</p>
                            </div>
                        </div>
                    )}

                    {/* Chat messages */}
                    <div className="space-y-4">
                        {messages.map((msg) => {
                            const isUser = msg.role === 'user';
                            return (
                                <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`flex items-end gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : ''}`}>
                                        {/* Avatar */}
                                        <div className="flex-shrink-0">
                                            {isUser ? (
                                                <div
                                                    className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs text-gray-200">You</div>
                                            ) : (
                                                <div
                                                    className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-xs font-semibold">AI</div>
                                            )}
                                        </div>

                                        {/* Bubble */}
                                        <div className={`${isUser ? 'text-right' : 'text-left'}`}>
                                            <div
                                                className={`${isUser ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-100'} 
                                    px-4 py-2 rounded-2xl shadow-sm break-words whitespace-pre-wrap`}
                                            >
                                                <ChatBubble role={msg.role} content={msg.content} timestamp={msg.timestamp}/>
                                            </div>
                                            <div className="mt-1 text-[11px] text-gray-400">
                                                {formatTime(msg.timestamp)}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}

                        {/* Streaming bubble: render when there is streamingContent OR loading OR toolCall */}
                        {(streamingContent || isLoading || toolCall) && (
                            <div className="flex justify-start">
                                <div className="flex items-end gap-3 max-w-[85%]">
                                    {/* assistant avatar */}
                                    <div className="flex-shrink-0">
                                        <div
                                            className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-xs font-semibold">AI
                                        </div>
                                    </div>

                                    {/* streaming bubble */}
                                    <div className="text-left">
                                        <div
                                            className={`bg-gray-800 text-gray-100 px-4 py-2 rounded-2xl shadow-sm break-words whitespace-pre-wrap`}
                                            aria-live="polite"
                                        >
                                            {streamingContent ? (
                                                <span>{streamingContent}</span>
                                            ) : toolCall ? (
                                                <span className="text-gray-400">
                                                    🔧 正在执行工具: {toolCall.toolName}...
                                                </span>
                                            ) : (
                                                <span className="text-gray-400">正在思考...</span>
                                            )}

                                            {/* typing caret only when actively streaming text */}
                                            {streamingContent && isLoading && (
                                                <span className="typing-caret" aria-hidden="true"/>
                                            )}
                                        </div>

                                        <div className="mt-1 text-[11px] text-gray-400">
                                            {toolCall ? '工具调用中...' : isLoading ? '正在输入...' : ''}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef}/>
                    </div>
                </div>
            </div>

            {/* Error area */}
            {error && (
                <div className="border-t border-gray-800 bg-gray-800 px-4 py-3">
                    <div className="max-w-3xl mx-auto">
                        <div className="bg-red-900/20 border border-red-800 text-red-400 px-4 py-3 rounded-lg flex items-start gap-3">
                            <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <div className="flex-1">
                                <p className="text-sm font-medium">Error</p>
                                <p className="text-xs mt-1">{error}</p>
                            </div>
                            {onDismissError && (
                                <button
                                    type="button"
                                    onClick={onDismissError}
                                    className="shrink-0 text-red-400 hover:text-red-300"
                                    aria-label="Dismiss error"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                                    </svg>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Input area */}
            <div className="border-t border-gray-800 bg-gray-900 px-4 py-4">
                <div className="max-w-3xl mx-auto">
                    <InputField onSend={onSendMessage} disabled={isLoading}/>
                </div>
            </div>

            {/* Tool Call Panel - 仅在工具调用需要手动批准时显示 */}
            {toolCall && onApproveToolCall && onRejectToolCall && !streamingContent && (
                <ToolCallPanel
                    toolCall={toolCall}
                    onApprove={onApproveToolCall}
                    onReject={onRejectToolCall}
                    onClose={onCloseToolCall}
                />
            )}
        </div>
    );
}