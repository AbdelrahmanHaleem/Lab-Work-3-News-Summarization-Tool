import os
import json
from typing import List, Dict, Any
from datetime import datetime

class UserManager:
    """Tracks user preferences and search history."""
    
    def __init__(self, user_data_path: str = "user_data.json"):
        """
        Initialize the user manager.
        
        Args:
            user_data_path (str): Path to the user data JSON file
        """
        self.user_data_path = user_data_path
        self.user_data = self._load_user_data()
    
    def _load_user_data(self) -> Dict[str, Any]:
        """
        Load user data from the JSON file.
        
        Returns:
            Dict[str, Any]: User data
        """
        if os.path.exists(self.user_data_path):
            try:
                with open(self.user_data_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding user data file. Creating new data.")
                return self._create_default_user_data()
        else:
            return self._create_default_user_data()
    
    def _create_default_user_data(self) -> Dict[str, Any]:
        """
        Create default user data structure.
        
        Returns:
            Dict[str, Any]: Default user data
        """
        return {
            "preferences": {
                "topics": [],
                "summary_type": "brief",
                "language": "en",
                "articles_per_topic": 5
            },
            "search_history": []
        }
    
    def save_user_data(self) -> None:
        """Save user data to the JSON file."""
        with open(self.user_data_path, "w") as f:
            json.dump(self.user_data, f, indent=2)
    
    def get_preferences(self) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Returns:
            Dict[str, Any]: User preferences
        """
        return self.user_data["preferences"]
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Update user preferences.
        
        Args:
            preferences (Dict[str, Any]): New preferences to update
        """
        self.user_data["preferences"].update(preferences)
        self.save_user_data()
    
    def add_topic(self, topic: str) -> None:
        """
        Add a topic of interest.
        
        Args:
            topic (str): Topic to add
        """
        if topic not in self.user_data["preferences"]["topics"]:
            self.user_data["preferences"]["topics"].append(topic)
            self.save_user_data()
    
    def remove_topic(self, topic: str) -> bool:
        """
        Remove a topic of interest.
        
        Args:
            topic (str): Topic to remove
            
        Returns:
            bool: True if topic was removed, False otherwise
        """
        if topic in self.user_data["preferences"]["topics"]:
            self.user_data["preferences"]["topics"].remove(topic)
            self.save_user_data()
            return True
        return False
    
    def get_topics(self) -> List[str]:
        """
        Get all topics of interest.
        
        Returns:
            List[str]: List of topics
        """
        return self.user_data["preferences"]["topics"]
    
    def add_search_history(self, query: str, num_results: int) -> None:
        """
        Add a search to the history.
        
        Args:
            query (str): Search query
            num_results (int): Number of results found
        """
        timestamp = datetime.now().isoformat()
        self.user_data["search_history"].append({
            "query": query,
            "timestamp": timestamp,
            "num_results": num_results
        })
        self.save_user_data()
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent search history.
        
        Args:
            limit (int): Maximum number of history items to return
            
        Returns:
            List[Dict[str, Any]]: List of search history items
        """
        return self.user_data["search_history"][-limit:]

# Example usage
if __name__ == "__main__":
    user_manager = UserManager()
    
    # Add some topics
    user_manager.add_topic("technology")
    user_manager.add_topic("science")
    user_manager.add_topic("health")
    
    # Update preferences
    user_manager.update_preferences({
        "summary_type": "detailed",
        "articles_per_topic": 3
    })
    
    # Add search history
    user_manager.add_search_history("AI advancements", 8)
    
    # Get preferences and history
    print("User preferences:", user_manager.get_preferences())
    print("Topics:", user_manager.get_topics())
    print("Search history:", user_manager.get_search_history())
    
    # Remove a topic
    user_manager.remove_topic("health")
    print("Updated topics:", user_manager.get_topics())