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

        const userMessage = { role: 'user', content: question, id: `temp-${Date.now()}` };
        setMessages((prev) => [...prev, userMessage]);
        setQuestion('');
        setSending(true);
        setError('');

        try {
            const res = await client.post(`/chat/sessions/${sessionId}/message`, {
                question: userMessage.content,
            });
            setMessages((prev) => [...prev, res.data]);
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
