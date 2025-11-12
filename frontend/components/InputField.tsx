// components/InputField.tsx
'use client';

import {useState, useRef, useEffect, type KeyboardEvent, type ChangeEvent} from 'react';

interface InputFieldProps {
    onSend: (message: string) => void;
    disabled?: boolean;
    placeholder?: string;
}

export default function InputField({
                                       onSend,
                                       disabled = false,
                                       placeholder = 'Send a message...'
                                   }: InputFieldProps) {
    const [message, setMessage] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        const trimmedMessage = message.trim();
        if (trimmedMessage && !disabled) {
            onSend(trimmedMessage);
            setMessage('');
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value);
    };

    // Auto-resize textarea
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
        }
    }, [message]);

    return (
        <div className="border-t border-gray-700 bg-gray-800 p-4">
            <div className="max-w-3xl mx-auto">
                <div className="relative flex items-end gap-2 bg-gray-700 rounded-xl p-2">
          <textarea
              ref={textareaRef}
              value={message}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className="flex-1 resize-none bg-transparent px-3 py-2 text-white placeholder-gray-400 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed max-h-[200px] overflow-y-auto"
          />
                    <button
                        type="button"
                        onClick={handleSend}
                        disabled={disabled || !message.trim()}
                        className="shrink-0 p-2 bg-white text-gray-900 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white transition-colors"
                        aria-label="Send message"
                    >
                        <svg className="size-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                        </svg>
                    </button>
                </div>
                <p className="text-xs text-gray-500 text-center mt-2">
                    Press Enter to send, Shift+Enter for new line
                </p>
            </div>
        </div>
    );
}