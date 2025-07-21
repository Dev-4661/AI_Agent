# Company Information Chatbot 🏢

A sophisticated chatbot that provides real-time company information using LangChain, Google Gemini 2.0 Flash, and Tavily Search API. The bot can answer questions about companies including their business model, leadership, financials, products, and recent news.

## 🚀 Features

- **Real-time Search**: Uses Tavily Search API to fetch the latest company information
- **Intelligent Responses**: Powered by Google Gemini 2.0 Flash model for accurate and comprehensive answers
- **Modern UI**: Beautiful Streamlit interface with chat functionality
- **Command Line Interface**: Optional CLI for terminal-based interactions
- **Conversation History**: Maintains chat history during the session
- **Error Handling**: Robust error handling and user-friendly error messages

## 📁 Project Structure

```
company_chat_bot/
│
├── src/
│   └── chatbot.py              # Main chatbot class
│
├── config/
│   └── settings.py             # Configuration and environment variables
│
├── templates/
│   └── prompts.py              # LangChain prompt templates
│
├── utils/
│   └── search_tool.py          # Tavily search integration
│
├── main.py                     # Command line interface
├── streamlit_app.py            # Streamlit web interface
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
# Navigate to your project directory
cd company_chat_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit the `.env` file and add your API keys:
```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional configurations
MODEL_NAME=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=1000
MAX_SEARCH_RESULTS=5
```

### 4. Get Required API Keys

#### Google API Key (for Gemini 2.0 Flash):
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" and create a new key
4. Copy the API key to your `.env` file

#### Tavily API Key (for Search):
1. Visit [Tavily](https://tavily.com/)
2. Sign up for a free account
3. Navigate to your dashboard to get your API key
4. Copy the API key to your `.env` file

## 🚀 Usage

### Web Interface (Recommended)

Run the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Command Line Interface

Run the CLI version:

```bash
python main.py
```

## 💬 Example Questions

- "Tell me about Apple Inc."
- "Who is the CEO of Microsoft?"
- "What does Tesla do?"
- "What are Google's recent financial results?"
- "Tell me about Amazon's business model"
- "What products does NVIDIA make?"
- "Who founded Facebook and when?"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google API key for Gemini | Required |
| `TAVILY_API_KEY` | Tavily API key for search | Required |
| `MODEL_NAME` | Gemini model to use | `gemini-2.0-flash-exp` |
| `TEMPERATURE` | Response creativity (0-1) | `0.7` |
| `MAX_TOKENS` | Maximum response length | `1000` |
| `MAX_SEARCH_RESULTS` | Max search results to fetch | `5` |

### Customizing Prompts

You can modify the prompt templates in `templates/prompts.py` to customize how the bot responds to queries.

## 🎯 How It Works

1. **User Input**: User asks a question about a company
2. **Query Optimization**: The question is optimized into a better search query using Gemini
3. **Search**: Tavily Search API fetches real-time information about the company
4. **Response Generation**: Gemini processes the search results and generates a comprehensive answer
5. **Display**: The response is displayed to the user with proper formatting

## 🔍 Technical Details

### LangChain Integration
- Uses LangChain for prompt management and LLM orchestration
- Implements custom prompt templates for different query types
- Maintains conversation history and context

### Google Gemini 2.0 Flash
- Latest Google AI model for fast and accurate responses
- Optimized for conversational AI applications
- Supports large context windows for comprehensive answers

### Tavily Search
- Real-time web search specifically designed for AI applications
- Returns structured, AI-ready search results
- Includes source attribution for transparency

## 🛡️ Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- API rate limits
- Invalid search queries
- Malformed responses

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them
- Regularly rotate your API keys
- Monitor your API usage to avoid unexpected charges

## 📝 Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY is required" error**
   - Make sure you've created a `.env` file
   - Verify your Google API key is correct
   - Ensure the key has access to Gemini API

2. **"TAVILY_API_KEY is required" error**
   - Check your Tavily API key in the `.env` file
   - Verify your Tavily account is active

3. **Import errors**
   - Run `pip install -r requirements.txt` again
   - Make sure you're using Python 3.8 or higher

4. **Slow responses**
   - Check your internet connection
   - Try reducing `MAX_SEARCH_RESULTS` in your `.env` file

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the chatbot!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the LLM framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) for the AI model
- [Tavily](https://tavily.com/) for the search API
- [Streamlit](https://streamlit.io/) for the web interface
