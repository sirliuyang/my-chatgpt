// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
'use client';

import React, {useState} from 'react';

interface ToolCall {
    toolCallId: string;
    toolName: string;
    argsRaw: string; // assembled JSON or text
    parentMessageId?: string | null;
}

interface Props {
    toolCall: ToolCall;
    onApprove: (toolCallId: string, resultContent: string) => void;
    onReject: (toolCallId: string) => void;
    onClose?: () => void;
}

/**
 * Simple UI to show tool call info, allow user to edit arguments, and Approve/Reject.
 * - resultContent: free text string returned as tool result (will be sent back to server).
 */
export default function ToolCallPanel({toolCall, onApprove, onReject, onClose}: Props) {
    const [editedArgs, setEditedArgs] = useState(toolCall.argsRaw ?? '');
    const [resultContent, setResultContent] = useState<string>('');

    return (
        <div className="fixed bottom-6 right-6 w-96 bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-4 z-50">
            <div className="flex items-start justify-between gap-2">
                <div>
                    <div className="text-sm text-gray-300">Tool call</div>
                    <div className="text-lg font-medium text-white">{toolCall.toolName}</div>
                    {toolCall.parentMessageId && <div className="text-xs text-gray-400">parent: {toolCall.parentMessageId}</div>}
                </div>
                <button
                    className="text-gray-400 hover:text-gray-200"
                    onClick={() => onClose?.()}
                    aria-label="Close"
                >
                    ✕
                </button>
            </div>

            <div className="mt-3">
                <div className="text-xs text-gray-400 mb-1">Arguments (editable)</div>
                <textarea
                    value={editedArgs}
                    onChange={(e) => setEditedArgs(e.target.value)}
                    rows={4}
                    className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm text-white"
                />
            </div>

            <div className="mt-3">
                <div className="text-xs text-gray-400 mb-1">Result to send back (tool result)</div>
                <textarea
                    placeholder="Enter result (string or JSON). This will be attached as the tool message."
                    value={resultContent}
                    onChange={(e) => setResultContent(e.target.value)}
                    rows={3}
                    className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm text-white"
                />
            </div>

            <div className="mt-3 flex gap-2">
                <button
                    className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 rounded"
                    onClick={() => onApprove(toolCall.toolCallId, resultContent || editedArgs)}
                >
                    Approve / Send result
                </button>
                <button
                    className="bg-red-700 hover:bg-red-600 text-white py-2 px-3 rounded"
                    onClick={() => onReject(toolCall.toolCallId)}
                >
                    Reject
                </button>
            </div>
        </div>
    );
}
