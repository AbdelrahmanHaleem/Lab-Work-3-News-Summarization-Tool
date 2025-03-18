import os
from typing import List, Dict, Any, Literal
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

class Summarizer:
    """Implements LangChain summarization chains for news articles."""
    
    def __init__(self, groq_api_key: str = None):
        """
        Initialize the summarizer.
        
        Args:
            groq_api_key (str, optional): API key for Groq. If not provided, 
                                        it will look for GROQ_API_KEY in environment variables.
        """
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("Groq API key is required. Please provide it or set GROQ_API_KEY environment variable.")
        
        # Initialize the language model
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=4096
        )
        
        # Text splitter for long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Define prompt templates
        self.brief_template = """
        Write a brief summary of the following article in 1-2 sentences:
        
        {text}
        
        BRIEF SUMMARY:
        """
        
        self.detailed_template = """
        Write a detailed summary of the following article in one paragraph:
        
        {text}
        
        DETAILED SUMMARY:
        """
    
    def _prepare_document(self, article: Dict[str, Any]) -> List[Document]:
        """
        Prepare an article for summarization.
        
        Args:
            article (Dict[str, Any]): Article content
            
        Returns:
            List[Document]: List of LangChain Document objects
        """
        # Combine title, description, and content
        text = f"Title: {article['title']}\n\n"
        text += f"Source: {article['source']}\n\n"
        
        if article.get('description'):
            text += f"Description: {article['description']}\n\n"
            
        if article.get('content'):
            text += f"Content: {article['content']}\n\n"
        
        # Split text into chunks if it's too long
        docs = self.text_splitter.create_documents([text])
        return docs
    
    def summarize(self, 
                 article: Dict[str, Any], 
                 summary_type: Literal["brief", "detailed"] = "brief") -> str:
        """
        Generate a summary of an article.
        
        Args:
            article (Dict[str, Any]): Article content
            summary_type (str): Type of summary to generate ("brief" or "detailed")
            
        Returns:
            str: Generated summary
        """
        docs = self._prepare_document(article)
        
        if summary_type == "brief":
            # Use map_reduce chain for brief summary
            prompt_template = PromptTemplate(template=self.brief_template, input_variables=["text"])
            chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                map_prompt=prompt_template,
                combine_prompt=prompt_template,
                verbose=False
            )
        else:  # detailed
            # Use stuff chain for detailed summary
            prompt_template = PromptTemplate(template=self.detailed_template, input_variables=["text"])
            chain = load_summarize_chain(
                self.llm,
                chain_type="stuff",
                prompt=prompt_template,
                verbose=False
            )
        
        summary = chain.run(docs)
        return summary.strip()

# Example usage
if __name__ == "__main__":
    # Sample article
    sample_article = {
        "title": "Example Tech Article",
        "source": "Tech News",
        "author": "John Doe",
        "description": "This is a sample tech article description about new AI developments.",
        "content": """
        This is the content of the sample tech article. It discusses the latest advancements in artificial intelligence
        and how they are transforming various industries. The article mentions several key innovations in natural
        language processing and computer vision that have been announced recently. It also covers the potential
        impacts of these technologies on society and the economy.
        """,
        "url": "https://example.com/tech/1",
        "publishedAt": "2023-08-01T12:00:00Z",
        "urlToImage": "https://example.com/images/tech1.jpg"
    }
    
    # Initialize summarizer
    summarizer = Summarizer(groq_api_key="your_groq_api_key")
    
    # Generate brief summary
    brief_summary = summarizer.summarize(sample_article, summary_type="brief")
    print(f"Brief summary:\n{brief_summary}\n")
    
    # Generate detailed summary
    detailed_summary = summarizer.summarize(sample_article, summary_type="detailed")
    print(f"Detailed summary:\n{detailed_summary}")