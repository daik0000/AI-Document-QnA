import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import client from '../api/client';

export default function Chat() {
    const { documentId } = useParams();
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState('');
    const [sending, setSending] = useState(false);
    const [error, setError] = useState('');
    const bottomRef = useRef(null);

    useEffect(() => {
        const initSession = async () => {
            try {
                const res = await client.post('/chat/sessions', {
                    document_id: Number(documentId),
                });
                setSessionId(res.data.id);

                const history = await client.get(`/chat/sessions/${res.data.id}/history`);
                setMessages(history.data);
            } catch (err) {
                setError(err.response?.data?.detail || 'Không tạo được phiên chat');
            }
        };
        initSession();
    }, [documentId]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!question.trim() || !sessionId) return;

        const q = question;
        const userMessage = { role: 'user', content: q, id: `temp-${Date.now()}` };
        const assistantId = `temp-assistant-${Date.now()}`;
        setMessages((prev) => [
            ...prev, 
            userMessage,
            {
                id: assistantId,
                role: 'assistant',
                content: '',
                source_chunks: [],
            }    
        ]);
        setQuestion('');
        setSending(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(
                `http://localhost:8000/chat/sessions/${sessionId}/message/stream`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({ question: q }),
                }
            );

            if (!res.ok) {
                throw new Error('Gửi câu hỏi thất bại');
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n\n');
                buffer = parts.pop();

                for (const part of parts) {
                    if (!part.startsWith('data: ')) continue;
                    const event = JSON.parse(part.slice(6));

                    if (event.type === 'chunk') {
                        setMessages((prev) => prev.map((msg) =>
                            msg.id === assistantId
                                ? { ...msg, content: msg.content + event.text }
                                : msg
                        ));
                    }
                    else if (event.type === 'done') {
                        setMessages((prev) => prev.map((msg) =>
                            msg.id === assistantId
                                ? { ...msg, id: event.message_id, source_chunks: event.source_chunks }
                                : msg
                        ));
                    }
                }
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Gửi câu hỏi thất bại');
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 flex flex-col h-screen">
            <div className="flex items-center gap-3 mb-4">
                <Link to="/" className="text-sm text-gray-500 hover:underline">← Quay lại</Link>
                <h1 className="text-lg font-semibold">Hỏi đáp tài liệu</h1>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 mb-4">
                {messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}
                {sending && <p className="text-sm text-gray-400">Đang trả lời...</p>}
                <div ref={bottomRef} />
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 text-sm p-2 rounded mb-2">{error}</div>
            )}

            <form onSubmit={handleSend} className="flex gap-2">
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Hỏi gì đó về tài liệu..."
                    disabled={sending || !sessionId}
                    className="flex-1 border rounded px-3 py-2"
                />
                <button
                    type="submit"
                    disabled={sending || !sessionId}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    Gửi
                </button>
            </form>
        </div>
    );
}

function MessageBubble({ message }) {
    const isUser = message.role === 'user';
    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[75%] rounded-lg px-4 py-2 ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'
                    }`}
            >
                <p className="whitespace-pre-wrap">{message.content}</p>

                {!isUser && message.source_chunks?.length > 0 && (
                    <details className="mt-2 text-xs opacity-75">
                        <summary className="cursor-pointer">Nguồn trích dẫn ({message.source_chunks.length})</summary>
                        <div className="mt-1 space-y-1">
                            {message.source_chunks.map((chunk, i) => (
                                <p key={i} className="border-l-2 border-gray-300 pl-2">
                                    {chunk.text.slice(0, 150)}...
                                </p>
                            ))}
                        </div>
                    </details>
                )}
            </div>
        </div>
    );
}
