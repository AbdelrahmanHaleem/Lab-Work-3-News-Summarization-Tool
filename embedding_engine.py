import os
from typing import List, Dict, Any
import numpy as np
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma, FAISS

class EmbeddingEngine:
    """Creates and manages article embeddings for semantic search."""
    
    def __init__(self, vector_db_type: str = "chroma", persist_directory: str = "db"):
        """
        Initialize the embedding engine.
        
        Args:
            vector_db_type (str): Type of vector database to use ("chroma" or "faiss")
            persist_directory (str): Directory to store the vector database
        """
        self.vector_db_type = vector_db_type.lower()
        self.persist_directory = persist_directory
        
        # Initialize embeddings model
        self.model_name = "BAAI/bge-small-en-v1.5"
        self.model_kwargs = {"device": "cpu"}
        self.encode_kwargs = {"normalize_embeddings": True}
        
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
        )
        
        self.vector_db = None
    
    def _prepare_documents(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare articles for embedding.
        
        Args:
            articles (List[Dict[str, Any]]): List of article content
            
        Returns:
            List[Dict[str, Any]]: Prepared documents for embedding
        """
        documents = []
        for article in articles:
            # Combine title, description, and content for embedding
            text = f"{article['title']} {article['description']} {article['content']}"
            doc = {
                "id": article.get("url", ""),
                "text": text,
                "metadata": {
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "author": article.get("author", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "urlToImage": article.get("urlToImage", "")
                }
            }
            documents.append(doc)
        
        return documents
    
    def create_vector_db(self, articles: List[Dict[str, Any]]) -> None:
        """
        Create a vector database from articles.
        
        Args:
            articles (List[Dict[str, Any]]): List of article content
        """
        documents = self._prepare_documents(articles)
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        if self.vector_db_type == "chroma":
            self.vector_db = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory=self.persist_directory
            )
        elif self.vector_db_type == "faiss":
            self.vector_db = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            # Save FAISS index
            self.vector_db.save_local(self.persist_directory)
        else:
            raise ValueError(f"Unsupported vector database type: {self.vector_db_type}")
    
    def load_vector_db(self) -> bool:
        """
        Load an existing vector database.
        
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            if self.vector_db_type == "chroma":
                self.vector_db = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            elif self.vector_db_type == "faiss":
                self.vector_db = FAISS.load_local(
                    self.persist_directory,
                    self.embeddings
                )
            return True
        except Exception as e:
            print(f"Error loading vector database: {e}")
            return False
    
    def search_similar_articles(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for articles similar to the query.
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar articles
        """
        if not self.vector_db:
            raise ValueError("Vector database not initialized. Please create or load a database first.")
        
        results = self.vector_db.similarity_search(query, k=k)
        
        similar_articles = []
        for doc in results:
            article = {
                "text": doc.page_content,
                **doc.metadata
            }
            similar_articles.append(article)
        
        return similar_articles

# Example usage
if __name__ == "__main__":
    # Sample article data
    sample_articles = [
        {
            "title": "Example Tech Article",
            "source": "Tech News",
            "author": "John Doe",
            "description": "This is a sample tech article description.",
            "content": "This is the content of the sample tech article.",
            "url": "https://example.com/tech/1",
            "publishedAt": "2023-08-01T12:00:00Z",
            "urlToImage": "https://example.com/images/tech1.jpg"
        },
        {
            "title": "Another Tech Article",
            "source": "Tech Blog",
            "author": "Jane Smith",
            "description": "This is another sample tech article description.",
            "content": "This is the content of another sample tech article.",
            "url": "https://example.com/tech/2",
            "publishedAt": "2023-08-02T12:00:00Z",
            "urlToImage": "https://example.com/images/tech2.jpg"
        }
    ]
    
    # Initialize embedding engine
    engine = EmbeddingEngine(vector_db_type="faiss")
    
    # Create vector database
    engine.create_vector_db(sample_articles)
    
    # Search for similar articles
    results = engine.search_similar_articles("tech article")
    
    print(f"Found {len(results)} similar articles:")
    for i, article in enumerate(results, 1):
        print(f"\n{i}. {article['title']} - {article['source']}")