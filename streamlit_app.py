import streamlit as st
import sys
import os
import PyPDF2
import time
import re
import urllib.parse

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables.")

from utils.email_generator import generate_insights_email, extract_email_from_analysis, extract_key_issues_from_analysis

# Try importing OCR and PDF libraries, handle missing modules gracefully
try:
    from PIL import Image
    import pytesseract
    PIL_AVAILABLE = True
    TESSERACT_AVAILABLE = True
    print("PIL and pytesseract imported successfully")
except ImportError as e:
    print(f"OCR import error: {e}")
    pytesseract = None
    Image = None

try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None

# Configure Tesseract path if needed (Windows specific)
if pytesseract is not None:
    import platform
    if platform.system() == "Windows":
        # Common Tesseract installation paths on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            r'C:\Tesseract-OCR\tesseract.exe',
            # Add path from environment variable if set
            os.path.join(os.environ.get('TESSERACT_PATH', ''), 'tesseract.exe') if os.environ.get('TESSERACT_PATH') else None
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import agent-based system
try:
    from config.agent_config import BusinessIntelligenceService, ApplicationIntegration
    AGENT_SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback to old system if agent system is not available
    from src.chatbot import CompanyChatbot
    AGENT_SYSTEM_AVAILABLE = False

from templates.prompts import IMAGE_ANALYSIS_AGENT_PROMPT, NO_TEXT_DETECTED_PROMPT, PDF_ANALYSIS_PROMPT

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
    """Initialize the enhanced agent-based system or fallback to old chatbot"""
    if 'business_service' not in st.session_state:
        try:
            if AGENT_SYSTEM_AVAILABLE:
                # Initialize new agent-based system
                business_service = BusinessIntelligenceService()
                
                # Check if agent system actually initialized properly
                if hasattr(business_service, 'initialized') and business_service.initialized:
                    st.session_state.business_service = business_service
                    st.session_state.app_integration = ApplicationIntegration()
                    st.session_state.system_type = "agent"
                    st.session_state.initialized = True
                else:
                    # Agent system failed to initialize, fallback to legacy
                    st.session_state.chatbot = CompanyChatbot()
                    st.session_state.system_type = "legacy"
                    st.session_state.initialized = True
            else:
                # Fallback to old system
                st.session_state.chatbot = CompanyChatbot()
                st.session_state.system_type = "legacy"
                st.session_state.initialized = True
        except Exception as e:
            # Try legacy system as final fallback
            try:
                st.session_state.chatbot = CompanyChatbot()
                st.session_state.system_type = "legacy"
                st.session_state.initialized = True
            except Exception as legacy_error:
                st.session_state.initialized = False
                st.session_state.error = f"Agent system: {str(e)}, Legacy system: {str(legacy_error)}"
                st.session_state.system_type = "error"
    
    return st.session_state.get('initialized', False)

def is_greeting_message(message):
    """Check if the message is just a greeting and doesn't require API calls"""
    msg_lower = message.lower().strip()
    
    # If message contains words like "company", "tell me", "what", "find", etc., it's NOT a greeting
    search_indicators = ['company', 'tell me', 'what', 'find', 'search', 'about', 'information', 'details', 'tcs', 'l&t', 'infosys', 'wipro', 'microsoft', 'google', 'apple', 'amazon']
    if any(indicator in msg_lower for indicator in search_indicators):
        return False
    
    # Only very basic greetings - be more restrictive
    exact_greetings = [
        'hi', 'hello', 'hey', 'hii', 'hiii',
        'good morning', 'good afternoon', 'good evening',
        'how are you', 'thank you', 'thanks', 'ok', 'okay', 
        'bye', 'goodbye', 'yes', 'no'
    ]
    
    # Only match exact greetings
    if msg_lower in exact_greetings:
        return True
    
    # Only match if it's exactly these greeting patterns
    greeting_patterns = [
        r'^hi+$', r'^hello+$', r'^hey+$',
        r'^thanks?$', r'^ok(ay)?$'
    ]
    
    for pattern in greeting_patterns:
        if re.match(pattern, msg_lower):
            return True
    
    # Don't use length-based detection as it catches company abbreviations
    return False

def check_rate_limit():
    """Check if user has exceeded rate limit (3 searches per minute)"""
    current_time = time.time()
    
    # Initialize rate limit tracking
    if 'search_timestamps' not in st.session_state:
        st.session_state.search_timestamps = []
    
    # Remove timestamps older than 1 minute
    st.session_state.search_timestamps = [
        timestamp for timestamp in st.session_state.search_timestamps 
        if current_time - timestamp < 60
    ]
    
    # Check if user has reached limit
    if len(st.session_state.search_timestamps) >= 3:
        return False, st.session_state.search_timestamps[0] + 60 - current_time
    
    return True, 0

def add_search_timestamp():
    """Add current timestamp to search history"""
    if 'search_timestamps' not in st.session_state:
        st.session_state.search_timestamps = []
    
    st.session_state.search_timestamps.append(time.time())

def handle_greeting(message):
    """Generate appropriate response for greetings without using APIs"""
    return "Hi there! 👋 I'm here to help you find information about companies. What company would you like to know about?"

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("<h1 class='main-header'>🏢 Lead Generation</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        
        # Rate limit display
        current_time = time.time()
        if 'search_timestamps' in st.session_state:
            recent_searches = [
                timestamp for timestamp in st.session_state.search_timestamps 
                if current_time - timestamp < 60
            ]
            searches_remaining = 3 - len(recent_searches)
            
            if searches_remaining > 0:
                st.markdown(f"### 🔍 Searches Remaining: {searches_remaining}/3")
            else:
                wait_time = int(st.session_state.search_timestamps[0] + 60 - current_time)
                st.markdown(f"### ⏰ Rate Limited: Wait {wait_time}s")
        else:
            st.markdown("### 🔍 Searches Remaining: 3/3")
        
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    
    # File Upload Section
        st.markdown("### 📁 Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload a PDF or Image file",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            label_visibility="collapsed"  
        )
        st.markdown("### 📋 Example Questions")
        st.markdown("""
        - Tell me about Apple Inc.
        - Who is the CEO of Microsoft?
        - What does Tesla do?
        - Google's recent financial results
        - Amazon's business model
        """)
        
        st.markdown("### ⚙️ Configuration")
        
        # Configuration section
        col1, col2 = st.columns(2)
        
        # System status indicator with more detailed information
        if st.session_state.get('system_type') == "agent":
            st.success("🤖 **Enhanced AI Agent System** - Active")
            st.caption("✅ Structured 14-point analysis")
            st.caption("✅ Gemini AI powered")
            if os.getenv("TAVILY_API_KEY"):
                st.caption("✅ Real-time search capabilities")
            else:
                st.caption("⚠️  Basic mode (no Tavily search)")
            st.caption("✅ Intelligent decision making")
        elif st.session_state.get('system_type') == "legacy":
            st.warning("⚡ **Legacy System** - Active")
            st.caption("✅ Gemini AI powered")
            st.caption("✅ Basic company information search")
        elif st.session_state.get('system_type') == "error":
            st.error("❌ **System Error** - Check configuration")
            if 'error' in st.session_state:
                with st.expander("Error Details"):
                    st.text(str(st.session_state.error))
            st.caption("💡 Check your GOOGLE_API_KEY in .env file")
        else:
            st.info("🔄 **System Loading** - Please wait")
            
        with col2:
            if st.button("Clear Chat History"):
                welcome_msg = """
                👋 Welcome! I'm your Enhanced Business Intelligence Assistant. 
                
                I can provide comprehensive company analysis including:
                • Company Name & Contact Information
                • Leadership Team & Founder Details
                • Financial Performance & Revenue Data
                • Market Position & Competitive Analysis
                • Vision, Mission & Strategic Direction
                • Top 5 Business Challenges & Impact Analysis
                
                Ask me about any company for detailed intelligence!
                """
                st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
                if 'chatbot' in st.session_state:
                    st.session_state.chatbot.clear_conversation_history()
                if 'business_service' in st.session_state:
                    # Clear any cached data in the agent system
                    pass
                st.success("Chat history cleared!")
        
        # Handle file upload processing
        if uploaded_file is not None and (not hasattr(st.session_state, 'last_uploaded_file') or 
                                      st.session_state.last_uploaded_file != uploaded_file.name):
            
            # Check rate limit before processing file
            can_search, wait_time = check_rate_limit()
            
            if not can_search:
                st.sidebar.error(f"🚫 Rate limit exceeded! Please wait {int(wait_time)} seconds before uploading files.")
            else:
                # Add timestamp for this file processing (counts as a search)
                add_search_timestamp()
                
                # Store the current file name to prevent reprocessing
                st.session_state.last_uploaded_file = uploaded_file.name
                file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
                
                try:
                    if file_details["FileType"] == 'application/pdf':
                        # PDF processing
                        try:
                            pdf_reader = PyPDF2.PdfReader(uploaded_file) 
                            text = []
                            for page in pdf_reader.pages:
                                try:
                                    page_text = page.extract_text()
                                    if page_text and page_text.strip():
                                        text.append(page_text.strip())
                                except Exception as e:
                                    print(f"Error extracting text from page: {str(e)}")
                            
                            if not text:
                                raise ValueError("Could not extract any text from the PDF.")
                                
                            file_content = "\n\n".join(text)
                            st.sidebar.success("✅ PDF processed! Check the chat for analysis.")
                            
                            with st.spinner("🔍 Analyzing PDF document..."):
                                # Check system type and use appropriate analysis
                                if st.session_state.get('system_type') == "agent" and 'app_integration' in st.session_state:
                                    # Use new agent-based system for PDF analysis
                                    summary = st.session_state.app_integration.handle_image_analysis(file_content)
                                elif st.session_state.get('initialized', False) and 'chatbot' in st.session_state and st.session_state.chatbot is not None:
                                    # Use legacy system
                                    summary = st.session_state.chatbot.chat(
                                        f"{PDF_ANALYSIS_PROMPT}\n\nDocument content from {uploaded_file.name}:\n\n{file_content}"
                                    )
                                else:
                                    # Fallback when neither system is available
                                    summary = f"I've successfully extracted text from '{uploaded_file.name}' but detailed analysis is temporarily unavailable. The document contains {len(file_content.split())} words. Please try again later for full AI analysis."
                                
                                st.session_state.messages.extend([
                                    {"role": "user", "content": f"Please analyze this PDF: {uploaded_file.name}"},
                                    {"role": "assistant", "content": f"Here's an analysis of '{uploaded_file.name}':\n\n{summary}"}
                                ])
                                
                                if summary and len(summary) > 100:
                                    st.session_state.last_analysis = {
                                        'company_name': uploaded_file.name.replace('.pdf', '').replace('_', ' ').title(),
                                        'analysis_text': summary,
                                        'analysis_type': 'pdf'
                                    }
                                
                                st.rerun()
                                
                        except Exception as e:
                            # Don't show backend errors to users
                            st.sidebar.info("📄 Unable to process this PDF. Please try a different file.")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "I'm having trouble processing this PDF file. Could you try uploading a different file?"
                            })
                            st.rerun()
                    
                    elif file_details["FileType"] in ['image/png', 'image/jpg', 'image/jpeg']:
                        # Image processing
                        try:
                            if pytesseract is None or Image is None:
                                st.sidebar.error("❌ OCR libraries not available. Please install: pip install pytesseract pillow")
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "I cannot process images because OCR libraries are not installed."
                                })
                                st.rerun()
                                return
                            
                            image = Image.open(uploaded_file)
                            
                            with st.spinner("🔍 Extracting text from image using OCR..."):
                                try:
                                    # Try multiple OCR configurations
                                    configs = [
                                        '--oem 3 --psm 6',
                                        '--oem 3 --psm 3',
                                        '--oem 3 --psm 4',
                                        '--oem 3 --psm 11',
                                        '--oem 3 --psm 12'
                                    ]
                                    
                                    all_text = []
                                    for config in configs:
                                        try:
                                            text = pytesseract.image_to_string(image, config=config, lang='eng')
                                            if text.strip():
                                                all_text.append(text.strip())
                                        except:
                                            continue
                                    
                                    if all_text:
                                        combined_text = '\n'.join(all_text)
                                        lines = combined_text.split('\n')
                                        unique_lines = []
                                        seen = set()
                                        for line in lines:
                                            line = line.strip()
                                            if line and line not in seen and len(line) > 2:
                                                unique_lines.append(line)
                                                seen.add(line)
                                        extracted_text = '\n'.join(unique_lines)
                                    else:
                                        extracted_text = pytesseract.image_to_string(image, lang='eng')
                                    
                                except Exception:
                                    extracted_text = pytesseract.image_to_string(image, lang='eng')
                            
                            if not extracted_text.strip():
                                st.sidebar.warning("⚠️ No text found in the image")
                                analysis = "I couldn't detect any readable text in this image. The image might contain graphics, logos, or text that's too small/unclear for OCR to process effectively."
                            else:
                                st.sidebar.success("✅ Image processed! Check the chat for analysis.")
                                # Check system type and use appropriate analysis
                                if st.session_state.get('system_type') == "agent" and 'app_integration' in st.session_state:
                                    # Use new agent-based system
                                    analysis = st.session_state.app_integration.handle_image_analysis(extracted_text.strip())
                                elif st.session_state.get('initialized', False) and 'chatbot' in st.session_state and st.session_state.chatbot is not None:
                                    # Use legacy system
                                    analysis = st.session_state.chatbot.chat(
                                        f"{IMAGE_ANALYSIS_AGENT_PROMPT}\n\nExtracted text from '{uploaded_file.name}':\n\n{extracted_text.strip()}"
                                    )
                                else:
                                    # Fallback when neither system is available
                                    analysis = f"I've successfully extracted text from '{uploaded_file.name}' but detailed analysis is temporarily unavailable. The extracted text contains {len(extracted_text.split())} words. Please try again later for full AI analysis."
                            
                            st.session_state.messages.extend([
                                {"role": "user", "content": f"Please analyze this image: {uploaded_file.name}"},
                                {"role": "assistant", "content": f"Here's an analysis of '{uploaded_file.name}':\n\n{analysis}"}
                            ])
                            
                            if analysis and len(analysis) > 100:
                                st.session_state.last_analysis = {
                                    'company_name': uploaded_file.name.replace('.jpg', '').replace('.png', '').replace('.jpeg', '').replace('_', ' ').title(),
                                    'analysis_text': analysis,
                                    'analysis_type': 'image'
                                }
                            
                            st.rerun()
                            
                        except Exception as e:
                            # Don't show backend errors to users
                            st.sidebar.info("📷 Unable to process this image. Please try a different image.")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"I'm having trouble processing the image '{uploaded_file.name}'. Could you try uploading a different image?"
                            })
                            st.rerun()
                            
                except Exception as general_error:
                    # Don't show backend errors to users
                    st.sidebar.info("📄 Unable to process this file. Please try a different file format.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"I'm having trouble processing the file '{uploaded_file.name}'. Please try uploading a different file."
                    })
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Initialize chatbot
    if not initialize_chatbot():
        # Just silently continue without chatbot - don't show errors to users
        pass
    
    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message for new agent system
        if st.session_state.get('system_type') == "agent":
            welcome_msg = """
            � **Enhanced Business Intelligence Assistant**

            I provide comprehensive 14-point company analysis including:
            
            📊 **Company Fundamentals:**
            • Company Name & Contact Information
            • Leadership Team & Founder Details
            • Complete Business Address & Location
            
            💰 **Financial Intelligence:**
            • Company Revenue & Market Position
            • Market Response & Industry Standing
            
            🎯 **Strategic Analysis:**
            • Vision & Mission Statements
            • Top 5 Business Challenges
            • Business Problems & Impact Analysis
            
            **How to use:** Simply ask about any company and I'll provide structured intelligence using advanced AI agents and real-time search!
            """
        else:
            welcome_msg = """
            �👋 Welcome! I'm your Company Information Assistant. 

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
    
    # Email button (only show if analysis is available and place it above chat input)
    if hasattr(st.session_state, 'last_analysis') and st.session_state.last_analysis:
        col1, col2, col3 = st.columns([6, 2, 2])
        with col2:
            if st.button("📧 Email Insights", key="email_btn", use_container_width=True):
                st.session_state.show_email_modal = True
                st.rerun()
    
    # Chat input (keep it normal without columns to maintain bottom position)
    prompt = st.chat_input("Enter your Prompt Here")

    # Handle chat input
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check if it's a greeting (doesn't count toward rate limit)
        is_greeting = is_greeting_message(prompt)
        
        # Debug info (remove this after testing)
        # st.write(f"Debug: Message '{prompt}' is_greeting: {is_greeting}")
        
        if is_greeting:
            with st.chat_message("assistant"):
                greeting_response = handle_greeting(prompt)
                st.markdown(greeting_response)
                st.session_state.messages.append({"role": "assistant", "content": greeting_response})
        else:
            # Check rate limit for actual searches
            can_search, wait_time = check_rate_limit()
            
            if not can_search:
                with st.chat_message("assistant"):
                    rate_limit_msg = f"🚫 Rate limit exceeded! You can make 3 searches per minute. Please wait {int(wait_time)} seconds before your next search."
                    st.markdown(rate_limit_msg)
                    st.session_state.messages.append({"role": "assistant", "content": rate_limit_msg})
            else:
                # Add timestamp for this search BEFORE making the call
                add_search_timestamp()
                
                # Include file content if available
                user_message = prompt
                if 'file_content' in st.session_state:
                    user_message = f"{st.session_state.file_content}\n\nUser question: {prompt}"
                    del st.session_state.file_content
                
                # Get bot response
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Analyzing your request..."):
                        try:
                            # Check system type and use appropriate response system
                            if st.session_state.get('system_type') == "agent" and 'app_integration' in st.session_state:
                                # Use new agent-based system
                                response = st.session_state.app_integration.handle_company_search(user_message)
                            elif 'chatbot' in st.session_state and st.session_state.chatbot is not None:
                                # Use legacy system
                                response = st.session_state.chatbot.chat(user_message)
                            else:
                                # Fallback response when neither system is available
                                response = "I'm currently experiencing some technical difficulties with the search service. Please try again in a few moments, or upload a document for analysis instead."
                            
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Check if this was a company search and store for email functionality
                            if not is_greeting and len(response) > 100:
                                # Try to extract company name from user prompt
                                company_name = extract_company_name_from_prompt(prompt)
                                if company_name:
                                    st.session_state.last_analysis = {
                                        'company_name': company_name,
                                        'analysis_text': response,
                                        'analysis_type': 'agent_search' if st.session_state.get('system_type') == "agent" else 'company_search'
                                    }
                                    st.rerun()
                        except Exception as e:
                            # Don't show backend errors to users
                            user_friendly_msg = "I'm having trouble processing your request right now. Please try again in a moment."
                            st.markdown(user_friendly_msg)
                            st.session_state.messages.append({"role": "assistant", "content": user_friendly_msg})

    # Email modal popup (show all email functions when clicked)
    if hasattr(st.session_state, 'show_email_modal') and st.session_state.show_email_modal:
        show_email_modal()

def show_email_modal():
    """Display all email functions in a prominent section"""
    
    # Email functions section (as shown in the image)
    with st.container():
        st.markdown("---")
        st.markdown("### 📧 Send Insights via Email")
        
        analysis_data = st.session_state.last_analysis
        
        # Company info display
        st.info(f"📊 **Analysis Ready:** {analysis_data['company_name']} ({analysis_data['analysis_type'].replace('_', ' ').title()})")
        
        # Email form in columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Extract email from analysis if available
            auto_email = extract_email_from_analysis(analysis_data['analysis_text'])
            recipient_email = st.text_input(
                "🎯 Recipient Email:", 
                value=auto_email or "",
                placeholder="Enter email address",
                key="main_email_input"
            )
            
            sender_name = st.text_input("👤 Your Name:", value="Business Analyst", key="sender_name")
            
        with col2:
            sender_company = st.text_input("🏢 Your Company:", value="Strategic Consulting Solutions", key="sender_company")
            sender_contact = st.text_input("📱 Your Contact:", value="+1-XXX-XXX-XXXX", key="sender_contact")
        
        # Email preview
        if recipient_email and '@' in recipient_email:
            key_issues = extract_key_issues_from_analysis(analysis_data['analysis_text'])
            
            with st.expander("📋 Email Preview"):
                st.markdown(f"**To:** {recipient_email}")
                st.markdown(f"**Subject:** Strategic Insights & Solutions for {analysis_data['company_name']}")
                st.markdown("**Key Issues Identified:**")
                for i, issue in enumerate(key_issues[:3], 1):
                    st.markdown(f"{i}. {issue}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("❌ Close", key="close_email_modal"):
                st.session_state.show_email_modal = False
                st.rerun()
        
        with col2:
            if st.button("📧 Send via Gmail", type="primary", key="send_gmail"):
                if recipient_email and '@' in recipient_email:
                    sender_config = {
                        'sender_name': sender_name,
                        'sender_company': sender_company,
                        'sender_contact': sender_contact
                    }
                    generate_and_open_gmail(analysis_data, recipient_email, sender_config)
                else:
                    st.error("❌ Please enter a valid email address")

def generate_and_open_gmail(analysis_data, recipient_email, sender_config):
    """Generate Gmail URL and open it"""
    key_issues = extract_key_issues_from_analysis(analysis_data['analysis_text'])
    subject = f"Strategic Insights & Solutions for {analysis_data['company_name']}"
    
    body = f"""Dear Team,

I recently conducted a comprehensive analysis of {analysis_data['company_name']} using AI-powered business intelligence tools.

KEY INSIGHTS IDENTIFIED:
"""
    
    for i, issue in enumerate(key_issues[:3], 1):
        body += f"{i}. {issue}\n"
    
    body += f"""
PROPOSED SOLUTIONS:
• Customized solutions addressing specific challenges
• Implementation roadmap with measurable outcomes
• Best practices from industry leaders

I believe there's tremendous potential to enhance {analysis_data['company_name']}'s operational efficiency. Would you be available for a consultation call?

Best regards,
{sender_config['sender_name']}
{sender_config['sender_company']}
Contact: {sender_config['sender_contact']}
"""
    
    # Create Gmail compose URL
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient_email}&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    # Display success message and clickable link
    st.success("✅ Gmail compose link generated!")
    
    # Create clickable link that definitely opens in new tab
    st.markdown(
        f"""
        <a href="{gmail_url}" target="_blank" rel="noopener noreferrer">
            <button style="background: linear-gradient(135deg, #EA4335, #4285F4); 
                          color: white; padding: 12px 24px; border: none; 
                          border-radius: 8px; cursor: pointer; font-size: 16px; 
                          margin: 10px 0; font-weight: bold;">
                🚀 Click Here to Open Gmail
            </button>
        </a>
        """, 
        unsafe_allow_html=True
    )
    
    # Try JavaScript approach as backup
    st.components.v1.html(
        f"""
        <script>
            setTimeout(function() {{
                window.open("{gmail_url}", "_blank");
            }}, 1000);
        </script>
        <p>Gmail should open automatically in 1 second...</p>
        """,
        height=50
    )

def extract_company_name_from_prompt(prompt: str) -> str:
    """Extract company name from user prompt"""
    import re
    
    # Common patterns for company searches
    patterns = [
        r"(?:tell me about|about|analyze|search|find|information on|details about)\s+([A-ZaZ0-9\s&.,'-]+?)(?:\s|$|\?|\.)",
        r"^([A-ZaZ0-9\s&.,'-]+?)(?:\s+company|\s+inc|\s+corp|\s+ltd|$)",
        r"([A-ZaZ0-9\s&.,'-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            if len(company_name) > 2:
                return company_name.title()
    
    return "Company"

if __name__ == "__main__":
    main()