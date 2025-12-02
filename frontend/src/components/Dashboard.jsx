// frontend/src/components/Dashboard.jsx
import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Dashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">
            AskVoilet Dashboard
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">
              Welcome, <strong>{user?.username}</strong>
            </span>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">
            🎉 Login Successful!
          </h2>
          <p className="text-gray-600 mb-4">
            You have successfully logged into your AskVoilet account. Your authentication token is stored securely.
          </p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800">
              ✅ Authentication Status: <strong>Active</strong>
            </p>
            <p className="text-green-800 mt-2">
              🔐 Token: <code className="text-xs">{localStorage.getItem('token')?.substring(0, 30)}...</code>
            </p>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-2 text-purple-600">
              📄 Upload PDFs
            </h3>
            <p className="text-gray-600">
              Upload and chat with your PDF documents using AI.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-2 text-purple-600">
              💬 Ask Questions
            </h3>
            <p className="text-gray-600">
              Get instant answers from your uploaded documents.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-2 text-purple-600">
              📊 Extract Tables
            </h3>
            <p className="text-gray-600">
              Automatically extract and query data from tables.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;