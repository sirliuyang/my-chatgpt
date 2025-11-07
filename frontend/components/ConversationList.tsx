"use client";

import {useEffect, useState} from "react";
import {getConversations, createConversation} from "../lib/api";

interface Conversation {
    id: string;
    title: string; // Assume backend provides title or generate one
}

interface Props {
    selectedId: string | null;
    onSelect: (id: string) => void;
}

export default function ConversationList({selectedId, onSelect}: Props) {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchConversations();
    }, []);

    const fetchConversations = async () => {
        try {
            const data = await getConversations();
            setConversations(data);
        } catch (err) {
            setError("Failed to load conversations");
        } finally {
            setLoading(false);
        }
    };

    const handleCreateNew = async () => {
        try {
            const newConv = await createConversation();
            setConversations([...conversations, newConv]);
            onSelect(newConv.id);
        } catch (err) {
            setError("Failed to create new conversation");
        }
    };

    if (loading) return <div className="p-4">Loading...</div>;
    if (error) return <div className="p-4 text-red-500">{error}</div>;

    return (
        <div className="p-4">
            <button
                onClick={handleCreateNew}
                className="mb-4 px-4 py-2 bg-blue-500 text-white rounded"
            >
                New Conversation
            </button>
            <ul>
                {conversations.map((conv) => (
                    <li
                        key={conv.id}
                        onClick={() => onSelect(conv.id)}
                        className={`cursor-pointer p-2 ${selectedId === conv.id ? "bg-blue-100" : ""}`}
                    >
                        {conv.title || `Conversation ${conv.id}`}
                    </li>
                ))}
            </ul>
        </div>
    );
}