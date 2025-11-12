// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
import axios, {AxiosHeaders} from 'axios';
import {AuthManager} from './auth';

export interface Message {
    id: number;
    conversation_id: number;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export interface Conversation {
    id: number;
    created_at: string;
    messages?: Message[];
}

export interface ChatRequest {
    conversation_id?: number;
    message: string;
    history?: Array<{ role: string; content: string }>;
}

const API_BASE_URL = ''; // 建议在生产环境直接指向后端 URL（避免 Next.js API 路由代理造成缓冲）

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.request.use(
    (config) => {
        const token = AuthManager.getAccessToken();
        if (token) {
            if (!config.headers) {
                config.headers = new AxiosHeaders();
            }
            (config.headers as any).Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error?.response?.status === 401) {
            AuthManager.clearAuth();
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export async function getConversations(): Promise<Conversation[]> {
    const response = await apiClient.get<Conversation[]>('/api/v1/conversations');
    return response.data;
}

export async function getConversationHistory(id: number): Promise<Message[]> {
    const response = await apiClient.get<Message[]>(`/api/v1/conversations/${id}`);
    return response.data;
}

export async function createConversation(): Promise<Conversation> {
    const response = await apiClient.post<Conversation>('/api/v1/conversations');
    return response.data;
}

export async function sendMessage(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
): Promise<void> {
    try {
        const token = AuthManager.getAccessToken();
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
        };
        if (token) headers.Authorization = `Bearer ${token}`;

        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers,
            body: JSON.stringify(request),
            // 显式禁用缓存，减少代理缓存/合并概率
            cache: 'no-cache',
            // keepalive 允许在页面卸载时完成部分请求（非必需）
            keepalive: true,
        });

        if (!response.ok) {
            if (response.status === 401) {
                AuthManager.clearAuth();
                window.location.href = '/login';
                throw new Error('Authentication required');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('Response body is not readable');

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
                    if (line.startsWith('data:')) {
                        dataLines.push(line.slice(5).trim());
                    }
                }
                if (dataLines.length === 0) {
                    delim = findDelimiter(buffer);
                    continue;
                }
                const dataStr = dataLines.join('\n');

                if (dataStr === '[DONE]') {
                    onComplete();
                    return;
                }

                try {
                    const parsed = JSON.parse(dataStr);
                    if (parsed && typeof parsed === 'object' && 'content' in parsed) {
                        onChunk(String(parsed.content));
                    } else {
                        onChunk(typeof parsed === 'string' ? parsed : JSON.stringify(parsed));
                    }
                } catch (e) {
                    onChunk(dataStr);
                }

                delim = findDelimiter(buffer);
            }
        }

        onComplete();
    } catch (error) {
        onError(error instanceof Error ? error : new Error(String(error)));
    }
}
