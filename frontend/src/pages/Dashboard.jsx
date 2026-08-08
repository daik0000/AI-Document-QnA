import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';

const STATUS_LABEL = {
    processing: { text: 'Đang xử lý', color: 'bg-yellow-100 text-yellow-700' },
    ready: { text: 'Sẵn sàng', color: 'bg-green-100 text-green-700' },
    failed: { text: 'Lỗi', color: 'bg-red-100 text-red-700' },
};

export default function Dashboard() {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [uploading, setUploading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const { user, logout } = useAuth();

    const fetchDocuments = useCallback(async () => {
        try {
            const res = await client.get('/documents');
            setDocuments(res.data);
        } catch (err) {
            setError('Không tải được danh sách tài liệu');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    useEffect(() => {
        const hasProcessing = documents.some((d) => d.status === 'processing');
        if (!hasProcessing) return;

        const interval = setInterval(() => {
            fetchDocuments();
        }, 3000);

        return () => clearInterval(interval);
    }, [documents, fetchDocuments]);

    const handleUpload = async (file) => {
        setError('');
        setUploading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            await client.post('/documents/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            await fetchDocuments();
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload thất bại');
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleUpload(file);
    };

    const handleFileInput = (e) => {
        const file = e.target.files[0];
        if (file) handleUpload(file);
    };

    const handleDelete = async (id) => {
        if (!confirm('Xóa tài liệu này?')) return;
        await client.delete(`/documents/${id}`);
        fetchDocuments();
    };

    return (
        <div className="max-w-3xl mx-auto p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Tài liệu của {user?.email}</h1>
                <button onClick={logout} className="text-sm text-gray-500 hover:underline">
                    Đăng xuất
                </button>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 text-sm p-2 rounded mb-4">{error}</div>
            )}

            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center mb-6 transition-colors ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                    }`}
            >
                {uploading ? (
                    <p className="text-gray-500">Đang upload...</p>
                ) : (
                    <>
                        <p className="text-gray-500 mb-2">Kéo thả file PDF/DOCX/TXT vào đây, hoặc</p>
                        <label className="inline-block bg-blue-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-blue-700">
                            Chọn file
                            <input
                                type="file"
                                accept=".pdf,.docx,.txt"
                                onChange={handleFileInput}
                                className="hidden"
                            />
                        </label>
                    </>
                )}
            </div>

            {loading ? (
                <p className="text-gray-500">Đang tải...</p>
            ) : documents.length === 0 ? (
                <p className="text-gray-500">Chưa có tài liệu nào.</p>
            ) : (
                <ul className="space-y-2">
                    {documents.map((doc) => {
                        const status = STATUS_LABEL[doc.status] || STATUS_LABEL.processing;
                        return (
                            <li
                                key={doc.id}
                                className="flex justify-between items-center bg-white border rounded-lg p-4"
                            >
                                <div>
                                    <p className="font-medium">{doc.filename}</p>
                                    <span className={`text-xs px-2 py-0.5 rounded ${status.color}`}>
                                        {status.text}
                                    </span>
                                    {doc.status === 'ready' && (
                                        <span className="text-xs text-gray-400 ml-2">
                                            {doc.num_chunks} đoạn
                                        </span>
                                    )}
                                </div>
                                <div className="flex gap-3">
                                    {doc.status === 'ready' && (
                                        <Link
                                            to={`/documents/${doc.id}/chat`}
                                            className="text-sm text-blue-600 hover:underline"
                                        >
                                            Chat
                                        </Link>
                                    )}
                                    <button
                                        onClick={() => handleDelete(doc.id)}
                                        className="text-sm text-red-500 hover:underline"
                                    >
                                        Xóa
                                    </button>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            )}
        </div>
    );
}