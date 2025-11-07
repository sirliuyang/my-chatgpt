"use client";

import {useState} from "react";
import ConversationList from "../components/ConversationList";
import Chat from "../components/Chat";

export default function Home() {
    const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);

    return (
        <main className="flex h-screen overflow-hidden">
            {/* Sidebar for conversations (hidden on mobile, shown on desktop) */}
            <aside className="w-1/4 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 hidden md:block">
                <ConversationList
                    selectedId={selectedConversationId}
                    onSelect={(id) => setSelectedConversationId(id)}
                />
            </aside>
            {/* Main chat area */}
            <section className="flex-1 flex flex-col">
                <Chat conversationId={selectedConversationId}/>
            </section>
        </main>
    );
}