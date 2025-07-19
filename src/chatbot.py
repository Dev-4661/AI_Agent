from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict, Any
from config.settings import Config
from templates.prompts import get_company_info_prompt, get_search_query_prompt
from utils.search_tool import TavilySearchTool

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
    
    def chat(self, user_input: str) -> str:
        """
        Main chat interface
        
        Args:
            user_input (str): User's input/question, which may include file content
            
        Returns:
            str: Chatbot response
        """
        if not user_input.strip():
            return "Please ask me something about a company or upload a document!"
        
        # Handle special commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            return "Thank you for using the Company Chatbot! Goodbye!"
        
        if user_input.lower() in ['clear', 'reset']:
            self.clear_conversation_history()
            return "Conversation history cleared!"
        
        if user_input.lower() in ['help']:
            return self._get_help_message()
        
        # Check if the input contains file content
        if user_input.startswith("Document content from") or user_input.startswith("Image file:"):
            try:
                # For file content, always process it
                if "\n\nUser question:" in user_input:
                    file_content, user_question = user_input.split("\n\nUser question:", 1)
                    user_question = user_question.strip()
                    if not user_question:
                        user_question = "Please provide a detailed summary of this document."
                else:
                    file_content = user_input
                    user_question = "Please provide a detailed summary of this document."
                
                # Process the file content
                return self._process_file_content(file_content, user_question)
                
            except Exception as e:
                return f"I encountered an error processing the document: {str(e)}"
        
        # Process regular company-related questions with web search
        return self.get_company_information(user_input)
    
    def _process_file_content(self, file_content: str, user_question: str = "") -> str:
        """Process uploaded file content and extract company information."""
        try:
            # Create system and human messages for the LLM
            system_message = SystemMessage(content="""You are an expert at extracting and summarizing company information from documents.
            Extract all available company information in a clear, structured format. If information is not available, state "Not specified".""")
            
            human_message = HumanMessage(content=f"""Please analyze this document and extract company information:
            
            Document content:
            {file_content}
            
            Extract information in this format:
            **Company Name:** [Name]
            **Industry/Sector:** [Industry]
            **Location:** [Location]
            **Key Products/Services:** [List]
            **Contact Information:** [Details]
            **About the Company:** [Description]
            **Key People/Leadership:** [Names/Positions]
            **Additional Notes:** [Any other relevant info]
            
            User's question: {user_question or 'Extract all company information'}
            """)
            
            # Generate response using the LLM
            response = self.llm.invoke([system_message, human_message])
            
            # Format the response
            formatted_response = f"Here's the company information I found in the document:\n\n{response.content.strip()}"
            
            # Store in conversation history
            self.conversation_history.append({
                "question": user_question or "Analyze the uploaded document",
                "file_content": file_content[:500] + "..." if len(file_content) > 500 else file_content,
                "response": formatted_response
            })
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Error processing the document: {str(e)}"
            print(error_msg)
            return "I'm sorry, there was an error processing your document. Please try again."
    
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
