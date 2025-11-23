from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Default LLM preferences for the user (changed to OpenAI)
    preferred_llm_provider = Column(String, default="openai")
    preferred_llm_model = Column(String, default="gpt-3.5-turbo")

    # Relationship: A user can have many collections
    collections = relationship("DocumentCollection", back_populates="owner")

class DocumentCollection(Base):
    __tablename__ = "document_collections"

    id = Column(Integer, primary_key=True, index=True)
    collection_name = Column(String, index=True)
    
    # UUID for the FAISS vector store
    vector_store_session_id = Column(String, unique=True, index=True) 
    
    # LLM configuration for this collection (changed to OpenAI)
    llm_provider = Column(String, default="openai")
    llm_model = Column(String, default="gpt-3.5-turbo")
    
    # Link to user
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="collections")