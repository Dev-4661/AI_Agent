import streamlit as st
import sys
import os

# Try importing OCR and PDF libraries, handle missing modules gracefully
try:
    from PIL import Image
    import pytesseract
except ModuleNotFoundError:
    pytesseract = None
    Image = None

try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import CompanyChatbot

# Page configuration
st.set_page_config(
    page_title="LEAD GENERATION",
    page_icon="🏢",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
    }
    .sidebar-content {
        background-color: #f1f3f4;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    """Initialize the chatbot"""
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = CompanyChatbot()
            st.session_state.initialized = True
        except Exception as e:
            st.session_state.initialized = False
            st.session_state.error = str(e)
    
    return st.session_state.get('initialized', False)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("<h1 class='main-header'>🏢 Lead Generation</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        st.markdown("### 🤖 About")
        st.markdown("""
        This chatbot helps you find information about companies using:
        - **LangChain** for LLM orchestration
        - **Tavily Search** for real-time data
        - **Google Gemini 2.0 Flash** for intelligent responses
        """)
        
        st.markdown("### 📋 Example Questions")
        st.markdown("""
        - Tell me about Apple Inc.
        - Who is the CEO of Microsoft?
        - What does Tesla do?
        - Google's recent financial results
        - Amazon's business model
        """)
        
        st.markdown("### ⚙️ Configuration")
        if st.button("Clear Chat History"):
            welcome_msg = """
            👋 Welcome! I'm your Company Information Assistant. 
            
            I can help you find information about any company including:
            • Company overview and business model
            • Leadership and key executives  
            • Financial information and performance
            • Products and services
            • Recent news and developments
            
            Just ask me about any company you're interested in!
            """
            st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
            if 'chatbot' in st.session_state:
                st.session_state.chatbot.clear_conversation_history()
            st.success("Chat history cleared!")
        
        
    
    # Initialize chatbot
    if not initialize_chatbot():
        st.error("❌ Failed to initialize chatbot!")
        st.error(f"Error: {st.session_state.get('error', 'Unknown error')}")
        
        st.markdown("""
        ### 🔧 Setup Instructions:
        1. Create a `.env` file in the project root
        2. Add your API keys:
           ```
           GOOGLE_API_KEY=your_google_api_key_here
           TAVILY_API_KEY=your_tavily_api_key_here
           ```
        3. Install required packages: `pip install -r requirements.txt`
        4. Restart the application
        """)
        return
    
    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_msg = """
        👋 Welcome! I'm your Company Information Assistant. 
        
        I can help you find information about any company including:
        • Company overview and business model
        • Leadership and key executives  
        • Financial information and performance
        • Products and services
        • Recent news and developments
        
        Just ask me about any company you're interested in!
        """
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle file upload and display extracted content
  

            

    # Chat input
    if prompt := st.chat_input("Ask me about any company..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching for company information..."):
                try:
                    response = st.session_state.chatbot.chat(prompt)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
