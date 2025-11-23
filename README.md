# Voilet: Intelligent Document Analysis & Chat

**Voilet** is a full-stack AI application that transforms static PDF documents into interactive knowledge bases. 

Unlike standard "Chat with PDF" tools, Voilet **proactively analyzes** documents upon upload, extracting structured data from tables, generating summaries, and suggesting key questions *before* you even type a prompt.

Built with **FastAPI**, **React**, and **LangChain**, it leverages state-of-the-art Large Language Models (Gemini Pro & GPT-4) to provide accurate, context-aware answers from multiple documents simultaneously.

---

## 🚀 Key Features

* **📂 Multi-Document RAG:** Upload and chat with entire folders of PDFs. The system synthesizes answers across multiple documents.
* **🧠 Proactive Insights:** Automatically generates a concise summary, key concepts, and suggested follow-up questions immediately after upload.
* **📊 Table Talk (Smart Extraction):** A specialized processing pipeline using `tabula-py` to detect, extract, and query structured data trapped in PDF tables.
* **🔌 Model Agnostic:** "Hot-swap" support for different LLM providers. Choose **Google Gemini** (cost-effective) or **OpenAI GPT** (high precision) for each collection.
* **🔐 Secure Authentication:** Full user management system with hashed passwords (bcrypt), JWT session tokens, and isolated document collections per user.
* **⚡ Hybrid Search:** Uses FAISS vector search combined with metadata filtering for high-precision retrieval.

---

## 🛠️ Tech Stack

### Backend (The Brain)
| Component | Technology |
| :--- | :--- |
| **Framework** | Python, FastAPI |
| **AI Orchestration** | LangChain |
| **Vector Database** | FAISS (Facebook AI Similarity Search) |
| **LLMs** | Google Gemini Pro, OpenAI GPT-3.5/4 |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) |
| **PDF Processing** | PyMuPDF (Fitz), Tabula-py (Java-based) |
| **Database** | SQLite (via SQLAlchemy) |
| **Auth** | OAuth2 with JWT & Bcrypt |

### Frontend (The Face)
| Component | Technology |
| :--- | :--- |
| **Library** | React.js |
| **Styling** | Tailwind CSS |
| **State Mgmt** | React Context API |
| **HTTP Client** | Axios |

---

## 🏗️ Architecture

The application follows a modular **Service-Oriented Architecture**:

1.  **Ingestion Layer:** PDFs are parsed; text is cleaned; tables are extracted via OCR-like heuristics.
2.  **Embedding Layer:** Text chunks are converted into dense vectors using sentence-transformers.
3.  **Storage Layer:** Vectors are stored in a local FAISS index; user metadata is stored in SQLite.
4.  **Retrieval Layer:** When a user asks a question, the system performs a semantic search to find the top 4 most relevant text chunks.
5.  **Generation Layer:** The chunks + user question are sent to the selected LLM to generate a grounded response.

---

## ⚙️ Installation & Setup

### Prerequisites
* **Python 3.9+**
* **Node.js & npm**
* **Java 8+** (Required for `tabula-py` to extract tables—ensure it is in your system PATH)

### 1. Clone the Repository
```bash
git clone [https://github.com/Nikhil-Porwal/voilet.git](https://github.com/yourusername/voilet.git)
cd voilet
