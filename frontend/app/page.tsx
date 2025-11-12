// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
'use client';
import React, {useState, useEffect, useCallback, useRef} from 'react';
import Chat from '@/components/Chat';
import ConversationList from '@/components/ConversationList';
import ProtectedRoute from '@/components/ProtectedRoute';
import UserMenu from '@/components/UserMenu';
import {
    getConversations,
    getConversationHistory,
    createConversation,
    sendMessage,
    type Conversation,
    type Message,
} from '@/lib/api';
import {runAgUi, type AgUiEvent} from '@/lib/agui';
import {AuthManager} from '@/lib/auth';

type ToolCall = {
    toolCallId: string;
    toolName: string;
    argsRaw: string;
    parentMessageId?: string | null;
};

export default function Home() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [streamingContent, setStreamingContent] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [conversationsLoading, setConversationsLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [currentToolCall, setCurrentToolCall] = useState<ToolCall | null>(null);
    const [useAgui, setUseAgui] = useState(false);
    const [currentRunId, setCurrentRunId] = useState<string | null>(null);

    const handledToolCallIdsRef = useRef<Set<string>>(new Set());
    const isAguiActiveRef = useRef(false);
    const aguiConversationIdRef = useRef<number | null>(null);
    const streamingContentRef = useRef('');

    useEffect(() => {
        void loadConversations();
    }, []);

    const loadConversations = useCallback(async () => {
        try {
            setConversationsLoading(true);
            const convs = await getConversations();
            setConversations(convs);
        } catch (err) {
            console.error('Failed to load conversations:', err);
        } finally {
            setConversationsLoading(false);
        }
    }, []);

    const loadConversationHistory = useCallback(async (id: number, forceReload = false) => {
        try {
            // 只有在 AG-UI 活动且不是强制重载时才跳过
            if (isAguiActiveRef.current && !forceReload) {
                console.log('[LoadHistory] Skipping load - AG-UI active, not forced');
                return;
            }

            console.log('[LoadHistory] Loading conversation:', id, 'forceReload:', forceReload);
            setIsLoading(true);
            setError(null);

            const history = await getConversationHistory(id);
            console.log('[LoadHistory] Loaded', history.length, 'messages');

            // 总是更新消息
            setMessages(history);
            setCurrentConversationId(id);

            // 如果正在切换会话（不同于当前 AG-UI 会话），重置 AG-UI 状态
            if (id !== aguiConversationIdRef.current) {
                console.log('[LoadHistory] Different conversation, resetting AG-UI state');
                isAguiActiveRef.current = false;
                aguiConversationIdRef.current = null;
                setStreamingContent('');
                streamingContentRef.current = '';
                handledToolCallIdsRef.current.clear();
            }
        } catch (err) {
            console.error('Failed to load conversation history:', err);
            setError('Failed to load conversation. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    // 修复问题2：添加空对话检查
    const handleNewConversation = useCallback(async () => {
        // 如果当前有对话但还没有任何消息，则不创建新对话，只是清空状态
        if (currentConversationId && messages.length === 0) {
            console.log('[New Conversation] Current conversation is empty, reusing it');
            setStreamingContent('');
            streamingContentRef.current = '';
            setCurrentToolCall(null);
            handledToolCallIdsRef.current.clear();
            return;
        }

        // 否则创建新对话
        try {
            setError(null);
            const newConv = await createConversation();
            setConversations((prev) => [newConv, ...prev]);
            setCurrentConversationId(newConv.id);
            setMessages([]);
            setStreamingContent('');
            streamingContentRef.current = '';
            // 重置AGUI状态
            isAguiActiveRef.current = false;
            aguiConversationIdRef.current = null;
            handledToolCallIdsRef.current.clear();
        } catch (err) {
            console.error('Failed to create conversation:', err);
            setError('Failed to create conversation.');
        }
    }, [currentConversationId, messages.length]);

    const sendDeferredResults = useCallback(
        async (
            runId: string,
            threadId: string,
            toolCallId: string,
            approval: boolean | { override_args?: any },
            message?: string
        ) => {
            const tools = [
                {
                    name: 'duckduckgo_search',
                    description: 'Search the web',
                    parameters: {
                        type: 'object',
                        properties: {
                            query: {type: 'string'},
                            max_results: {type: 'number', default: 5},
                        },
                        required: ['query'],
                    },
                },
            ];

            const body = {
                run_id: runId,
                thread_id: threadId,
                messages: messages.map((m) => ({
                    id: String(m.id),
                    role: m.role,
                    content: m.content ?? '',
                })),
                deferred_results: [
                    {
                        tool_call_id: toolCallId,
                        approval: approval,
                        ...(message ? {message} : {}),
                    },
                ],
                state: {},
                context: [],
                forwarded_props: {},
            };

            const token = AuthManager.getAccessToken?.();
            const headers: Record<string, string> = {
                'Content-Type': 'application/json',
                Accept: 'text/event-stream',
            };
            if (token) headers.Authorization = `Bearer ${token}`;

            const url = `${window.location.origin}/api/v1/agui/deferred_results`;
            console.debug('[AG-UI] sendDeferredResults ->', toolCallId);

            const res = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(body),
                cache: 'no-cache',
            });

            if (!res.ok) {
                const text = await res.text().catch(() => '');
                throw new Error(`Deferred results failed: ${res.status}`);
            }

            const reader = res.body?.getReader();
            if (!reader) throw new Error('Response body not readable');

            const decoder = new TextDecoder();
            let buffer = '';

            const findDelimiter = (s: string) => {
                const idxRN = s.indexOf('\r\n\r\n');
                const idxN = s.indexOf('\n\n');
                if (idxRN !== -1 && (idxN === -1 || idxRN <= idxN)) return {idx: idxRN, len: 4};
                if (idxN !== -1) return {idx: idxN, len: 2};
                return {idx: -1, len: 0};
            };

            while (true) {
                const {done, value} = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, {stream: true});

                let delim = findDelimiter(buffer);
                while (delim.idx !== -1) {
                    const rawEvent = buffer.slice(0, delim.idx);
                    buffer = buffer.slice(delim.idx + delim.len);

                    const lines = rawEvent.split(/\r?\n/);
                    const dataLines: string[] = [];
                    for (const line of lines) {
                        if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
                    }
                    if (dataLines.length === 0) {
                        delim = findDelimiter(buffer);
                        continue;
                    }

                    const dataStr = dataLines.join('\n');

                    if (dataStr === '[DONE]') {
                        console.debug('[AG-UI] deferred_results [DONE]');
                        return;
                    }

                    let parsed: any = null;
                    try {
                        parsed = JSON.parse(dataStr);
                    } catch (e) {
                        delim = findDelimiter(buffer);
                        continue;
                    }

                    const t = (parsed.type ?? '').toString();
                    console.debug('[AG-UI] deferred_results event:', t);

                    if (t === 'TEXT_MESSAGE_CONTENT') {
                        const delta = parsed.delta ?? parsed.content ?? parsed.text ?? '';
                        if (delta) {
                            streamingContentRef.current += String(delta);
                            setStreamingContent(streamingContentRef.current);
                        }
                    } else if (t === 'tool_call' || parsed.tool_call_id) {
                        const newToolCallId = parsed.tool_call_id ?? '';
                        if (newToolCallId && !handledToolCallIdsRef.current.has(newToolCallId)) {
                            handledToolCallIdsRef.current.add(newToolCallId);
                            setCurrentToolCall({
                                toolCallId: newToolCallId,
                                toolName: parsed.tool_name ?? 'unknown',
                                argsRaw: JSON.stringify(parsed.args ?? {}, null, 2),
                                parentMessageId: null,
                            });

                            setTimeout(() => {
                                sendDeferredResults(runId, threadId, newToolCallId, true).catch(err => {
                                    console.error('[AG-UI] nested tool call failed:', err);
                                });
                            }, 100);
                        }
                    }

                    delim = findDelimiter(buffer);
                }
            }

            console.debug('[AG-UI] deferred_results stream complete');
        },
        [messages]
    );

    const handleSendMessage = useCallback(
        async (messageText: string) => {
            if (!messageText.trim()) return;

            let conversationId = currentConversationId;
            if (!conversationId) {
                try {
                    const newConv = await createConversation();
                    conversationId = newConv.id;
                    setConversations((prev) => [newConv, ...prev]);
                    setCurrentConversationId(newConv.id);
                    aguiConversationIdRef.current = newConv.id;
                } catch (err) {
                    console.error('Failed to create conversation:', err);
                    setError('Failed to create conversation. Please try again.');
                    return;
                }
            } else {
                aguiConversationIdRef.current = conversationId;
            }

            const historyForApi = messages.map((m) => ({
                id: m.id.toString(),
                role: m.role,
                content: m.content,
            }));

            const userMessageId = Date.now();
            const userMessage: Message = {
                id: userMessageId,
                conversation_id: conversationId,
                role: 'user',
                content: messageText,
                timestamp: new Date().toISOString(),
            };

            // 立即添加用户消息到界面
            setMessages((prev) => [...prev, userMessage]);
            setIsLoading(true);
            setStreamingContent('');
            streamingContentRef.current = '';
            setError(null);

            if (useAgui) {
                console.log('[AG-UI] Starting AG-UI session');
                isAguiActiveRef.current = true;

                const runId = `run-${Date.now()}`;
                setCurrentRunId(runId);
                const threadId = conversationId.toString();
                const tools = [
                    {
                        name: 'duckduckgo_search',
                        description: 'Search the web',
                        parameters: {
                            type: 'object',
                            properties: {
                                query: {type: 'string'},
                                max_results: {type: 'number', default: 5},
                            },
                            required: ['query'],
                        },
                    },
                ];

                try {
                    await runAgUi(
                        {
                            run_id: runId,
                            thread_id: threadId,
                            messages: [...historyForApi, {id: userMessageId.toString(), role: 'user', content: messageText}],
                            tools,
                            state: {},
                            context: [],
                            forwarded_props: {},
                        },
                        (event: AgUiEvent) => {
                            let ev: any = event;
                            if (ev && typeof ev === 'object' && typeof ev.data === 'string') {
                                try {
                                    ev = JSON.parse(ev.data);
                                } catch (_e) {
                                }
                            }

                            const evType = (ev?.type ?? '').toString();
                            console.debug('[AG-UI] main event:', evType);

                            if (evType === 'TEXT_MESSAGE_CONTENT') {
                                const delta = ev.delta ?? ev.content ?? ev.text ?? '';
                                if (delta) {
                                    streamingContentRef.current += String(delta);
                                    setStreamingContent(streamingContentRef.current);
                                }
                                return;
                            }

                            if (evType.includes('tool') || ev.tool_call_id || ev.tool) {
                                const toolCallId = ev.tool_call_id ?? ev.toolCallId ?? ev.tool?.id ?? '';
                                if (toolCallId && !handledToolCallIdsRef.current.has(toolCallId)) {
                                    handledToolCallIdsRef.current.add(toolCallId);

                                    const toolName = ev.tool_name ?? ev.toolName ?? ev.tool?.name ?? 'unknown';
                                    const args = ev.args ?? ev.arguments ?? ev.tool?.args ?? {};

                                    setCurrentToolCall({
                                        toolCallId,
                                        toolName,
                                        argsRaw: JSON.stringify(args, null, 2),
                                        parentMessageId: ev.message_id ?? null,
                                    });

                                    console.debug('[AG-UI] auto-approving tool:', toolCallId);
                                    setTimeout(() => {
                                        sendDeferredResults(runId, threadId, toolCallId, true).catch(err => {
                                            console.error('[AG-UI] tool call failed:', err);
                                            handledToolCallIdsRef.current.delete(toolCallId);
                                            setError('Tool call failed.');
                                        });
                                    }, 100);
                                }
                                return;
                            }
                        },
                        () => {
                            console.debug('[AG-UI] Session complete');
                            const convId = aguiConversationIdRef.current;
                            const finalContent = streamingContentRef.current;

                            console.log('[AG-UI] Complete - convId:', convId, 'content length:', finalContent.length);

                            isAguiActiveRef.current = false;
                            setIsLoading(false);
                            setCurrentToolCall(null);
                            handledToolCallIdsRef.current.clear();

                            // 将流式内容添加到消息列表
                            if (finalContent && convId) {
                                const assistantMessage: Message = {
                                    id: Date.now(),
                                    conversation_id: convId,
                                    role: 'assistant',
                                    content: finalContent,
                                    timestamp: new Date().toISOString(),
                                };
                                setMessages((prev) => {
                                    console.log('[AG-UI] Adding assistant message, prev length:', prev.length);
                                    return [...prev, assistantMessage];
                                });
                                setStreamingContent('');
                                streamingContentRef.current = '';
                            }
                        },
                        (err: any) => {
                            console.error('[AG-UI] Session error:', err);
                            isAguiActiveRef.current = false;
                            setError('Failed to send message. Please try again.');
                            setIsLoading(false);
                            setStreamingContent('');
                            streamingContentRef.current = '';
                            setCurrentToolCall(null);
                            handledToolCallIdsRef.current.clear();
                        }
                    );
                } catch (err) {
                    console.error('[AG-UI] Exception:', err);
                    isAguiActiveRef.current = false;
                    setError('Request failed.');
                    setIsLoading(false);
                    setStreamingContent('');
                    streamingContentRef.current = '';
                }
            } else {
                // Normal mode
                await sendMessage(
                    {
                        conversation_id: conversationId,
                        message: messageText,
                        history: historyForApi,
                    },
                    (chunk) => {
                        setStreamingContent((prev) => prev + chunk);
                    },
                    () => {
                        if (conversationId) {
                            void loadConversationHistory(conversationId);
                        }
                        setStreamingContent('');
                        setIsLoading(false);
                    },
                    (err) => {
                        console.error('Failed to send message:', err);
                        setError('Failed to send message. Please try again.');
                        setIsLoading(false);
                        setStreamingContent('');
                    }
                );
            }
        },
        [useAgui, messages, currentConversationId, loadConversationHistory, sendDeferredResults]
    );

    const handleDismissError = useCallback(() => {
        setError(null);
    }, []);

    const handleApproveToolCall = useCallback(
        async (toolCallId: string, resultContent: string) => {
            if (!currentRunId || !currentConversationId) return;
            try {
                await sendDeferredResults(currentRunId, currentConversationId.toString(), toolCallId, true);
                setCurrentToolCall(null);
            } catch (err) {
                console.error('Manual approve failed:', err);
                setError('Failed to approve tool call.');
            }
        },
        [currentRunId, currentConversationId, sendDeferredResults]
    );

    const handleRejectToolCall = useCallback(
        async (toolCallId: string) => {
            if (!currentRunId || !currentConversationId) return;
            try {
                await sendDeferredResults(currentRunId, currentConversationId.toString(), toolCallId, false, 'Rejected');
                setCurrentToolCall(null);
            } catch (err) {
                console.error('Reject failed:', err);
                setError('Failed to reject tool call.');
            }
        },
        [currentRunId, currentConversationId, sendDeferredResults]
    );

    const handleCloseToolCall = useCallback(() => {
        setCurrentToolCall(null);
    }, []);

    // 修复问题1：移除切换模式时的强制重载逻辑
    const handleToggleAgui = useCallback(() => {
        const newMode = !useAgui;
        console.log('[AG-UI Toggle] Mode change:', useAgui, '->', newMode, 'convId:', currentConversationId);

        setUseAgui(newMode);

        // 如果从 AG-UI 切换到普通模式，重置状态但不重载历史
        if (!newMode) {
            console.log('[AG-UI Toggle] Switching to normal mode, preserving current history');

            // 重置 AG-UI 状态
            isAguiActiveRef.current = false;
            aguiConversationIdRef.current = null;
            setStreamingContent('');
            streamingContentRef.current = '';
            handledToolCallIdsRef.current.clear();

            // 不再调用 loadConversationHistory，避免覆盖当前消息
        }
    }, [useAgui, currentConversationId]);

    return (
        <ProtectedRoute>
            <div className="flex h-screen overflow-hidden bg-gray-900">
                <button
                    type="button"
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className="lg:hidden fixed top-4 left-4 z-50 bg-gray-800 text-white p-2 rounded-lg shadow-lg border border-gray-700"
                    aria-label="Toggle sidebar"
                >
                    <svg className="size-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/>
                    </svg>
                </button>

                <div
                    className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-transform duration-300 fixed lg:relative z-40 h-full`}>
                    <ConversationList
                        conversations={conversations}
                        currentConversationId={currentConversationId}
                        onSelectConversation={loadConversationHistory}
                        onNewConversation={handleNewConversation}
                        loading={conversationsLoading}
                    />
                </div>

                {isSidebarOpen &&
                    <button type="button" onClick={() => setIsSidebarOpen(false)} className="lg:hidden fixed inset-0 bg-black/50 z-30"
                            aria-label="Close sidebar"/>}

                <div className="flex-1 flex flex-col overflow-hidden">
                    <div className="border-b border-gray-700 bg-gray-800 px-4 py-2 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <h1 className="text-lg font-semibold text-white hidden sm:block">Leon AI</h1>
                            <button
                                type="button"
                                onClick={handleToggleAgui}
                                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${useAgui ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                            >
                                {useAgui ? 'AG-UI ON' : 'AG-UI OFF'}
                            </button>
                        </div>
                        <UserMenu/>
                    </div>

                    <div className="flex-1 overflow-hidden">
                        <Chat
                            messages={messages}
                            onSendMessage={handleSendMessage}
                            isLoading={isLoading}
                            streamingContent={streamingContent}
                            error={error}
                            onDismissError={handleDismissError}
                            toolCall={currentToolCall}
                            onApproveToolCall={handleApproveToolCall}
                            onRejectToolCall={handleRejectToolCall}
                            onCloseToolCall={handleCloseToolCall}
                        />
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
}