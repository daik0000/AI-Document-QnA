import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(email, password, fullName);
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || 'Đăng ký thất bại');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <form
                onSubmit={handleSubmit}
                className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm"
            >
                <h1 className="text-2xl font-bold mb-6">Đăng ký</h1>

                {error && (
                    <div className="bg-red-50 text-red-600 text-sm p-2 rounded mb-4">
                        {error}
                    </div>
                )}

                <input
                    type="text"
                    placeholder="Họ tên"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-3"
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-3"
                    required
                />
                <input
                    type="password"
                    placeholder="Mật khẩu"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-4"
                    required
                />

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    {loading ? 'Đang đăng ký...' : 'Đăng ký'}
                </button>

                <p className="text-sm text-center mt-4">
                    Đã có tài khoản? <Link to="/login" className="text-blue-600">Đăng nhập</Link>
                </p>
            </form>
        </div>
    );
}