"""
Business Intelligence Agent Implementation with LangChain and Tavily Search

This module implements an intelligent agent-based approach for comprehensive
company research and business intelligence gathering using LangChain agents
and Tavily search as tools.
"""

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.agents.agent import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain_core.tools import tool
try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilySearchResults = None

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List, Any, Optional
import json
import re


class BusinessIntelligenceAgent:
    """
    Intelligent Business Intelligence Agent that uses LangChain agents
    and Tavily search to gather comprehensive company information.
    """
    
    def __init__(self, llm, tavily_api_key: str = None):
        """
        Initialize the Business Intelligence Agent.
        
        Args:
            llm: Language model instance (e.g., ChatGoogleGenerativeAI)
            tavily_api_key: API key for Tavily search service (optional)
        """
        self.llm = llm
        self.tavily_api_key = tavily_api_key
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize Tavily search tool if available
        if TAVILY_AVAILABLE and tavily_api_key:
            try:
                self.tavily_tool = TavilySearchResults(
                    api_key=tavily_api_key,
                    max_results=5,
                    search_depth="advanced"
                )
                self.search_available = True
            except Exception as e:
                print(f"Warning: Tavily search initialization failed: {e}")
                self.tavily_tool = None
                self.search_available = False
        else:
            self.tavily_tool = None
            self.search_available = False
        
        # Required company information structure
        self.required_fields = [
            "company_name", "contact_phone", "email_id", "contact_person_name",
            "location", "address", "founder_ceo_md", "company_revenue",
            "market_response", "leadership_team", "vision", "mission",
            "top_5_challenges", "business_problem_impact"
        ]
        
        # Initialize agent tools
        self.tools = self._create_tools()
        
        # Initialize the agent
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent using modern LangChain tool patterns."""
        
        tools = []
        
        # Add Tavily search if available - use direct run method to avoid schema issues
        if self.search_available and self.tavily_tool:
            tools.append(
                Tool.from_function(
                    name="tavily_search",
                    description="Search the internet for comprehensive company information. Use specific queries like 'company_name headquarters contact information' or 'company_name CEO leadership team'",
                    func=self._safe_tavily_search_wrapper,
                )
            )
        
        # Add comprehensive research tool that does everything in one go
        tools.append(
            Tool.from_function(
                name="comprehensive_company_research",
                description="Conduct comprehensive research for a company and return all 14 required fields in structured format",
                func=self._comprehensive_research,
            )
        )
        
        return tools
    
    def _safe_tavily_search_wrapper(self, query: str) -> str:
        """Safe wrapper for Tavily search that ensures string output."""
        try:
            if self.search_available and self.tavily_tool:
                # Use invoke method which is more reliable
                result = self.tavily_tool.invoke({"query": query})
                
                # Handle different result formats
                if isinstance(result, str):
                    return result
                elif isinstance(result, list):
                    # Extract content from list of results
                    search_results = []
                    for item in result:
                        if isinstance(item, dict):
                            content = item.get('content', item.get('snippet', item.get('title', str(item))))
                            if content:
                                search_results.append(content)
                        else:
                            search_results.append(str(item))
                    return "\n".join(search_results[:5])  # Limit to top 5 results
                elif isinstance(result, dict):
                    return result.get('content', result.get('snippet', str(result)))
                else:
                    return str(result)
            else:
                return f"Internet search not available. Using general knowledge for: {query}"
        except Exception as e:
            # Fallback to general knowledge when search fails
            return f"Search encountered an error for '{query}'. Proceeding with general knowledge."
    
    def _comprehensive_research(self, company_query: str) -> str:
        """Comprehensive research function that gathers all company information using Tavily search."""
        
        # Extract company name
        company_name = self._extract_main_company_name(company_query)
        
        # If Tavily search is available, use it to gather comprehensive information
        if self.search_available and self.tavily_tool:
            search_results = []
            
            # Multiple targeted searches for comprehensive information
            search_queries = [
                f"{company_name} company headquarters contact information phone email address",
                f"{company_name} CEO founder leadership team management executives",
                f"{company_name} annual revenue financial performance 2024 earnings",
                f"{company_name} vision mission statement corporate values",
                f"{company_name} business challenges market competition industry problems",
                f"{company_name} market position industry reputation customer feedback"
            ]
            
            for query in search_queries:
                try:
                    result = self._safe_tavily_search_wrapper(query)
                    search_results.append(f"Search for '{query}':\n{result}\n")
                except Exception as e:
                    search_results.append(f"Search error for '{query}': {str(e)}\n")
            
            # Combine search results and create comprehensive analysis
            combined_search_data = "\n---\n".join(search_results)
            
            # Use LLM to analyze search results and format properly
            analysis_prompt = f"""
            Based on the following search results, provide comprehensive business intelligence for {company_name} in the exact format requested:
            
            Search Results:
            {combined_search_data}
            
            Analyze these search results and present the information in this EXACT format:
            
            **Company Name:** [Full official company name]
            **Contact Ph #:** [Primary business phone number with country code if found]
            **Email Id:** [Official business email if found]
            **Contact Person Name:** [Current CEO name]
            **Location:** [Headquarters city and country]
            **Address:** [Complete business address]
            **Founder/CEO/MD:** [Current CEO name and background]
            **Company Revenue:** [Latest revenue with year and currency]
            **Market Response:** [Market position and industry reputation]
            **Leadership Team:** [Key executives and roles]
            **Vision:** [Official vision statement]
            **Mission:** [Official mission statement]
            **Top 5 or Major Challenges:**
            1. [First challenge based on search results]
            2. [Second challenge based on search results]
            3. [Third challenge based on search results]
            4. [Fourth challenge based on search results]
            5. [Fifth challenge based on search results]
            **Business Problem and its Business Impact:** [Detailed analysis based on search findings]
            
            Extract specific information from the search results where available. If search results don't contain specific information, use your knowledge to fill gaps.
            """
            
            try:
                result = self.llm.invoke(analysis_prompt).content
                return result
            except Exception as e:
                return f"Error analyzing search results: {str(e)}"
        
        else:
            # Fallback to LLM knowledge when search is not available
            research_prompt = f"""
            Based on your comprehensive knowledge, provide detailed business intelligence for: {company_name}
            
            You must provide information in this EXACT format:
            
            **Company Name:** [Full official company name]
            **Contact Ph #:** [Primary business phone number or indicate "Available via official website"]
            **Email Id:** [Official contact email or indicate pattern like "contact@company.com"]
            **Contact Person Name:** [Current CEO name]
            **Location:** [Headquarters city and country]
            **Address:** [Complete business address or headquarters location]
            **Founder/CEO/MD:** [Name and brief background of current CEO/founder]
            **Company Revenue:** [Latest revenue figures with year and currency]
            **Market Response:** [Market position, industry reputation, customer feedback]
            **Leadership Team:** [Key executives and their roles]
            **Vision:** [Official company vision statement]
            **Mission:** [Official company mission statement]
            **Top 5 or Major Challenges:**
            1. [Specific industry challenge]
            2. [Technology/digital transformation challenge]
            3. [Market competition challenge]
            4. [Regulatory/compliance challenge]
            5. [Operational/scaling challenge]
            **Business Problem and its Business Impact:** [Detailed analysis of challenges and business impact]
            
            Provide specific, factual information where available. For {company_name}, use your knowledge of this company to provide accurate details.
            """
            
            try:
                # Get comprehensive information from LLM
                result = self.llm.invoke(research_prompt).content
                return result
            except Exception as e:
                return f"Error conducting comprehensive research: {str(e)}"
    
    def _extract_main_company_name(self, query: str) -> str:
        """Extract the main company name from query, handling common patterns."""
        import re
        
        # Handle common patterns like "TCS (Tata Consultancy Services)"
        parentheses_match = re.search(r'([^()]+)\s*\(([^()]+)\)', query)
        if parentheses_match:
            part1, part2 = parentheses_match.groups()
            # Usually the longer name is the full name
            if len(part1.strip()) > len(part2.strip()):
                return part1.strip()
            else:
                return part2.strip()
        
        # Remove common words and get company name
        words = query.split()
        common_words = {"search", "for", "about", "company", "information", "details", "tell", "me", "find", "research"}
        company_words = [word for word in words if word.lower() not in common_words]
        
        if company_words:
            return " ".join(company_words[:4])  # Take up to 4 words for company name
        
        return query.strip()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools and prompts."""
        
        # System message for the agent
        system_message = SystemMessage(content="""
        You are an expert Business Intelligence Agent. Your task is to provide comprehensive company research using available search tools.
        
        IMPORTANT INSTRUCTIONS:
        1. For company research requests, ALWAYS use the comprehensive_company_research tool first
        2. If you need additional specific information, use tavily_search with targeted queries
        3. Present the final result in the exact 14-point format without showing intermediate steps
        4. Do not explain your process - just provide the final formatted research results
        
        Available tools:
        - comprehensive_company_research: Use this for complete company research
        - tavily_search: Use this for specific additional information if needed
        
        Always provide comprehensive results in the structured format.
        """)
        
        # Initialize agent with CONVERSATIONAL_REACT_DESCRIPTION for better tool usage
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,  # Enable verbose to see tool usage
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )
        
        return agent
    
    def research_company(self, company_query: str, initial_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Research a company and return comprehensive business intelligence.
        
        Args:
            company_query: The company name or query to research
            initial_data: Any initial data available about the company
        
        Returns:
            Dict containing structured business intelligence
        """
        
        # Use agent-based research with Tavily search when available
        return self._agent_based_research(company_query, initial_data)
    
    def _agent_based_research(self, company_query: str, initial_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Agent-based research that properly uses Tavily search when available."""
        
        company_name = self._extract_main_company_name(company_query)
        
        # Create enhanced research prompt for the agent
        research_prompt = f"""
        Research comprehensive business intelligence for: {company_name}
        
        {f"Initial available data: {initial_data}" if initial_data else ""}
        
        Use all available search tools to gather comprehensive information and present it in this EXACT format:
        
        **Company Name:** [Full official company name]
        **Contact Ph #:** [Primary business phone number with country code]
        **Email Id:** [Official business email or contact email]
        **Contact Person Name:** [Current CEO name]
        **Location:** [Headquarters city and country]
        **Address:** [Complete business address]
        **Founder/CEO/MD:** [Current CEO name and background]
        **Company Revenue:** [Latest revenue with year and currency]
        **Market Response:** [Market position and industry reputation]
        **Leadership Team:** [Key executives and roles]
        **Vision:** [Official vision statement]
        **Mission:** [Official mission statement]
        **Top 5 or Major Challenges:**
        1. [First challenge]
        2. [Second challenge]
        3. [Third challenge]
        4. [Fourth challenge]
        5. [Fifth challenge]
        **Business Problem and its Business Impact:** [Detailed analysis]
        
        Use internet search tools to find current and accurate information.
        """
        
        try:
            if self.search_available:
                # Use agent with Tavily search
                result = self.agent.run(research_prompt)
            else:
                # Fallback to direct LLM research
                return self._direct_llm_research(company_query, initial_data)
            
            # Parse the result
            structured_result = self._parse_agent_result(result)
            
            return {
                "success": True,
                "company_intelligence": structured_result,
                "raw_result": result
            }
            
        except Exception as e:
            # Fallback to direct LLM research if agent fails
            print(f"Agent research failed: {e}, falling back to direct LLM research")
            return self._direct_llm_research(company_query, initial_data)
    
    def _direct_llm_research(self, company_query: str, initial_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Direct LLM research bypassing agent complexity."""
        
        company_name = self._extract_main_company_name(company_query)
        
        # Enhanced prompt for direct LLM research
        research_prompt = f"""
        You are a business intelligence expert. Provide comprehensive business information for: {company_name}
        
        {f"Available initial data: {initial_data}" if initial_data else ""}
        
        Present the information in this EXACT format (use this exact structure):
        
        **Company Name:** [Full official company name]
        **Contact Ph #:** [Main phone number or "Available via official website/headquarters"]
        **Email Id:** [Official email or "Available via official website"]
        **Contact Person Name:** [Current CEO name]
        **Location:** [Headquarters city and country]
        **Address:** [Complete business address]
        **Founder/CEO/MD:** [Current CEO name and background]
        **Company Revenue:** [Latest revenue with year and currency]
        **Market Response:** [Market position and industry reputation]
        **Leadership Team:** [Key executives and roles]
        **Vision:** [Official vision statement]
        **Mission:** [Official mission statement]
        **Top 5 or Major Challenges:**
        1. [First major challenge]
        2. [Second major challenge]  
        3. [Third major challenge]
        4. [Fourth major challenge]
        5. [Fifth major challenge]
        **Business Problem and its Business Impact:** [Detailed analysis]
        
        For well-known companies like TCS, provide specific factual information from your knowledge. Be comprehensive and accurate.
        """
        
        try:
            # Use LLM directly for better control
            result = self.llm.invoke(research_prompt).content
            
            # Parse the result
            structured_result = self._parse_agent_result(result)
            
            return {
                "success": True,
                "company_intelligence": structured_result,
                "raw_result": result
            }
            
        except Exception as e:
            # Fallback with template
            return {
                "success": False,
                "error": str(e),
                "company_intelligence": self._get_enhanced_template(company_name),
                "raw_result": f"Research failed for {company_name}. Error: {str(e)}"
            }
    
    def _get_enhanced_template(self, company_name: str) -> Dict[str, Any]:
        """Get enhanced template with better default information."""
        return {
            "company_name": company_name,
            "contact_phone": f"Contact information for {company_name} available through official website",
            "email_id": f"Official contact available via {company_name.lower().replace(' ', '')}.com", 
            "contact_person_name": f"CEO information for {company_name} requires current research",
            "location": f"Headquarters location for {company_name} - please check official sources",
            "address": f"Complete address available on {company_name} official website",
            "founder_ceo_md": f"Leadership information for {company_name} available in company reports",
            "company_revenue": f"Revenue information for {company_name} available in financial reports",
            "market_response": f"Market analysis for {company_name} available through industry reports",
            "leadership_team": f"Executive team information for {company_name} on company website",
            "vision": f"Vision statement for {company_name} available in corporate materials",
            "mission": f"Mission statement for {company_name} in company documentation",
            "top_5_challenges": [
                "Market competition and industry positioning",
                "Digital transformation and technology adoption", 
                "Talent acquisition and retention strategies",
                "Regulatory compliance and industry standards",
                "Operational efficiency and growth scalability"
            ],
            "business_problem_impact": f"Business impact analysis for {company_name} requires comprehensive market research and current industry data."
        }
    
    def _parse_agent_result(self, result: str) -> Dict[str, Any]:
        """Parse the agent result into structured format."""
        
        # Initialize structured data
        structured_data = {}
        
        # Define field mappings
        field_patterns = {
            "company_name": r"\*\*Company Name:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "contact_phone": r"\*\*Contact Ph #:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "email_id": r"\*\*Email Id:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "contact_person_name": r"\*\*Contact Person Name:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "location": r"\*\*Location:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "address": r"\*\*Address:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "founder_ceo_md": r"\*\*Founder/CEO/MD:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "company_revenue": r"\*\*Company Revenue:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "market_response": r"\*\*Market Response:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "leadership_team": r"\*\*Leadership Team:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "vision": r"\*\*Vision:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)",
            "mission": r"\*\*Mission:\*\*\s*(.*?)(?=\n\*\*|\n\n|$)"
        }
        
        # Extract fields using regex
        for field, pattern in field_patterns.items():
            match = re.search(pattern, result, re.IGNORECASE | re.DOTALL)
            if match:
                structured_data[field] = match.group(1).strip()
            else:
                structured_data[field] = "Information not available"
        
        # Extract challenges (special handling for numbered list)
        challenges_pattern = r"\*\*Top 5 or Major Challenges:\*\*\s*(.*?)(?=\*\*Business Problem|$)"
        challenges_match = re.search(challenges_pattern, result, re.IGNORECASE | re.DOTALL)
        if challenges_match:
            challenges_text = challenges_match.group(1).strip()
            challenges = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\n\*\*|$)', challenges_text, re.DOTALL)
            structured_data["top_5_challenges"] = [challenge.strip() for challenge in challenges if challenge.strip()]
        
        if not structured_data.get("top_5_challenges"):
            structured_data["top_5_challenges"] = ["Information not available"]
        
        # Extract business problem and impact
        business_problem_pattern = r"\*\*Business Problem and its Business Impact:\*\*\s*(.*?)(?=\n\*\*|$)"
        business_problem_match = re.search(business_problem_pattern, result, re.IGNORECASE | re.DOTALL)
        if business_problem_match:
            structured_data["business_problem_impact"] = business_problem_match.group(1).strip()
        else:
            structured_data["business_problem_impact"] = "Information not available"
        
        return structured_data
    
    def analyze_document(self, ocr_text: str) -> Dict[str, Any]:
        """
        Analyze document OCR text and research the company.
        
        Args:
            ocr_text: Text extracted from document via OCR
        
        Returns:
            Dict containing structured business intelligence
        """
        
        # Extract company name from OCR text and research
        analysis_prompt = f"""
        Extract the company name from this OCR text and provide comprehensive business intelligence:
        
        OCR Text:
        {ocr_text}
        
        Identify the main company mentioned and provide complete business intelligence in the 14-point format.
        """
        
        return self.research_company(analysis_prompt)
    
    def generate_follow_up_research(self, company_name: str, previous_context: str, 
                                  new_question: str) -> Dict[str, Any]:
        """
        Generate follow-up research based on previous context and new questions.
        """
        
        followup_prompt = f"""
        Based on previous research for {company_name} and this new question: {new_question}
        
        Previous Context: {previous_context}
        
        Provide updated comprehensive business intelligence addressing the new question while maintaining the 14-point structure.
        """
        
        return self.research_company(followup_prompt)


# Usage example and configuration
def create_business_intelligence_agent(llm, tavily_api_key: str = None) -> BusinessIntelligenceAgent:
    """
    Factory function to create a configured Business Intelligence Agent.
    
    Args:
        llm: Language model instance (e.g., ChatGoogleGenerativeAI)
        tavily_api_key: Tavily search API key (optional)
    
    Returns:
        Configured BusinessIntelligenceAgent instance
    """
    return BusinessIntelligenceAgent(llm, tavily_api_key)


# Integration example with existing workflow
class AgentWorkflowManager:
    """
    Manager class to integrate the agent-based approach with existing application workflow.
    """
    
    def __init__(self, llm, tavily_api_key: str = None):
        self.agent = create_business_intelligence_agent(llm, tavily_api_key)
    
    def process_company_query(self, query: str) -> Dict[str, Any]:
        """Process a company query using the intelligent agent."""
        return self.agent.research_company(query)
    
    def process_document_analysis(self, ocr_text: str) -> Dict[str, Any]:
        """Process document analysis using the intelligent agent."""
        return self.agent.analyze_document(ocr_text)
    
    def process_follow_up(self, company_name: str, context: str, question: str) -> Dict[str, Any]:
        """Process follow-up questions using the intelligent agent."""
        return self.agent.generate_follow_up_research(company_name, context, question)
    
    def format_response_for_ui(self, agent_result: Dict[str, Any]) -> str:
        """Format agent result for UI display."""
        if not agent_result.get("success", False):
            return f"Error: {agent_result.get('error', 'Unknown error occurred')}"
        
        intelligence = agent_result["company_intelligence"]
        
        formatted_response = f"""**Company Name:** {intelligence.get('company_name', 'N/A')}

**Contact Ph #:** {intelligence.get('contact_phone', 'N/A')}

**Email Id:** {intelligence.get('email_id', 'N/A')}

**Contact Person Name:** {intelligence.get('contact_person_name', 'N/A')}

**Location:** {intelligence.get('location', 'N/A')}

**Address:** {intelligence.get('address', 'N/A')}

**Founder/CEO/MD:** {intelligence.get('founder_ceo_md', 'N/A')}

**Company Revenue:** {intelligence.get('company_revenue', 'N/A')}

**Market Response:** {intelligence.get('market_response', 'N/A')}

**Leadership Team:** {intelligence.get('leadership_team', 'N/A')}

**Vision:** {intelligence.get('vision', 'N/A')}

**Mission:** {intelligence.get('mission', 'N/A')}

**Top 5 or Major Challenges:**"""
        
        challenges = intelligence.get('top_5_challenges', [])
        for i, challenge in enumerate(challenges, 1):
            formatted_response += f"\n{i}. {challenge}"
        
        formatted_response += f"\n\n**Business Problem and its Business Impact:** {intelligence.get('business_problem_impact', 'N/A')}"
        
        return formatted_response
