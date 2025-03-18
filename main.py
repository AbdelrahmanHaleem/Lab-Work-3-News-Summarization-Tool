import os
import sys
import textwrap
from typing import List, Dict, Any
from news_retriever import NewsRetriever
from embedding_engine import EmbeddingEngine
from summarizer import Summarizer
from user_manager import UserManager

class NewsApp:
    """Main application interface for news summarization."""
    
    def __init__(self):
        """Initialize the news application."""
        # Load API keys from environment or set defaults
        self.news_api_key = os.environ.get("NEWS_API_KEY", "d34ef5e40475433e97841a65b32938fe")
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "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")
        
        # Initialize components
        try:
            self.news_retriever = NewsRetriever(self.news_api_key)
            self.embedding_engine = EmbeddingEngine(vector_db_type="chroma")
            self.summarizer = Summarizer(self.groq_api_key)
            self.user_manager = UserManager()
        except Exception as e:
            print(f"Error initializing components: {e}")
            sys.exit(1)
    
    def search_news(self, query: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Search for news articles.
        
        Args:
            query (str): Search query
            page_size (int): Number of articles to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of articles
        """
        try:
            results = self.news_retriever.get_articles(query, page_size=page_size)
            
            if results["status"] == "ok":
                articles = self.news_retriever.extract_article_content(results["articles"])
                self.user_manager.add_search_history(query, len(articles))
                return articles
            else:
                print(f"Error: {results.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"Error searching news: {e}")
            return []
    
    def add_articles_to_vector_db(self, articles: List[Dict[str, Any]]) -> None:
        """
        Add articles to the vector database.
        
        Args:
            articles (List[Dict[str, Any]]): List of articles
        """
        try:
            self.embedding_engine.create_vector_db(articles)
            print(f"Added {len(articles)} articles to vector database.")
        except Exception as e:
            print(f"Error adding articles to vector database: {e}")
    
    def find_similar_articles(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Find articles similar to the query.
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar articles
        """
        try:
            return self.embedding_engine.search_similar_articles(query, k=k)
        except Exception as e:
            print(f"Error finding similar articles: {e}")
            return []
    
    def summarize_article(self, article: Dict[str, Any], summary_type: str = None) -> str:
        """
        Generate a summary of an article.
        
        Args:
            article (Dict[str, Any]): Article content
            summary_type (str): Type of summary to generate (brief or detailed)
            
        Returns:
            str: Generated summary
        """
        if summary_type is None:
            summary_type = self.user_manager.get_preferences()["summary_type"]
        
        try:
            return self.summarizer.summarize(article, summary_type=summary_type)
        except Exception as e:
            print(f"Error summarizing article: {e}")
            return "Error generating summary"
    
    def display_article(self, article: Dict[str, Any], summary: str = None) -> None:
        """
        Display an article with its summary.
        
        Args:
            article (Dict[str, Any]): Article content
            summary (str): Generated summary
        """
        print("\n" + "="*80)
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['publishedAt']}")
        print(f"URL: {article['url']}")
        print("-"*80)
        
        if summary:
            print("Summary:")
            print(textwrap.fill(summary, width=80))
            print("-"*80)
        
        print("Description:")
        print(textwrap.fill(article.get('description', 'No description available'), width=80))
        print("="*80)
    
    def run_cli(self) -> None:
        """Run the command-line interface."""
        print("Welcome to News Summarizer App!")
        print("This app retrieves news articles and creates summaries based on your preferences.")
        
        while True:
            print("\nMain Menu:")
            print("1. Search for news")
            print("2. View saved topics")
            print("3. Manage topics")
            print("4. View search history")
            print("5. Update preferences")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                self._search_news_menu()
            elif choice == "2":
                self._view_saved_topics_menu()
            elif choice == "3":
                self._manage_topics_menu()
            elif choice == "4":
                self._view_search_history_menu()
            elif choice == "5":
                self._update_preferences_menu()
            elif choice == "6":
                print("Thank you for using News Summarizer App. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _search_news_menu(self) -> None:
        """Search news menu."""
        query = input("\nEnter search query: ")
        if not query:
            print("Search query cannot be empty.")
            return
        
        preferences = self.user_manager.get_preferences()
        page_size = preferences["articles_per_topic"]
        
        print(f"Searching for '{query}'...")
        articles = self.search_news(query, page_size=page_size)
        
        if not articles:
            print("No articles found.")
            return
        
        print(f"\nFound {len(articles)} articles.")
        
        # Add articles to vector database
        self.add_articles_to_vector_db(articles)
        
        # Display articles
        self._display_articles_menu(articles)
    
    def _display_articles_menu(self, articles: List[Dict[str, Any]]) -> None:
        """
        Display articles menu.
        
        Args:
            articles (List[Dict[str, Any]]): List of articles
        """
        while True:
            print("\nArticles:")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']} - {article['source']}")
            
            print("\nOptions:")
            print("1-N. Select article to view")
            print("S. Summarize all articles")
            print("B. Back to main menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice.upper() == "B":
                break
            elif choice.upper() == "S":
                self._summarize_all_articles(articles)
            else:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(articles):
                        self._view_article_menu(articles[index])
                    else:
                        print("Invalid article number.")
                except ValueError:
                    print("Invalid choice. Please try again.")
    
    def _view_article_menu(self, article: Dict[str, Any]) -> None:
        """
        View article menu.
        
        Args:
            article (Dict[str, Any]): Article content
        """
        preferences = self.user_manager.get_preferences()
        default_summary_type = preferences["summary_type"]
        
        while True:
            print("\nArticle Options:")
            print("1. View article details")
            print(f"2. Generate brief summary")
            print(f"3. Generate detailed summary")
            print("4. Back to articles list")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":
                self.display_article(article)
            elif choice == "2":
                summary = self.summarize_article(article, summary_type="brief")
                self.display_article(article, summary)
            elif choice == "3":
                summary = self.summarize_article(article, summary_type="detailed")
                self.display_article(article, summary)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _summarize_all_articles(self, articles: List[Dict[str, Any]]) -> None:
        """
        Summarize all articles.
        
        Args:
            articles (List[Dict[str, Any]]): List of articles
        """
        preferences = self.user_manager.get_preferences()
        summary_type = preferences["summary_type"]
        
        print(f"\nGenerating {summary_type} summaries for all articles...")
        
        for i, article in enumerate(articles, 1):
            print(f"Processing article {i}/{len(articles)}...")
            summary = self.summarize_article(article, summary_type=summary_type)
            self.display_article(article, summary)
    
    def _view_saved_topics_menu(self) -> None:
        """View saved topics menu."""
        topics = self.user_manager.get_topics()
        
        if not topics:
            print("\nNo saved topics found.")
            return
        
        while True:
            print("\nSaved Topics:")
            for i, topic in enumerate(topics, 1):
                print(f"{i}. {topic}")
            
            print("\nOptions:")
            print("1-N. Select topic to view news")
            print("B. Back to main menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice.upper() == "B":
                break
            else:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(topics):
                        topic = topics[index]
                        print(f"\nSearching for '{topic}'...")
                        
                        preferences = self.user_manager.get_preferences()
                        page_size = preferences["articles_per_topic"]
                        
                        articles = self.search_news(topic, page_size=page_size)
                        
                        if not articles:
                            print("No articles found.")
                        else:
                            # Add articles to vector database
                            self.add_articles_to_vector_db(articles)
                            
                            # Display articles
                            self._display_articles_menu(articles)
                    else:
                        print("Invalid topic number.")
                except ValueError:
                    print("Invalid choice. Please try again.")
    
    def _manage_topics_menu(self) -> None:
        """Manage topics menu."""
        while True:
            topics = self.user_manager.get_topics()
            
            print("\nManage Topics:")
            if topics:
                for i, topic in enumerate(topics, 1):
                    print(f"{i}. {topic}")
            else:
                print("No saved topics found.")
            
            print("\nOptions:")
            print("A. Add a new topic")
            print("R. Remove a topic")
            print("B. Back to main menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice.upper() == "A":
                topic = input("Enter topic to add: ")
                if topic:
                    self.user_manager.add_topic(topic)
                    print(f"Topic '{topic}' added successfully.")
                else:
                    print("Topic cannot be empty.")
            elif choice.upper() == "R":
                if not topics:
                    print("No topics to remove.")
                    continue
                
                topic_num = input("Enter topic number to remove: ")
                try:
                    index = int(topic_num) - 1
                    if 0 <= index < len(topics):
                        topic = topics[index]
                        if self.user_manager.remove_topic(topic):
                            print(f"Topic '{topic}' removed successfully.")
                        else:
                            print(f"Failed to remove topic '{topic}'.")
                    else:
                        print("Invalid topic number.")
                except ValueError:
                    print("Invalid topic number.")
            elif choice.upper() == "B":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _view_search_history_menu(self) -> None:
        """View search history menu."""
        history = self.user_manager.get_search_history()
        
        if not history:
            print("\nNo search history found.")
            return
        
        print("\nSearch History:")
        for i, item in enumerate(history, 1):
            timestamp = item["timestamp"].split("T")[0]
            print(f"{i}. [{timestamp}] '{item['query']}' ({item['num_results']} results)")
        
        print("\nPress Enter to return to main menu")
        input()
    
    def _update_preferences_menu(self) -> None:
        """Update preferences menu."""
        preferences = self.user_manager.get_preferences()
        
        while True:
            print("\nCurrent Preferences:")
            print(f"1. Default summary type: {preferences['summary_type']}")
            print(f"2. Articles per topic: {preferences['articles_per_topic']}")
            print(f"3. Language: {preferences['language']}")
            
            print("\nOptions:")
            print("1-3. Select preference to update")
            print("B. Back to main menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice == "1":
                print("\nSummary Type:")
                print("1. Brief (1-2 sentences)")
                print("2. Detailed (paragraph)")
                
                summary_choice = input("Enter your choice (1-2): ")
                if summary_choice == "1":
                    preferences["summary_type"] = "brief"
                    self.user_manager.update_preferences(preferences)
                    print("Summary type updated to 'brief'.")
                elif summary_choice == "2":
                    preferences["summary_type"] = "detailed"
                    self.user_manager.update_preferences(preferences)
                    print("Summary type updated to 'detailed'.")
                else:
                    print("Invalid choice.")
            elif choice == "2":
                try:
                    num = int(input("Enter number of articles per topic (1-20): "))
                    if 1 <= num <= 20:
                        preferences["articles_per_topic"] = num
                        self.user_manager.update_preferences(preferences)
                        print(f"Articles per topic updated to {num}.")
                    else:
                        print("Number must be between 1 and 20.")
                except ValueError:
                    print("Invalid number.")
            elif choice == "3":
                lang = input("Enter language code (e.g., 'en', 'fr', 'es'): ")
                if lang and len(lang) == 2:
                    preferences["language"] = lang.lower()
                    self.user_manager.update_preferences(preferences)
                    print(f"Language updated to '{lang.lower()}'.")
                else:
                    print("Invalid language code.")
            elif choice.upper() == "B":
                break
            else:
                print("Invalid choice. Please try again.")

# Main entry point
if __name__ == "__main__":
    app = NewsApp()
    app.run_cli()