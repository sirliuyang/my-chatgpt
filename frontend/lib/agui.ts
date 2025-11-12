// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
import {AuthManager} from './auth';

export type AgUiEvent = { type: string; [k: string]: any };

export async function runAgUi(
    runInput: any,
    onEvent: (ev: AgUiEvent) => void,
    onComplete: () => void,
    onError: (err: Error) => void
): Promise<void> {
    try {
        const token = AuthManager.getAccessToken?.();
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
        };
        if (token) headers.Authorization = `Bearer ${token}`;

        const bodyContent = JSON.stringify(runInput);
        console.debug('[AG-UI] runAgUi request:', bodyContent);

        const res = await fetch('/api/v1/agui/agent', {
            method: 'POST',
            headers,
            body: bodyContent,
            cache: 'no-cache',
        });

        if (!res.ok) {
            const txt = await res.text().catch(() => '');
            throw new Error(`AG-UI run failed: ${res.status} ${res.statusText} ${txt}`);
        }

        const reader = res.body?.getReader();
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
                    console.debug('[AG-UI] runAgUi: [DONE]');
                    onComplete();
                    return;
                }

                try {
                    const parsed = JSON.parse(dataStr);
                    console.debug('[AG-UI] runAgUi parsed event:', parsed);
                    onEvent(parsed as AgUiEvent);
                } catch (e) {
                    console.warn('[AG-UI] runAgUi non-JSON data:', dataStr.slice(0, 100));
                    onEvent({type: 'raw', raw: dataStr});
                }

                delim = findDelimiter(buffer);
            }
        }

        console.debug('[AG-UI] runAgUi stream ended');
        onComplete();
    } catch (err) {
        console.error('[AG-UI] runAgUi error:', err);
        onError(err instanceof Error ? err : new Error(String(err)));
    }
}