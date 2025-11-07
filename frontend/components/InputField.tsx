"use client";

import React, {useState} from "react";

interface Props {
    onSend: (message: string) => void;
    disabled: boolean;
}

export default function InputField({onSend, disabled}: Props) {
    const [message, setMessage] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (message.trim()) {
            onSend(message);
            setMessage("");
        }
    };

    return (
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none"
                    disabled={disabled}
                />
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded-r-lg"
                    disabled={disabled}
                >
                    Send
                </button>
            </div>
        </form>
    );
}