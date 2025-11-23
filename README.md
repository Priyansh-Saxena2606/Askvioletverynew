Voilet: Intelligent Document Analysis & Chat(Replace this link with a real screenshot of your frontend dashboard once ready)Voilet is a full-stack AI application that transforms static PDF documents into interactive knowledge bases. Unlike standard "Chat with PDF" tools, Voilet proactively analyzes documents upon upload, extracting structured data from tables, generating summaries, and suggesting key questions before the user even types a prompt.Built with FastAPI, React, and LangChain, it leverages state-of-the-art Large Language Models (Gemini Pro & GPT-4) to provide accurate, context-aware answers from multiple documents simultaneously.🚀 Key Features📂 Multi-Document RAG: Upload and chat with entire folders of PDFs. The system synthesizes answers across multiple documents.🧠 Proactive Insights: Automatically generates a concise summary, key concepts, and suggested follow-up questions immediately after upload.📊 Table Talk (Smart Extraction): specialized processing pipeline using tabula-py to detect, extract, and query structured data trapped in PDF tables.🔌 Model Agnostic: "Hot-swap" support for different LLM providers. Users can choose between Google Gemini (cost-effective) or OpenAI GPT (high precision) for each collection.🔐 Secure Authentication: Full user management system with hashed passwords (bcrypt), JWT session tokens, and isolated document collections per user.⚡ Hybrid Search: Uses FAISS vector search combined with metadata filtering for high-precision retrieval.🛠️ Tech StackBackend (The Brain)Framework: Python, FastAPIAI Orchestration: LangChainVector Database: FAISS (Facebook AI Similarity Search)LLMs: Google Gemini Pro, OpenAI GPT-3.5/4Embeddings: HuggingFace (all-MiniLM-L6-v2)PDF Processing: PyMuPDF (Fitz), Tabula-py (Java-based table extraction)Database: SQLite (via SQLAlchemy)Auth: OAuth2 with JWT & BcryptFrontend (The Face)Library: React.jsStyling: Tailwind CSSState Management: React Context APIHTTP Client: Axios⚙️ Installation & SetupPrerequisitesPython 3.9+Node.js & npmJava 8+ (Required for tabula-py to extract tables)1. Clone the Repositorygit clone [https://github.com/yourusername/voilet.git](https://github.com/yourusername/voilet.git)
cd voilet
2. Backend SetupNavigate to the backend directory and set up the environment.# 1. Enter the backend folder (assuming root is backend, or cd app)
# Create a virtual environment
python -m venv venv

# 2. Activate the environment
# Windows:
.\venv\Scripts\Activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
Configuration:Create a .env file in the root directory and add your API keys:SECRET_KEY=your_super_secret_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Provider Keys
GEMINI_API_KEY=your_google_gemini_key
OPENAI_API_KEY=your_openai_key
Run the Server:uvicorn app.main:app --reload
The API will be available at http://localhost:8000. You can view the interactive documentation at http://localhost:8000/docs.3. Frontend SetupNavigate to the frontend directory.cd frontend

# 1. Install dependencies
npm install

# 2. Start the development server
npm start
The UI will launch at http://localhost:3000.📖 Usage GuideRegister/Login: Create an account to secure your workspace.Create Collection: Click "New Upload" and select the LLM model you wish to use (Gemini or GPT).Upload Documents: Drag and drop PDF files. The system will process text, tables, and images.View Insights: Read the auto-generated summary and key concepts.Chat: Ask specific questions like "What were the total sales in Q3 based on the table on page 5?" or "Summarize the conclusion of the research paper."🏗️ ArchitectureThe application follows a modular Service-Oriented Architecture:Ingestion Layer: PDFs are parsed; text is cleaned; tables are extracted via OCR-like heuristics.Embedding Layer: Text chunks are converted into dense vectors using sentence-transformers.Storage Layer: Vectors are stored in a local FAISS index; user metadata is stored in SQLite.Retrieval Layer: When a user asks a question, the system performs a semantic search to find the top 4 most relevant text chunks.Generation Layer: The chunks + user question are sent to the selected LLM (Gemini/GPT) to generate a grounded response.🔮 Future ImprovementsCloud Deployment: Dockerize the application and deploy to AWS/Render.Citation Highlighting: Highlight the exact sentence in the PDF viewer that answered the question.Voice Interface: Add Speech-to-Text to ask questions verbally.🤝 ContributingContributions are welcome! Please fork the repository and create a pull request for any features or bug fixes.📄 LicenseThis project is licensed under the MIT License.
