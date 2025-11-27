import React from "react";
import { BookOpen, Upload, User, LogOut } from "lucide-react";

const Header = ({ username, onUploadClick, onLogout }) => (
  <header className="bg-white border-b border-gray-200 px-6 py-4">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center">
          <BookOpen className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Voilet</h1>
          <p className="text-xs text-gray-500">PDF Q&A Assistant</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={onUploadClick}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 transition-colors flex items-center gap-2"
        >
          <Upload className="w-4 h-4" />
          Upload PDFs
        </button>

        <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
          <User className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">{username}</span>
        </div>

        <button
          onClick={onLogout}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Logout"
        >
          <LogOut className="w-5 h-5 text-gray-600" />
        </button>
      </div>
    </div>
  </header>
);

export default Header;
