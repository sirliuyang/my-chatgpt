"use client";

import { useEffect, useState, useRef } from "react";
import ChatBubble from "./ChatBubble";
import InputField from "./InputField";
import LoadingIndicator from "./LoadingIndicator";
import { getConversationHistory, sendMessage } from "../lib/api";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface Props {
    conversationId: string | null;
}

export default function Chat({ conversationId }: Props) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [streamingContent, setStreamingContent] = useState("");
    const chatRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (conversationId) {
            loadHistory();
        } else {
            setMessages([]);
        }
    }, [conversationId]);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const history = await getConversationHistory(conversationId!);
            setMessages(history.messages || []); // Assume backend returns { messages: Message[] }
        } catch (err) {
            setError("Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async (message: string) => {
        if (!conversationId) return;
        setMessages((prev) => [...prev, { role: "user", content: message }]);
        setStreamingContent(""); // Reset for new stream
        setLoading(true);
        scrollToBottom();

        try {
            await sendMessage(conversationId, message, (chunk) => {
                setStreamingContent((prev) => prev + chunk);
                scrollToBottom();
            });
            setMessages((prev) => [...prev, { role: "assistant", content: streamingContent }]);
            setStreamingContent("");
        } catch (err) {
            setError("Failed to send message");
        } finally {
            setLoading(false);
        }
    };

    const scrollToBottom = () => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    };

    useEffect(scrollToBottom, [messages, streamingContent]);

    if (!conversationId) return <div className="flex-1 flex items-center justify-center">Select or create a conversation</div>;
    if (error) return <div className="p-4 text-red-500">{error}</div>;

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            <div ref={chatRef} className="flex-1 overflow-y-auto p-4">
                {messages.map((msg, index) => (
                    <ChatBubble key={index} role={msg.role} content={msg.content} />
                ))}
                {streamingContent && <ChatBubble role="assistant" content={streamingContent} />}
                {loading && <LoadingIndicator />}
            </div>
            <InputField onSend={handleSend} disabled={loading || !conversationId} />
        </div>
    );
}