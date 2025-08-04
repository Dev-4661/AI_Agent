"""
Configuration and integration file for agent-based business intelligence system.

This module provides configuration and integration examples for converting your
existing sequential chain approach to an intelligent agent-based system with
Tavily search capabilities.
"""

import os
from typing import Dict, Any, Optional, List
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        from langchain_openai import ChatOpenAI
        GEMINI_AVAILABLE = False
    except ImportError:
        from langchain.llms import OpenAI as ChatOpenAI
        GEMINI_AVAILABLE = False

# Try to import Tavily search - handle gracefully if not available
try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilySearchResults = None

from agents.business_intelligence_agent import AgentWorkflowManager


class AgentBasedBusinessIntelligenceConfig:
    """Configuration class for agent-based business intelligence system."""
    
    def __init__(self):
        # API Keys - set these in your environment variables
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        # LLM Configuration for Gemini
        self.llm_model = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))  # Low temperature for consistent, factual responses
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        
        # Agent Configuration
        self.max_search_results = 5
        self.search_depth = "advanced"
        self.max_agent_iterations = 10
        
        # Required business intelligence fields
        self.required_fields = [
            "company_name", "contact_phone", "email_id", "contact_person_name",
            "location", "address", "founder_ceo_md", "company_revenue",
            "market_response", "leadership_team", "vision", "mission",
            "top_5_challenges", "business_problem_impact"
        ]
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is available."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        # Tavily is optional - system will work without it
        if not self.tavily_api_key:
            print("Warning: TAVILY_API_KEY not found. Agent system will use basic search only.")
        return True
    
    def get_llm(self):
        """Get configured LLM instance using Gemini."""
        if GEMINI_AVAILABLE:
            return ChatGoogleGenerativeAI(
                model=self.llm_model,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                google_api_key=self.google_api_key
            )
        else:
            # Fallback to basic LLM if Gemini not available
            raise ImportError("langchain_google_genai not available. Please install: pip install langchain-google-genai")


class BusinessIntelligenceService:
    """
    Main service class that replaces your existing sequential chains with
    intelligent agent-based approach.
    """
    
    def __init__(self, config: Optional[AgentBasedBusinessIntelligenceConfig] = None):
        try:
            self.config = config or AgentBasedBusinessIntelligenceConfig()
            self.config.validate_configuration()
            
            # Initialize LLM
            self.llm = self.config.get_llm()
            
            # Initialize Agent Workflow Manager with better error handling
            self.agent_manager = AgentWorkflowManager(
                llm=self.llm,
                tavily_api_key=self.config.tavily_api_key
            )
            self.initialized = True
        except Exception as e:
            print(f"Warning: Agent system initialization failed: {e}")
            self.agent_manager = None
            self.initialized = False
            # Don't raise error - allow fallback to work
    
    def research_company(self, company_query: str, initial_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main method to research a company using intelligent agents.
        
        This replaces your existing sequential chain approach with an intelligent
        agent that can make decisions about what information to search for.
        
        Args:
            company_query: Company name or query to research
            initial_data: Any initial data available about the company
        
        Returns:
            Structured business intelligence in the required 14-point format
        """
        try:
            # Check if agent system is properly initialized
            if not self.initialized or not self.agent_manager:
                return {
                    "success": False,
                    "error": "Agent system not properly initialized",
                    "response": "I'm experiencing technical difficulties with the enhanced search system. Please try again later or contact support if the issue persists."
                }
            
            # Use agent to research company
            result = self.agent_manager.process_company_query(company_query)
            
            if result["success"]:
                # Pass the original query to formatting for proper multi-company detection
                formatted_response = self._format_structured_response(result["company_intelligence"], company_query)
                return {
                    "success": True,
                    "response": formatted_response,
                    "structured_data": result["company_intelligence"],
                    "agent_reasoning": result.get("raw_result", "")
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "response": f"Unable to gather complete business intelligence: {result['error']}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I'm experiencing technical difficulties with the research system. Please try again later."
            }
    
    def analyze_document(self, ocr_text: str) -> Dict[str, Any]:
        """
        Analyze document using intelligent agents.
        
        This replaces your existing document analysis approach with an intelligent
        agent that can extract company information and research additional details.
        
        Args:
            ocr_text: Text extracted from document via OCR
        
        Returns:
            Structured business intelligence in the required 14-point format
        """
        try:
            # Use agent to analyze document and research company
            result = self.agent_manager.process_document_analysis(ocr_text)
            
            if result["success"]:
                formatted_response = self._format_structured_response(result["company_intelligence"], ocr_text)
                return {
                    "success": True,
                    "response": formatted_response,
                    "structured_data": result["company_intelligence"],
                    "ocr_analysis": "Document analyzed and company research completed"
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "response": f"Unable to analyze document and research company: {result['error']}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Error in document analysis: {str(e)}"
            }
    
    def process_follow_up(self, company_name: str, previous_context: str, 
                         new_question: str) -> Dict[str, Any]:
        """
        Process follow-up questions using intelligent agents.
        
        Args:
            company_name: Name of the company
            previous_context: Previous conversation/research context
            new_question: New question or research direction
        
        Returns:
            Updated business intelligence addressing the follow-up question
        """
        try:
            result = self.agent_manager.process_follow_up(company_name, previous_context, new_question)
            
            if result["success"]:
                # Use new_question as the prompt for formatting
                formatted_response = self._format_structured_response(result["company_intelligence"], new_question)
                return {
                    "success": True,
                    "response": formatted_response,
                    "structured_data": result["company_intelligence"],
                    "follow_up_analysis": "Follow-up research completed with updated intelligence"
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "response": f"Unable to process follow-up research: {result['error']}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Error in follow-up research: {str(e)}"
            }
    
    def _format_structured_response(self, intelligence_data: Dict[str, Any], user_prompt: str = "") -> str:
        """
        Format the structured intelligence data into a natural, ChatGPT-like response.
        If the prompt is for a list of companies, format as a list with contact details. Otherwise, use the 14-point format.
        Args:
            intelligence_data: Structured company intelligence data
            user_prompt: The original user prompt (for query type detection)
        Returns:
            Formatted response string
        """
        # Detect if the prompt is for a list of companies
        list_keywords = ["list", "companies", "show", "top", "find", "give me", "which companies", "who are"]
        is_list_query = any(word in user_prompt.lower() for word in list_keywords)

        # If multi-company, format as a list
        if is_list_query and isinstance(intelligence_data, list):
            if not intelligence_data:
                return "No companies found matching your criteria."
            response = "Here are the companies you requested:\n"
            for idx, company in enumerate(intelligence_data, 1):
                response += f"\n{idx}. {company.get('company_name', 'N/A')} - {company.get('description', 'N/A')}\n"
                response += f"   📞 Phone: {company.get('contact_phone', 'N/A')} | 📧 Email: {company.get('email_id', 'N/A')} | 🌐 Website: {company.get('website', 'N/A')} | 💼 LinkedIn: {company.get('linkedin', 'N/A')} | 📍 Location: {company.get('location', 'N/A')}\n"
            return response

        # Otherwise, use the 14-point format for single company
        formatted_response = f"""**Company Name:** {intelligence_data.get('company_name', 'Information not available')}

**Contact Ph #:** {intelligence_data.get('contact_phone', 'Information not available')}

**Email Id:** {intelligence_data.get('email_id', 'Information not available')}

**Contact Person Name:** {intelligence_data.get('contact_person_name', 'Information not available')}

**Location:** {intelligence_data.get('location', 'Information not available')}

**Address:** {intelligence_data.get('address', 'Information not available')}

**Founder/CEO/MD:** {intelligence_data.get('founder_ceo_md', 'Information not available')}

**Company Revenue:** {intelligence_data.get('company_revenue', 'Information not available')}

**Market Response:** {intelligence_data.get('market_response', 'Information not available')}

**Leadership Team:** {intelligence_data.get('leadership_team', 'Information not available')}

**Vision:** {intelligence_data.get('vision', 'Information not available')}

**Mission:** {intelligence_data.get('mission', 'Information not available')}

**Top 5 or Major Challenges:**"""
        challenges = intelligence_data.get('top_5_challenges', ['Information not available'])
        for i, challenge in enumerate(challenges, 1):
            formatted_response += f"\n{i}. {challenge}"
        formatted_response += f"\n\n**Business Problem and its Business Impact:** {intelligence_data.get('business_problem_impact', 'Information not available')}"
        return formatted_response
    
    def get_missing_information_fields(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """
        Identify which fields are missing or incomplete in the intelligence data.
        
        Args:
            intelligence_data: Current intelligence data
        
        Returns:
            List of missing field names
        """
        missing_fields = []
        
        for field in self.config.required_fields:
            value = intelligence_data.get(field, "")
            if not value or value == "Information not available" or value == "N/A":
                missing_fields.append(field)
        
        return missing_fields
    
    def trigger_additional_search(self, company_name: str, missing_fields: List[str]) -> Dict[str, Any]:
        """
        Trigger additional targeted searches for missing information.
        
        Args:
            company_name: Name of the company
            missing_fields: List of missing field names
        
        Returns:
            Additional intelligence data
        """
        search_query = f"Gather missing information for {company_name}: {', '.join(missing_fields)}"
        return self.research_company(search_query)


# Integration example for your existing application
class ApplicationIntegration:
    """
    Example integration class showing how to replace your existing chains
    with the new agent-based approach.
    """
    
    def __init__(self):
        # Initialize the business intelligence service with error handling
        try:
            self.bi_service = BusinessIntelligenceService()
            self.initialized = True
        except Exception as e:
            print(f"Warning: ApplicationIntegration failed to initialize: {e}")
            self.bi_service = None
            self.initialized = False
    
    def handle_company_search(self, company_query: str) -> str:
        """
        Handle company search requests.
        Replace your existing company_chain usage with this method.
        """
        if not self.initialized or not self.bi_service:
            return "I'm experiencing technical difficulties with the enhanced search system. Please try the basic search or contact support if the issue persists."
        
        try:
            result = self.bi_service.research_company(company_query)
            return result["response"]
        except Exception as e:
            return "I'm experiencing some technical difficulties. Please try again in a moment or upload a document for analysis instead."
    
    def handle_image_analysis(self, ocr_text: str) -> str:
        """
        Handle image/document analysis requests.
        Replace your existing image analysis chain with this method.
        """
        if not self.initialized or not self.bi_service:
            return "I've extracted text from your document, but detailed analysis is temporarily unavailable. Please try again later."
        
        try:
            result = self.bi_service.analyze_document(ocr_text)
            return result["response"]
        except Exception as e:
            return "I've processed your document but encountered some difficulties with the detailed analysis. Please try again later."
    
    def handle_follow_up_question(self, company_name: str, context: str, question: str) -> str:
        """
        Handle follow-up questions.
        Replace your existing follow-up chain with this method.
        """
        result = self.bi_service.process_follow_up(company_name, context, question)
        return result["response"]
    
    def generate_email_from_intelligence(self, intelligence_data: Dict[str, Any]) -> str:
        """
        Generate email using the structured intelligence data.
        This can be integrated with your existing email generation logic.
        """
        # Extract key insights for email generation
        key_insights = {
            "company_challenges": intelligence_data.get("top_5_challenges", []),
            "business_impact": intelligence_data.get("business_problem_impact", ""),
            "market_position": intelligence_data.get("market_response", ""),
            "leadership": intelligence_data.get("leadership_team", ""),
            "revenue_info": intelligence_data.get("company_revenue", "")
        }
        
        # Use your existing email generation logic with these insights
        # This would integrate with your email_generator.py module
        return f"Email generation with insights: {key_insights}"


# Environment setup example
def setup_environment_variables():
    """
    Example of how to set up environment variables for the agent-based system.
    
    Add these to your .env file or set them in your deployment environment:
    """
    environment_setup = """
    # Add these to your .env file:
    OPENAI_API_KEY=your_openai_api_key_here
    TAVILY_API_KEY=your_tavily_api_key_here
    
    # Optional configuration
    LLM_MODEL=gpt-4-turbo-preview
    AGENT_MAX_ITERATIONS=10
    SEARCH_MAX_RESULTS=5
    """
    
    print("Environment Variables Setup:")
    print(environment_setup)


# Usage examples
if __name__ == "__main__":
    # Example usage of the new agent-based system
    
    # 1. Setup (do this once)
    print("Setting up Business Intelligence Service...")
    bi_service = BusinessIntelligenceService()
    
    # 2. Research a company
    print("\nResearching company...")
    company_result = bi_service.research_company("Tesla Inc")
    print("Company Research Result:")
    print(company_result["response"])
    
    # 3. Analyze a document (example with OCR text)
    print("\nAnalyzing document...")
    ocr_text = "TCS - Tata Consultancy Services, Leading IT services company..."
    document_result = bi_service.analyze_document(ocr_text)
    print("Document Analysis Result:")
    print(document_result["response"])
    
    # 4. Follow-up question
    print("\nProcessing follow-up question...")
    followup_result = bi_service.process_follow_up(
        "Tesla Inc",
        "Previous research on Tesla completed",
        "What are Tesla's main business challenges in 2024?"
    )
    print("Follow-up Result:")
    print(followup_result["response"])
    
    # 5. Integration example
    print("\nIntegration Example...")
    app_integration = ApplicationIntegration()
    result = app_integration.handle_company_search("Apple Inc")
    print("Integrated Search Result:")
    print(result)
