// components/ChatBubble.tsx
'use client';

import {memo} from 'react';
import ReactMarkdown from 'react-markdown';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter';
import {vscDarkPlus} from 'react-syntax-highlighter/dist/cjs/styles/prism';
import remarkGfm from 'remark-gfm';

interface ChatBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

function ChatBubble({role, content, timestamp}: ChatBubbleProps) {
    const isUser = role === 'user';

    // 自定义代码块渲染器
    const CodeBlock = ({children, className, ...props}: any) => {
        const match = /language-(\w+)/.exec(className || '');
        const language = match ? match[1] : '';
        
        return match ? (
            <div className="my-3 rounded-lg overflow-hidden border border-gray-700 bg-black">
                <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
                    <span className="text-xs text-gray-400">{language}</span>
                    <button
                        type="button"
                        onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                        className="text-xs text-gray-400 hover:text-white transition-colors px-2 py-1 rounded hover:bg-gray-700"
                    >
                        复制代码
                    </button>
                </div>
                <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={language}
                    PreTag="div"
                    className="p-0 m-0"
                    {...props}
                >
                    {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
            </div>
        ) : (
            <code className="bg-gray-800 px-1 py-0.5 rounded text-sm font-mono text-gray-200" {...props}>
                {children}
            </code>
        );
    };

    // Markdown组件配置
    const MarkdownComponents = {
        code: CodeBlock,
        // 自定义段落样式
        p: ({children}: any) => <p className="mb-4 last:mb-0">{children}</p>,
        // 自定义标题样式
        h1: ({children}: any) => <h1 className="text-2xl font-bold mb-4 mt-6">{children}</h1>,
        h2: ({children}: any) => <h2 className="text-xl font-bold mb-3 mt-5">{children}</h2>,
        h3: ({children}: any) => <h3 className="text-lg font-bold mb-2 mt-4">{children}</h3>,
        // 自定义列表样式
        ul: ({children}: any) => <ul className="list-disc list-inside mb-4">{children}</ul>,
        ol: ({children}: any) => <ol className="list-decimal list-inside mb-4">{children}</ol>,
        li: ({children}: any) => <li className="mb-1">{children}</li>,
        // 自定义链接样式
        a: ({href, children}: any) => (
            <a href={href} className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noopener noreferrer">
                {children}
            </a>
        ),
        // 自定义表格样式
        table: ({children}: any) => (
            <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-gray-700">{children}</table>
            </div>
        ),
        thead: ({children}: any) => <thead className="bg-gray-800">{children}</thead>,
        tbody: ({children}: any) => <tbody>{children}</tbody>,
        tr: ({children}: any) => <tr className="border-b border-gray-700">{children}</tr>,
        th: ({children}: any) => <th className="border border-gray-700 px-4 py-2 text-left">{children}</th>,
        td: ({children}: any) => <td className="border border-gray-700 px-4 py-2">{children}</td>,
        // 自定义引用样式
        blockquote: ({children}: any) => (
            <blockquote className="border-l-4 border-gray-600 pl-4 my-4 italic text-gray-300">
                {children}
            </blockquote>
        ),
        // 自定义水平线样式
        hr: () => <hr className="border-gray-700 my-6" />,
    };

    return (
        <div className={`group w-full border-b border-gray-700 ${isUser ? 'bg-gray-800' : 'bg-gray-900'}`}>
            <div className="max-w-3xl mx-auto px-4 py-6 flex gap-6">
                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="text-gray-100 text-base leading-7 prose prose-invert max-w-none">
                        {isUser ? (
                            <p className="whitespace-pre-wrap break-words">{content}</p>
                        ) : (
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={MarkdownComponents}
                            >
                                {content}
                            </ReactMarkdown>
                        )}
                    </div>

                    {/* Timestamp */}
                    {timestamp && (
                        <div className="mt-2 text-xs text-gray-500">
                            {new Date(timestamp).toLocaleTimeString()}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default memo(ChatBubble);