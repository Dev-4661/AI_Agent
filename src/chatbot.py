import re

def extract_business_card_info(ocr_text: str) -> dict:
    """
    Improved: Extracts structured business card/company info from OCR text using line-by-line and context-aware parsing.
    Returns a dict with keys: name, title, email, phone, organization, address, website.
    """
    lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]
    name, title, email, phone, org, address, website = None, None, None, None, None, None, None
    # Try to find email, phone, website, org, address by context
    for line in lines:
        # Email
        if not email and ('@' in line or 'mail' in line.lower()):
            match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', line)
            if match:
                email = match.group(0)
        # Phone
        if not phone and (('phone' in line.lower()) or re.search(r'\+?\d{10,}', line)):
            match = re.search(r'(\+\d{1,3}[\s-]?)?\d{10,12}', line.replace(' ', ''))
            if match:
                phone = match.group(0)
        # Website
        if not website and ('.com' in line or '.org' in line or 'www' in line):
            match = re.search(r'(https?://[\w\.-]+|www\.[\w\.-]+)', line)
            if match:
                website = match.group(0)
        # Organization
        if not org and re.search(r'(Foundation|Ltd|Pvt|Inc|LLP|Corporation|Knowledge|Trust|Society|Company|Group|Enterprises|Industries|Systems|Solutions|Consultancy|Association|Organization)', line, re.IGNORECASE):
            org = line
        # Address
        if not address and (re.search(r'(Road|Street|St|Avenue|Ave|Building|Buildings|Block|Sector|Colony|Nagar|Egmore|Chennai|Tamilnadu|India|\d{6,})', line, re.IGNORECASE) or re.search(r'\d{6,}', line)):
            address = line
    # Name and title: usually first lines, or lines with capitalized words
    for i, line in enumerate(lines):
        if not name and re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', line):
            name = line
            # Try next line for title
            if i+1 < len(lines):
                tline = lines[i+1]
                if re.search(r'(President|Vice President|Director|Manager|Founder|CEO|CTO|CFO|COO|Head|Lead|Engineer|Consultant|Adviser|Advisor|Officer|Principal|Partner|Owner|Chairman|Board Member|Institutional Engagement)', tline, re.IGNORECASE):
                    title = tline
        elif not title and re.search(r'(President|Vice President|Director|Manager|Founder|CEO|CTO|CFO|COO|Head|Lead|Engineer|Consultant|Adviser|Advisor|Officer|Principal|Partner|Owner|Chairman|Board Member|Institutional Engagement)', line, re.IGNORECASE):
            title = line
    # Fallback: org from website
    if not org and website:
        org = website.split('//')[-1].split('.')[0].capitalize() + ' (from website)'
    # Fallback: address from last lines
    if not address and len(lines) > 2:
        for l in lines[-3:]:
            if re.search(r'(Road|Street|St|Avenue|Ave|Building|Buildings|Block|Sector|Colony|Nagar|Egmore|Chennai|Tamilnadu|India|\d{6,})', l, re.IGNORECASE):
                address = l
                break
    return {
        'name': name,
        'title': title,
        'email': email,
        'phone': phone,
        'organization': org,
        'address': address,
        'website': website
    }
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

    def filter_blocks_by_company(self, blocks, expected_company):
        """
        Filter blocks to prioritize those containing the expected company name (case-insensitive).
        If none match, fallback to all blocks.
        """
        expected_company_lower = expected_company.lower()
        filtered = [block for block in blocks if expected_company_lower in block.lower()]
        return filtered if filtered else blocks

    def get_company_information(self, user_question: str) -> str:
        """
        Get company information based on user question
        """
        try:
            # Check if this is just a greeting/casual message
            if self._is_greeting_or_casual(user_question):
                return self._handle_greeting(user_question)

            # Rate limiting check - only for actual company searches
            if not self._check_rate_limit():
                return "🚫 Oops! Only 3 searches per minute allowed. Please Try After 1 Minute."

            # Directly use the user's original query for search
            search_query = user_question.strip()
            print(f"🔍 Searching for: {search_query}")

            # Step 2: Search for company information
            search_results = self.search_tool.search_and_format(search_query)

            if not search_results or search_results == "No search results found.":
                return "I'm sorry, I couldn't find any information about that company. Please check the company name and try again."

            import re
            blocks = re.split(r'\n\n|###|\d+\. |\d+\)', str(search_results))
            company_names = self.extract_company_names(user_question)

            # Improved: Detect generic/multi-company queries by keywords or lack of company name
            generic_keywords = [
                'companies', 'list', 'bankrupt', 'collapse', 'scandal', 'filed for bankruptcy',
                'top', 'leading', 'major', 'biggest', 'largest', 'well-known', 'examples', 'cases', 'brands', 'industries', 'organizations', 'corporate', 'recent', '2024', '2025', '2023'
            ]
            user_question_lower = user_question.lower()
            is_generic_query = any(kw in user_question_lower for kw in generic_keywords)

            # If no real company name detected, or generic query, treat as multi-company/industry query
            is_multi_company = False
            if is_generic_query or not company_names or (len(company_names) == 1 and (company_names[0].strip().lower() == user_question.strip().lower() or len(company_names[0].strip().split()) < 2)):
                is_multi_company = True

            # Ensure filtered_blocks and structured_list are defined
            filtered_blocks = [search_results] if isinstance(search_results, str) else []
            structured_list = []
            for block in filtered_blocks:
                block = block.strip()
                if not block:
                    continue
                name_match = re.search(r'([A-Z][A-Za-z0-9 .,&\-]+(?:Technologies|Consultancy|Solutions|IT|Services|Limited|Ltd|Corporation|Systems|Mahindra|Capgemini|Hexaware|Cognisant|Wipro|Infosys|Tata|HCL|LTIMindtree|EClerx|Deloitte|EY|IBM|Accenture|Oracle|SAP|Microsoft|Google|Amazon|LinkedIn|IBall|63 Moons|ICICI|IDBI|IDFC|MakeMyTrip|Marico|Mahindra Group)[A-Za-z0-9 .,&\-]*)', block)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    fallback_name = re.search(r'([A-Z][A-Za-z0-9 .,&\-]{2,})', block)
                    name = fallback_name.group(1).strip() if fallback_name else None

                phone_match = re.search(r'(\+?\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}', block)
                phone = phone_match.group(0) if phone_match else None
                email_match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', block)
                email = email_match.group(0) if email_match else None
                ceo_match = re.search(r'(CEO|Chief Executive Officer|Founder|Managing Director|MD)[:\-]?\s*([A-Z][A-Za-z .,&\-]+)', block)
                ceo = ceo_match.group(2).strip() if ceo_match and ceo_match.group(2) else None

                leadership_match = re.findall(r'(?:Leadership Team|Team|Executives|Management|Board|Members|Director|Officer|Manager|Principal|Adviser|Engineer|General Manager|COO|CFO|CMO|CTO|President|Head|Founder|Chief|Senior|Executive|Officer|Director|Adviser|Manager|Reed|Willett|Cordie|Leather|Jesuadian|Reeves|Stewart|RootStatix)[^\n]*', block)
                leadership_team = [l for l in leadership_match if l.strip()] if leadership_match else []
                address_match = re.search(r'(Address|Headquarters|Location)[:\-]?\s*([A-Za-z0-9 .,&\-]+)', block)
                address = address_match.group(2).strip() if address_match else None
                location_match = re.search(r'(Mumbai|Navi Mumbai|India|Ahmedabad|Gurugram|Bengaluru|Chennai|New Jersey|New York)', block)
                location = location_match.group(1) if location_match else None
                issue_match = re.search(r'(technological issues|regular operations|financial issue|crisis|liabilities|bankrupt|debt|loss|fall|distressed|restructuring|costs|drop|cut|negative outlook)', block, re.IGNORECASE)
                issue = issue_match.group(1) if issue_match else None
                services_match = re.search(r'(services|offer|provides|products|solutions|business|consulting|software|BPO|IT/BPO|outsourcing|cloud|digital|finance|accounting|supply chain|management|technology|platform|industry|vertical|client|project|portfolio|capabilities|expertise|specialises|focuses|acquires|oversees|assets|distressed|NPA|ARC|recovery|interest|fees|performance|financials|recent news|developments|model|profile|leadership|executives|CEO|employees|workers|headcount|founded|established|year|location|office|headquarters|subsidiary|parent|group|division|unit|brand|company|firm|enterprise|corporation|limited|ltd|plc|llc|pvt|inc|holdings|industries|enterprises|solutions|systems|technologies|consultancy|services|group|business|profile|overview|about|info|information|details|show|list|find|search|for|about|the|please|provide|can you|could you|give|details|overview|business|profile|ceo|leadership|financials|performance|recent|news|developments|model|products|services|do|does|are|in|of|with|and|or|plus)', block, re.IGNORECASE)
                services = services_match.group(1) if services_match else None

                # Try to extract a summary/description (first long sentence or paragraph)
                summary = None
                summary_match = re.search(r'([A-Z][^\.\n]{30,}\.)', block)
                if summary_match:
                    summary = summary_match.group(1).strip()

                # Build structured line only with found fields
                line_parts = []
                if name:
                    line_parts.append(f"{name}")
                if location:
                    line_parts.append(f"Location: {location}")
                if address:
                    line_parts.append(f"Address: {address}")
                if phone:
                    line_parts.append(f"Phone: {phone}")
                if email:
                    line_parts.append(f"Email: {email}")
                if ceo:
                    line_parts.append(f"CEO/MD/Founder: {ceo}")
                if leadership_team:
                    line_parts.append(f"Leadership Team: {', '.join(leadership_team)}")
                if issue:
                    line_parts.append(f"Issue: {issue}")
                if services:
                    line_parts.append(f"Services/Details: {services}")
                if summary:
                    line_parts.append(f"Summary: {summary}")

                # If nothing found, just show the name or fallback
                if not line_parts:
                    if name:
                        line = f"• {name}"
                    else:
                        line = "• No structured information found."
                else:
                    line = "• " + " | ".join(line_parts)
                structured_list.append(line)
            if structured_list:
                ai_response = "Here is the structured information you requested:\n\n" + "\n".join(structured_list)
            else:
                ai_response = f"Here is the structured information you requested:\n\n{search_results}"
                if structured_list:
                    ai_response = "Here is the structured information you requested:\n\n" + "\n".join(structured_list)
                else:
                    ai_response = f"Here is the structured information you requested:\n\n{search_results}"
            # Step 4: Store in conversation history
            self.conversation_history.append({
                "question": user_question,
                "action_input": search_query,
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
            # Validate: Only keep names that look like real companies (letters, numbers, dots, ampersands, Inc, Ltd, Pvt, Corp, etc.)
            if name and len(name) > 1 and re.match(r'^[A-Za-z0-9 .&\-]+(Inc|Ltd|Pvt|Corp|LLC|PLC|Group|Technologies|Systems|Solutions|Consultancy|Enterprises|Industries|Holdings|Limited)?$', name, re.IGNORECASE):

💡 **Tips:**
• Be specific about the company name
• You can ask about financials, leadership, products, services, and more
• I use real-time search to get the latest information

Just ask me anything about a company and I'll help you find the information!
        """
    
    def search_web(self, query):
        """Search the web using Tavily API with fallback to Google-only search"""
        try:
            # Try Tavily search first
            search_results = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                include_answer=False,
                include_images=False,
                include_raw_content=False,
                max_results=5
            )
            return search_results.get('results', [])
        
        except Exception as tavily_error:
            print(f"Tavily search failed: {str(tavily_error)}")
            
            # Fallback: Return a message indicating search limitation
            return [{
                'title': 'Search Service Temporarily Unavailable',
                'content': f'I encountered an issue with the web search service while looking for information about "{query}". Please try again later or contact support if this issue persists.',
                'url': '#'
            }]
