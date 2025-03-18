# News Summarization Application

A LangChain-based application that retrieves news articles on specific topics and creates concise summaries according to user preferences.

## Features

- Retrieve news articles using NewsAPI
- Create vector embeddings of articles for semantic search
- Generate brief or detailed summaries of articles using Groq LLM
- Track user topic preferences and search history
- Command-line interface for easy interaction

## Prerequisites

- Python 3.8+
- NewsAPI key (provided: `d34ef5e40475433e97841a65b32938fe`)
- Groq API key (provided: `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`)

## Installation

1. Create and activate a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install langchain langchain_community langchain_groq requests chromadb faiss-cpu sentence-transformers
   ```

   Or create a requirements.txt file with the following content and run:
   ```
   langchain==0.1.0
   langchain_community==0.0.10
   langchain_groq==0.1.0
   requests==2.31.0
   chromadb==0.4.22
   faiss-cpu==1.7.4
   sentence-transformers==2.5.1
   ```

   Then install with:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   # Windows
   set NEWS_API_KEY=d34ef5e40475433e97841a65b32938fe
   set GROQ_API_KEY=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
   ```

## Project Structure

- `news_retriever.py`: Handles API requests to NewsAPI
- `embedding_engine.py`: Creates and manages article embeddings
- `summarizer.py`: Implements LangChain summarization chains
- `user_manager.py`: Tracks user preferences and history
- `main.py`: Main application interface
- `user_data.json`: Stores user preferences and search history

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Follow the interactive menu to:
   - Search for news on specific topics
   - Save topics of interest
   - View customized summaries
   - See your search history
   - Update your preferences

### Main Menu Options

The application provides the following options in the main menu:

1. **Search for news**: Enter a query to search for news articles
2. **View saved topics**: View articles from your saved topics of interest
3. **Manage topics**: Add or remove topics of interest
4. **View search history**: View your recent search history
5. **Update preferences**: Change your preferences for summaries and results
6. **Exit**: Exit the application

## Summarization Features

The application offers two types of summaries:

1. **Brief Summary**: 1-2 sentences that capture the main point of the article (uses map_reduce chain)
2. **Detailed Summary**: A paragraph that provides more comprehensive information (uses stuff chain)

### Example Summaries

- Brief: "The article discusses recent advancements in artificial intelligence and their impact on various industries."
- Detailed: "The article explores how recent developments in artificial intelligence, particularly in natural language processing and computer vision, are transforming industries from healthcare to finance. It highlights key innovations such as improved deep learning models and more efficient algorithms, while also addressing concerns about ethical implications and job displacement. The author concludes that while AI presents challenges, its potential benefits for solving complex problems may outweigh these concerns if properly managed."

## Vector Database

The application uses vector embeddings to enable semantic search:

- Creates embeddings using a HuggingFace BGE model
- Stores embeddings in either Chroma or FAISS vector database
- Allows searching for articles by semantic similarity

## User Preferences

The system tracks:

- Topics of interest
- Preferred summary type (brief or detailed)
- Number of articles to display per topic
- Preferred language for articles

All preferences are saved to `user_data.json` for persistence between sessions.

## Example Workflow

1. Search for news on "artificial intelligence"
2. The app retrieves articles and creates embeddings
3. View article details and generate summaries
4. Save "artificial intelligence" as a topic of interest
5. Update preferences to show detailed summaries
6. Search for more topics or view saved topics

## Troubleshooting

- If you encounter import errors, ensure you have installed all dependencies correctly.
- If the NewsAPI requests fail, check your internet connection and API key.
- If summarization fails, ensure your Groq API key is correctly set.

## License

MIT
