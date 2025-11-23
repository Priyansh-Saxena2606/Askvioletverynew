import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import tabula
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class DocumentProcessor:
    """Handles PDF processing including text, tables, and metadata extraction"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def extract_text_with_metadata(self, pdf_path: Path) -> List[Document]:
        """Extract text from PDF with page numbers and source metadata"""
        documents = []
        pdf_document = fitz.open(pdf_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            
            if text.strip():
                # Extract text coordinates for highlighting (bounding boxes)
                blocks = page.get_text("blocks")
                text_blocks = []
                
                for block in blocks:
                    if block[6] == 0:  # Text block
                        text_blocks.append({
                            "text": block[4],
                            "bbox": list(block[:4])  # x0, y0, x1, y1
                        })
                
                # Create document with rich metadata
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_num + 1,
                        "total_pages": len(pdf_document),
                        "file_path": str(pdf_path),
                        "text_blocks": json.dumps(text_blocks)  # For highlighting
                    }
                )
                documents.append(doc)
        
        pdf_document.close()
        return documents
    
    def extract_tables(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract tables from PDF using tabula"""
        try:
            tables = tabula.read_pdf(
                str(pdf_path),
                pages='all',
                multiple_tables=True,
                silent=True
            )
            
            extracted_tables = []
            for idx, table in enumerate(tables):
                if isinstance(table, pd.DataFrame) and not table.empty:
                    extracted_tables.append({
                        "table_index": idx,
                        "source": pdf_path.name,
                        "data": table.to_dict('records'),
                        "columns": list(table.columns),
                        "csv_string": table.to_csv(index=False)
                    })
            
            return extracted_tables
        except Exception as e:
            print(f"Table extraction failed for {pdf_path.name}: {str(e)}")
            print("Note: Table extraction requires Java. Install Java and set JAVA_HOME if needed.")
            return []
    
    def extract_images_info(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract information about images in the PDF"""
        pdf_document = fitz.open(pdf_path)
        images_info = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()
            
            for img_idx, img in enumerate(image_list):
                images_info.append({
                    "source": pdf_path.name,
                    "page": page_num + 1,
                    "image_index": img_idx,
                    "xref": img[0]
                })
        
        pdf_document.close()
        return images_info
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks while preserving metadata"""
        chunks = self.text_splitter.split_documents(documents)
        return chunks


class LLMManager:
    """Manages OpenAI LLM provider"""
    
    def __init__(self, llm_provider: str = "openai", llm_model: Optional[str] = None):
        self.llm_provider = llm_provider.lower()
        self.llm_model = llm_model
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize OpenAI LLM"""
        if self.llm_provider != "openai":
            raise ValueError(f"Only OpenAI provider is supported. Got: {self.llm_provider}")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # OpenAI model mapping
        OPENAI_MODEL_MAP = {
            "gpt-3.5-turbo": "gpt-3.5-turbo",
            "gpt-4": "gpt-4",
            "gpt-4-turbo": "gpt-4-turbo-preview",
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini"
        }
        
        # Default to gpt-3.5-turbo (fastest and cheapest)
        default_model = "gpt-3.5-turbo"
        model_name = self.llm_model or default_model
        api_model_name = OPENAI_MODEL_MAP.get(model_name, default_model)
        
        if model_name not in OPENAI_MODEL_MAP:
            print(f"Warning: Unknown OpenAI model '{model_name}'. Defaulting to '{default_model}'.")
        
        print(f"Initializing ChatOpenAI with model: {api_model_name}")
        
        try:
            return ChatOpenAI(
                model=api_model_name,
                openai_api_key=api_key,
                temperature=0.3
            )
        except Exception as e:
            print(f"Error initializing OpenAI: {str(e)}")
            raise
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM"""
        try:
            response = self.llm.invoke(prompt)
            # ChatOpenAI returns a message object with .content
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return error_msg


class ProactiveInsights:
    """Generate proactive insights from documents"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a TL;DR summary"""
        prompt = f"""Provide a concise summary (max {max_length} characters) of the following text. 
Focus on the main points and key takeaways:

{text[:4000]}

Summary:"""
        
        return self.llm_manager.generate_response(prompt)
    
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract main topics and key concepts"""
        prompt = f"""Analyze the following text and extract the top 5-7 key concepts, topics, or themes.
Return them as a simple bulleted list:

{text[:4000]}

Key Concepts:"""
        
        response = self.llm_manager.generate_response(prompt)
        # Parse the response into a list
        concepts = [line.strip('- •*').strip() for line in response.split('\n') if line.strip()]
        return concepts[:7]
    
    def generate_suggested_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """Generate suggested questions about the content"""
        prompt = f"""Based on the following text, generate {num_questions} interesting and relevant questions 
that a reader might want to ask. Make them specific and actionable.

{text[:4000]}

Questions (one per line):"""
        
        response = self.llm_manager.generate_response(prompt)
        questions = [q.strip('1234567890. ').strip() for q in response.split('\n') if q.strip()]
        return questions[:num_questions]
    
    def analyze_document(self, documents: List[Document]) -> Dict[str, Any]:
        """Perform comprehensive analysis of uploaded documents"""
        # Combine first few pages for analysis
        combined_text = "\n\n".join([doc.page_content for doc in documents[:5]])
        
        try:
            insights = {
                "summary": self.generate_summary(combined_text),
                "key_concepts": self.extract_key_concepts(combined_text),
                "suggested_questions": self.generate_suggested_questions(combined_text),
                "document_stats": {
                    "total_documents": len(set([doc.metadata.get("source") for doc in documents])),
                    "total_pages": sum([1 for doc in documents]),
                }
            }
        except Exception as e:
            print(f"Error generating insights: {str(e)}")
            # Return basic stats if LLM fails
            insights = {
                "summary": "Unable to generate summary due to API error",
                "key_concepts": [],
                "suggested_questions": [],
                "document_stats": {
                    "total_documents": len(set([doc.metadata.get("source") for doc in documents])),
                    "total_pages": sum([1 for doc in documents]),
                }
            }
        
        return insights


class EnhancedRAGSystem:
    """Enhanced Retrieval-Augmented Generation system with multi-document support"""
    
    def __init__(self, llm_provider: str = "openai", llm_model: Optional[str] = None):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.llm_manager = LLMManager(llm_provider, llm_model)
        self.document_processor = DocumentProcessor()
        self.insights_generator = ProactiveInsights(self.llm_manager)
        self.vector_store = None
        self.tables_data = []
        self.images_info = []
    
    def process_files(
        self, 
        file_paths: List[Path], 
        vector_store_path: Path
    ) -> Dict[str, Any]:
        """Process multiple PDF files and create vector store with metadata"""
        all_documents = []
        all_tables = []
        all_images = []
        
        # Process each file
        for file_path in file_paths:
            print(f"Processing {file_path.name}...")
            
            # Extract text with metadata
            documents = self.document_processor.extract_text_with_metadata(file_path)
            all_documents.extend(documents)
            
            # Extract tables (will fail gracefully if Java not installed)
            tables = self.document_processor.extract_tables(file_path)
            all_tables.extend(tables)
            
            # Extract image information
            images = self.document_processor.extract_images_info(file_path)
            all_images.extend(images)
        
        # Chunk documents
        chunks = self.document_processor.chunk_documents(all_documents)
        
        # Create vector store
        print(f"Creating vector store with {len(chunks)} chunks...")
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        # Save vector store
        vector_store_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(vector_store_path))
        print(f"Vector store saved to {vector_store_path}")
        
        # Save tables and images metadata
        with open(vector_store_path / "tables.json", "w") as f:
            json.dump(all_tables, f, indent=2)
        
        with open(vector_store_path / "images.json", "w") as f:
            json.dump(all_images, f, indent=2)
        
        # Generate proactive insights
        print("Generating insights...")
        insights = self.insights_generator.analyze_document(all_documents[:10])
        
        # Save insights
        with open(vector_store_path / "insights.json", "w") as f:
            json.dump(insights, f, indent=2)
        
        return {
            "status": "success",
            "chunks_created": len(chunks),
            "documents_processed": len(file_paths),
            "tables_extracted": len(all_tables),
            "images_found": len(all_images),
            "insights": insights
        }
    
    def load_vector_store(self, vector_store_path: Path):
        """Load existing vector store and metadata"""
        self.vector_store = FAISS.load_local(
            str(vector_store_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Load tables
        tables_path = vector_store_path / "tables.json"
        if tables_path.exists():
            with open(tables_path, "r") as f:
                self.tables_data = json.load(f)
        
        # Load images
        images_path = vector_store_path / "images.json"
        if images_path.exists():
            with open(images_path, "r") as f:
                self.images_info = json.load(f)
    
    def query_tables(self, question: str) -> Optional[str]:
        """Query tables using LLM"""
        if not self.tables_data:
            return None
        
        # Convert tables to text format
        tables_text = "\n\n".join([
            f"Table from {t['source']}:\n{t['csv_string']}"
            for t in self.tables_data
        ])
        
        prompt = f"""Based on the following tables, answer this question: {question}

Tables:
{tables_text[:3000]}

Answer:"""
        
        return self.llm_manager.generate_response(prompt)
    
    def get_answer_with_sources(
        self, 
        question: str, 
        k: int = 4
    ) -> Dict[str, Any]:
        """Get answer with detailed source information for highlighting"""
        if not self.vector_store:
            return {"error": "Vector store not loaded"}
        
        # Check if question is about tables
        table_keywords = ["table", "data", "row", "column", "value", "sales", "revenue"]
        if any(keyword in question.lower() for keyword in table_keywords):
            table_answer = self.query_tables(question)
            if table_answer:
                return {
                    "answer": table_answer,
                    "type": "table_query",
                    "sources": []
                }
        
        # Retrieve relevant documents
        docs_and_scores = self.vector_store.similarity_search_with_score(question, k=k)
        
        # Prepare context with source information
        context_parts = []
        sources = []
        
        for doc, score in docs_and_scores:
            context_parts.append(doc.page_content)
            
            # Parse text blocks for highlighting
            text_blocks = []
            if "text_blocks" in doc.metadata:
                try:
                    text_blocks = json.loads(doc.metadata["text_blocks"])
                except:
                    text_blocks = []
            
            sources.append({
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", 0),
                "file_path": doc.metadata.get("file_path", ""),
                "relevance_score": float(score),
                "text_preview": doc.page_content[:200] + "...",
                "text_blocks": text_blocks
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer with prompt template
        prompt = f"""You are a helpful AI assistant analyzing documents. Answer the question based on the provided context.
If the context doesn't contain the answer, say so clearly.

Context from multiple documents:
{context}

Question: {question}

Provide a clear, detailed answer citing specific sources when possible:"""
        
        answer = self.llm_manager.generate_response(prompt)
        
        return {
            "answer": answer,
            "type": "document_query",
            "sources": sources,
            "context_used": len(context_parts)
        }


# Main functions to be called from endpoints
def process_files(
    file_paths: List[Path], 
    vector_store_path: Path,
    llm_provider: str = "openai",
    llm_model: Optional[str] = None
) -> Dict[str, Any]:
    """Main function to process files"""
    rag_system = EnhancedRAGSystem(llm_provider, llm_model)
    return rag_system.process_files(file_paths, vector_store_path)


def get_chat_answer(
    question: str, 
    vector_store_path: Path,
    llm_provider: str = "openai",
    llm_model: Optional[str] = None
) -> Dict[str, Any]:
    """Main function to get chat answer with sources"""
    rag_system = EnhancedRAGSystem(llm_provider, llm_model)
    rag_system.load_vector_store(vector_store_path)
    return rag_system.get_answer_with_sources(question)


def get_insights(vector_store_path: Path) -> Dict[str, Any]:
    """Get proactive insights for a collection"""
    insights_path = vector_store_path / "insights.json"
    
    if insights_path.exists():
        with open(insights_path, "r") as f:
            return json.load(f)
    
    return {"error": "No insights found"}