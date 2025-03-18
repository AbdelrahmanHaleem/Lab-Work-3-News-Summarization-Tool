import requests
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

class NewsRetriever:
    """Handles API requests to NewsAPI for retrieving news articles."""
    
    def __init__(self, api_key: str = None):
        """Initialize the NewsRetriever with an API key."""
        self.api_key = api_key or os.environ.get("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Please provide it or set NEWS_API_KEY environment variable.")
        self.base_url = "https://newsapi.org/v2/everything"
        
    def get_articles(self, 
                    query: str, 
                    language: str = "en", 
                    sort_by: str = "publishedAt", 
                    page_size: int = 10, 
                    page: int = 1,
                    days_back: int = 7) -> Dict[str, Any]:
        """
        Retrieve articles based on a search query.
        
        Args:
            query (str): Search query term or phrase
            language (str): Language of articles (default: 'en')
            sort_by (str): Sort order (default: 'publishedAt')
            page_size (int): Number of results per page (default: 10)
            page (int): Page number (default: 1)
            days_back (int): Number of days to look back (default: 7)
            
        Returns:
            Dict[str, Any]: Response from NewsAPI
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates for API
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page,
            "from": from_date,
            "to": to_date,
            "apiKey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        
        return response.json()
    
    def extract_article_content(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract relevant content from articles.
        
        Args:
            articles (List[Dict[str, Any]]): List of articles from NewsAPI
            
        Returns:
            List[Dict[str, Any]]: List of extracted article content
        """
        extracted_content = []
        for article in articles:
            # Extract relevant fields and handle potential missing data
            content = {
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown Source"),
                "author": article.get("author", "Unknown Author"),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "publishedAt": article.get("publishedAt", ""),
                "urlToImage": article.get("urlToImage", "")
            }
            extracted_content.append(content)
        
        return extracted_content

# Example usage
if __name__ == "__main__":
    api_key = "d34ef5e40475433e97841a65b32938fe"  # Replace with your actual API key
    retriever = NewsRetriever(api_key)
    results = retriever.get_articles("technology")
    
    if results["status"] == "ok":
        articles = results["articles"]
        extracted = retriever.extract_article_content(articles)
        
        print(f"Found {len(extracted)} articles:")
        for i, article in enumerate(extracted[:3], 1):  # Print first 3 articles
            print(f"\n{i}. {article['title']} - {article['source']}")
            print(f"   {article['description'][:100]}...")
    else:
        print(f"Error: {results.get('message', 'Unknown error')}")