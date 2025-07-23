from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict, Any
from config.settings import Config
from templates.prompts import get_company_info_prompt, get_search_query_prompt
from utils.search_tool import TavilySearchTool
import time
from collections import deque

class CompanyChatbot:
    """Main chatbot class for company information retrieval"""
    
    def __init__(self):
        """Initialize the chatbot with LLM and search tool"""
        try:
            Config.validate_config()
            
            # Initialize LLM
            self.llm = ChatGoogleGenerativeAI(
                model=Config.MODEL_NAME,
                temperature=Config.TEMPERATURE,
                max_output_tokens=Config.MAX_TOKENS,
                google_api_key=Config.GOOGLE_API_KEY
            )
            
            # Initialize search tool
            self.search_tool = TavilySearchTool()
            
            # Initialize prompt templates
            self.company_info_prompt = get_company_info_prompt()
            self.search_query_prompt = get_search_query_prompt()
            
            # Rate limiting: Track search timestamps (max 3 per minute)
            self.search_timestamps = deque()
            self.max_searches_per_minute = 3
            
            # Conversation history
            self.conversation_history: List[Dict[str, str]] = []
            
        except Exception as e:
            raise ValueError(f"Failed to initialize chatbot: {str(e)}")
    
    def optimize_search_query(self, user_question: str) -> str:
        """
        Optimize user question into a better search query
        
        Args:
            user_question (str): Original user question
            
        Returns:
            str: Optimized search query
        """
        try:
            prompt = self.search_query_prompt.format(question=user_question)
            
            messages = [
                SystemMessage(content="You are an expert at creating search queries for company information."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            optimized_query = response.content.strip()
            
            # Fallback to original question if optimization fails
            if not optimized_query or len(optimized_query) < 3:
                return user_question
                
            return optimized_query
            
        except Exception as e:
            print(f"Error optimizing search query: {str(e)}")
            return user_question
    
    def get_company_information(self, user_question: str) -> str:
        """
        Get company information based on user question
        
        Args:
            user_question (str): User's question about a company
            
        Returns:
            str: AI-generated response with company information
        """
        try:
            # Check if this is just a greeting/casual message
            if self._is_greeting_or_casual(user_question):
                return self._handle_greeting(user_question)
            
            # Rate limiting check - only for actual company searches
            if not self._check_rate_limit():
                return "🚫 Oops! Only 3 searches per minute allowed. Please Try After 1 Minute."
            
            # Step 1: Optimize the search query
            search_query = self.optimize_search_query(user_question)
            print(f"🔍 Searching for: {search_query}")
            
            # Step 2: Search for company information
            search_results = self.search_tool.search_and_format(search_query)
            
            if not search_results or search_results == "No search results found.":
                return "I'm sorry, I couldn't find any information about that company. Please check the company name and try again."
            
            # Step 3: Generate response using LLM
            prompt = self.company_info_prompt.format(
                search_results=search_results,
                question=user_question
            )
            
            messages = [
                SystemMessage(content="You are a helpful AI assistant specialized in providing accurate company information."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            ai_response = response.content.strip()
            
            # Step 4: Store in conversation history
            self.conversation_history.append({
                "question": user_question,
                "search_query": search_query,
                "response": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error processing your request: {str(e)}"
            print(error_msg)
            return "I'm sorry, there was an error processing your request. Please try again later."
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history.clear()
    
    def _is_greeting_or_casual(self, user_input: str) -> bool:
        """
        Check if user input is a greeting or casual message (not a company query)
        
        Args:
            user_input (str): User's input
            
        Returns:
            bool: True if it's a greeting/casual, False if it's a company query
        """
        user_input_lower = user_input.lower().strip()
        
        # Common greetings and casual phrases
        greetings = [
            'hi', 'hello', 'hey', 'hii', 'hiii', 'hiiii',
            'good morning', 'good afternoon', 'good evening',
            'how are you', 'how are you doing', 'whats up', "what's up",
            'thanks', 'thank you', 'ok', 'okay', 'alright',
            'nice', 'great', 'awesome', 'cool', 'fine',
            'yes', 'no', 'yeah', 'yep', 'nope',
            'good', 'bad', 'excellent', 'perfect'
        ]
        
        # Check if the entire input is just a greeting
        if user_input_lower in greetings:
            return True
        
        # Check if input starts with greeting but is very short (likely just greeting)
        for greeting in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']:
            if user_input_lower.startswith(greeting) and len(user_input_lower) <= len(greeting) + 5:
                return True
        
        return False
    
    def _handle_greeting(self, user_input: str) -> str:
        """
        Handle greeting messages without using search
        
        Args:
            user_input (str): User's greeting
            
        Returns:
            str: Friendly greeting response
        """
        user_input_lower = user_input.lower().strip()
        
        if any(greeting in user_input_lower for greeting in ['hi', 'hello', 'hey']):
            return """👋 Hello! I'm your Company Information Assistant. 

I can help you find information about any company including:
• Company overview and business model
• Leadership and key executives  
• Financial information and performance
• Products and services
• Recent news and developments

Just ask me about any company you're interested in! For example:
"Tell me about Apple Inc." or "Who is the CEO of Microsoft?"
"""
        
        elif any(phrase in user_input_lower for phrase in ['how are you', 'whats up', "what's up"]):
            return """I'm doing great, thank you for asking! 😊 

I'm here to help you find information about companies. What company would you like to know more about?"""
        
        elif any(phrase in user_input_lower for phrase in ['thanks', 'thank you']):
            return """You're welcome! 😊 

Is there any company information you'd like me to help you find?"""
        
        else:
            return """Hello! 👋 

I'm your Company Information Assistant. Ask me about any company and I'll provide you with detailed information!"""
    
    def _check_rate_limit(self) -> bool:
        """
        Check if user has exceeded rate limit (3 searches per minute)
        
        Returns:
            bool: True if within rate limit, False if exceeded
        """
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        while self.search_timestamps and current_time - self.search_timestamps[0] > 60: # Created timestamp of 1 min 
            # it automatically resets the max_search_per_min after 1 minute
            self.search_timestamps.popleft()
        
        # Check if user has made too many searches
        if len(self.search_timestamps) >= self.max_searches_per_minute:
            return False
        
        # Add current search timestamp
        self.search_timestamps.append(current_time)
        return True
    
    def chat(self, user_input: str) -> str:
        """
        Main chat interface
        
        Args:
            user_input (str): User's input/question
            
        Returns:
            str: Chatbot response
        """
        if not user_input.strip():
            return "Please ask me something about a company!"
        
        # Handle special commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            return "Thank you for using the Company Chatbot! Goodbye!"
        
        if user_input.lower() in ['clear', 'reset']:
            self.clear_conversation_history()
            return "Conversation history cleared!"
        
        if user_input.lower() in ['help']:
            return self._get_help_message()
        
        # Process company-related questions
        return self.get_company_information(user_input)
    
    def _get_help_message(self) -> str:
        """Get help message for users"""
        return """
🤖 Company Chatbot Help

I can help you find information about companies! Here's what you can ask:

📋 **Examples of questions:**
• "Tell me about Apple Inc."
• "What does Microsoft do?"
• "Who is the CEO of Tesla?"
• "What are Google's recent financial results?"
• "Tell me about Amazon's business model"

⚡ **Special commands:**
• 'help' - Show this help message
• 'clear' or 'reset' - Clear conversation history
• 'exit', 'quit', or 'bye' - Exit the chatbot

💡 **Tips:**
• Be specific about the company name
• You can ask about financials, leadership, products, services, and more
• I use real-time search to get the latest information

Just ask me anything about a company and I'll help you find the information!
        """
