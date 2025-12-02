import React, { useState, useEffect, useRef } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import AuthForm from "./components/AuthForm";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import UploadModal from "./components/UploadModal";
import Notification from "./components/Notification";

const API_BASE_URL = "http://localhost:8000/api";

// Separate the main app logic into a component that can use useNavigate
const MainApp = () => {
  const navigate = useNavigate(); // ✅ This is what was missing!
  
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [authMode, setAuthMode] = useState("login");

  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const [uploadFiles, setUploadFiles] = useState([]);
  const [collectionName, setCollectionName] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [notification, setNotification] = useState(null);

  const fileInputRef = useRef(null);

  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  useEffect(() => {
    const savedToken = localStorage.getItem("voilet_token");
    const savedUsername = localStorage.getItem("voilet_username");
    if (savedToken && savedUsername) {
      setToken(savedToken);
      setUsername(savedUsername);
      setIsAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchCollections();
    }
  }, [isAuthenticated, token]);

  const handleAuth = async () => {
    console.log('handleAuth called', { authMode, username });
    if (!username || !password) {
      showNotification("Please enter username and password", "error");
      return;
    }
    setIsLoading(true);
    try {
      const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";
      let resp;

      if (authMode === "login") {
        const body = new URLSearchParams({ username, password }).toString();
        resp = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body,
        });
      } else {
        resp = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });
      }
      let data = null;
      try {
        data = await resp.json();
      } catch (e) {
        console.error('Failed to parse JSON response from auth endpoint', e);
      }
      console.log('Auth response', { status: resp.status, ok: resp.ok, data });
      if (resp.ok) {
        if (authMode === "login") {
          setToken(data.access_token);
          localStorage.setItem("voilet_token", data.access_token);
          localStorage.setItem("voilet_username", username);
          setIsAuthenticated(true);
          showNotification("Welcome back!");
          console.log('Login success, token set, navigating to /dashboard');
          
          // ✅ THIS IS THE KEY FIX - Navigate to dashboard after login
          navigate("/dashboard");
          
          // Open upload modal automatically after first login
          setTimeout(() => setShowUploadModal(true), 500);
        } else {
          showNotification("Account created! Please login.");
          setAuthMode("login");
          setPassword("");
        }
      } else {
        showNotification(data.detail || "Authentication failed", "error");
      }
    } catch (err) {
      showNotification("Connection error. Please try again.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setToken(null);
    setUsername("");
    setPassword("");
    localStorage.removeItem("voilet_token");
    localStorage.removeItem("voilet_username");
    setCollections([]);
    setSelectedCollection(null);
    setMessages([]);
    showNotification("Logged out successfully");
    
    // ✅ Navigate to login after logout
    navigate("/login");
  };

  const fetchCollections = async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/app/collections`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        const data = await resp.json();
        setCollections(data);
      }
    } catch (err) {
      console.error("Error fetching collections:", err);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const pdfFiles = files.filter((f) => f.name.toLowerCase().endsWith(".pdf"));
    if (pdfFiles.length !== files.length) {
      showNotification("Only PDF files are supported", "error");
    }
    setUploadFiles(pdfFiles);
  };

  const handleUpload = async () => {
    if (uploadFiles.length === 0 || !collectionName.trim()) {
      showNotification("Please select files and enter a collection name", "error");
      return;
    }
    setIsLoading(true);
    setUploadProgress(10);
    const formData = new FormData();
    uploadFiles.forEach((file) => formData.append("files", file));
    formData.append("collection_name", collectionName);
    formData.append("llm_provider", "openai");
    formData.append("llm_model", "gpt-4o-mini");
    try {
      setUploadProgress(30);
      const resp = await fetch(`${API_BASE_URL}/app/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      setUploadProgress(70);
      const data = await resp.json();
      if (resp.ok) {
        setUploadProgress(100);
        showNotification(`Successfully uploaded ${uploadFiles.length} file(s)!`);
        setShowUploadModal(false);
        setUploadFiles([]);
        setCollectionName("");
        setUploadProgress(0);
        await fetchCollections();
        setSelectedCollection(data.collection);
        if (data.insights) {
          setInsights(data.insights);
        }
      } else {
        showNotification(data.detail || "Upload failed", "error");
      }
    } catch (err) {
      showNotification("Upload error. Please try again.", "error");
    } finally {
      setIsLoading(false);
      setUploadProgress(0);
    }
  };

  const handleSelectCollection = async (collection) => {
    setSelectedCollection(collection);
    setMessages([]);
    setInsights(null);
    try {
      const resp = await fetch(`${API_BASE_URL}/app/insights/${collection.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        const data = await resp.json();
        setInsights(data.insights);
      }
    } catch (err) {
      console.error("Error fetching insights:", err);
    }
  };

  const handleSendQuestion = async (question = currentQuestion) => {
    if (!question.trim() || !selectedCollection) return;
    const userMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentQuestion("");
    setIsLoading(true);
    try {
      const resp = await fetch(`${API_BASE_URL}/app/chat`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          collection_id: selectedCollection.id,
          question,
        }),
      });
      const data = await resp.json();
      if (resp.ok) {
        const assistantMessage = {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          type: data.type,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        showNotification(data.detail || "Failed to get answer", "error");
      }
    } catch (err) {
      showNotification("Error sending question", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCollection = async (collectionId) => {
    if (!window.confirm("Are you sure you want to delete this collection?")) return;
    try {
      const resp = await fetch(`${API_BASE_URL}/app/collections/${collectionId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        showNotification("Collection deleted");
        await fetchCollections();
        if (selectedCollection?.id === collectionId) {
          setSelectedCollection(null);
          setMessages([]);
          setInsights(null);
        }
      }
    } catch (err) {
      showNotification("Error deleting collection", "error");
    }
  };

  // Login/Register Page
  const LoginPage = () => (
    <AuthForm
      username={username}
      password={password}
      setUsername={setUsername}
      setPassword={setPassword}
      authMode={authMode}
      setAuthMode={setAuthMode}
      handleAuth={handleAuth}
      isLoading={isLoading}
    />
  );

  // Main Dashboard
  const Dashboard = () => (
    <>
      {/* DEBUG: Render marker to confirm Dashboard mounts */}
      <div className="p-4 text-sm text-gray-500">DEBUG: Dashboard mounted</div>
    <div className="h-screen flex flex-col bg-gray-50">
      <Notification notification={notification} />
      <Header
        username={username}
        onUploadClick={() => setShowUploadModal(true)}
        onLogout={handleLogout}
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          collections={collections}
          selectedCollection={selectedCollection}
          onSelect={handleSelectCollection}
          onDelete={handleDeleteCollection}
        />
        <ChatArea
          selectedCollection={selectedCollection}
          messages={messages}
          insights={insights}
          isLoading={isLoading}
          currentQuestion={currentQuestion}
          setCurrentQuestion={setCurrentQuestion}
          handleSendQuestion={handleSendQuestion}
        />
      </div>
      <UploadModal
        showUploadModal={showUploadModal}
        setShowUploadModal={setShowUploadModal}
        uploadFiles={uploadFiles}
        setUploadFiles={setUploadFiles}
        collectionName={collectionName}
        setCollectionName={setCollectionName}
        handleUpload={handleUpload}
        fileInputRef={fileInputRef}
        handleFileSelect={handleFileSelect}
        isLoading={isLoading}
        uploadProgress={uploadProgress}
      />
    </div>
    </>
  );

  // ✅ Router setup
  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
      />
      <Route 
        path="/dashboard" 
        element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} 
      />
      <Route 
        path="/" 
        element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} 
      />
    </Routes>
  );
};

// ✅ Wrap everything in BrowserRouter
const App = () => {
  return (
    <BrowserRouter>
      <MainApp />
    </BrowserRouter>
  );
};

export default App;