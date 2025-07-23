import streamlit as st
import sys
import os
import PyPDF2
import time
import re

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

# Configure Tesseract path if needed (Windows specific)
if pytesseract is not None:
    import platform
    if platform.system() == "Windows":
        # Common Tesseract installation paths on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import CompanyChatbot
from templates.prompts import IMAGE_ANALYSIS_PROMPT, NO_TEXT_DETECTED_PROMPT, PDF_ANALYSIS_PROMPT

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
        
        
        
        
        if uploaded_file is not None and (not hasattr(st.session_state, 'last_uploaded_file') or 
                                      st.session_state.last_uploaded_file != uploaded_file.name):
            
            # Check rate limit before processing file
            can_search, wait_time = check_rate_limit()
            
            if not can_search:
                st.sidebar.error(f"🚫 Rate limit exceeded! Please wait {int(wait_time)} seconds before uploading files.")
                return
            
            # Add timestamp for this file processing (counts as a search)
            add_search_timestamp()
            
            # Store the current file name to prevent reprocessing
            st.session_state.last_uploaded_file = uploaded_file.name
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            
            try:
                if file_details["FileType"] == 'application/pdf':
                    # Read PDF file with better error handling
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
                            raise ValueError("Could not extract any text from the PDF. The document might be scanned or encrypted.")
                            
                        # Store extracted text in session state
                        file_content = "\n\n".join(text)
                        st.session_state.file_content = file_content
                        
                        # Show a brief success message in the sidebar
                        st.sidebar.success("✅ PDF processed! Check the chat for the summary.")
                        
                        # Process the document in the chat
                        with st.spinner("🔍 Analyzing the document..."):
                            summary = st.session_state.chatbot.chat(
                                f"Document content from {uploaded_file.name}:\n\n{file_content}\n\nPlease provide a detailed summary of this document."
                            )
                            
                            # Add to chat history
                            st.session_state.messages.extend([
                                {"role": "user", "content": f"Please analyze this document: {uploaded_file.name}"},
                                {"role": "assistant", "content": f"Here's a summary of the uploaded document '{uploaded_file.name}':\n\n{summary}"}
                            ])
                            
                            # Rerun to update the UI
                            st.rerun()
                            
                    except Exception as e:
                        error_msg = f"Failed to process PDF: {str(e)}"
                        st.sidebar.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"I couldn't process the PDF '{uploaded_file.name}'. Error: {str(e)}"
                        })
                        st.rerun()
                
                elif file_details["FileType"] in ['image/png', 'image/jpg', 'image/jpeg']:
                    try:
                        if pytesseract is None or Image is None:
                            st.sidebar.error("❌ OCR libraries not available. Please install: pip install pytesseract pillow")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "I cannot process images because the required OCR libraries (pytesseract, PIL) are not installed. Please install them with: pip install pytesseract pillow"
                            })
                            st.rerun()
                            return
                        
                        # Load the image
                        image = Image.open(uploaded_file)
                        
                        # Extract text using OCR
                        with st.spinner("🔍 Extracting text from image using OCR..."):
                            try:
                                # Use multiple OCR configurations for better results without OpenCV
                                configs = [
                                    '--oem 3 --psm 6',  # Default
                                    '--oem 3 --psm 3',  # Fully automatic page segmentation
                                    '--oem 3 --psm 4',  # Single column text
                                    '--oem 3 --psm 11', # Sparse text
                                    '--oem 3 --psm 12'  # Single text line
                                ]
                                
                                all_text = []
                                for config in configs:
                                    try:
                                        text = pytesseract.image_to_string(image, config=config, lang='eng')
                                        if text.strip():
                                            all_text.append(text.strip())
                                    except:
                                        continue
                                
                                # Combine all extracted texts and remove duplicates
                                if all_text:
                                    # Join all texts and remove duplicate lines
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
                                    # Fallback to basic OCR
                                    extracted_text = pytesseract.image_to_string(image, lang='eng')
                                
                            except Exception as ocr_error:
                                # Fallback to basic OCR
                                extracted_text = pytesseract.image_to_string(image, lang='eng')
                        
                        if not extracted_text.strip():
                            st.sidebar.warning("⚠️ No text found in the image")
                            file_content = f"Image file: {uploaded_file.name} - No readable text detected"
                            analysis_prompt = NO_TEXT_DETECTED_PROMPT
                        else:
                            file_content = f"Text extracted from image '{uploaded_file.name}':\n\n{extracted_text.strip()}"
                            analysis_prompt = f"{IMAGE_ANALYSIS_PROMPT}\n\n{file_content}"
                        
                        st.session_state.file_content = file_content
                        
                        # Show success message in the sidebar
                        st.sidebar.success("✅ Image processed! Check the chat for the analysis.")
                        
                        # Process the extracted text in the chat
                        if extracted_text.strip():
                            # Use the updated IMAGE_ANALYSIS_PROMPT with the extracted text
                            analysis = st.session_state.chatbot.chat(
                                f"{IMAGE_ANALYSIS_PROMPT}\n\n{extracted_text.strip()}"
                            )
                        else:
                            # Use the no text detected prompt
                            analysis = "I couldn't detect any readable text in this image. The image might contain graphics, logos, or text that's too small/unclear for OCR to process effectively."
                        
                        # Add to chat history WITHOUT setting file_content in session_state
                        st.session_state.messages.extend([
                            {"role": "user", "content": f"Please analyze this image: {uploaded_file.name}"},
                            {"role": "assistant", "content": f"Here's an analysis of the uploaded image '{uploaded_file.name}':\n\n{analysis}"}
                        ])
                        
                        # Rerun to update the UI
                        st.rerun()
                        
                    except Exception as e:
                        st.sidebar.error(f"Failed to process image: {str(e)}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"I couldn't process the image '{uploaded_file.name}'. Error: {str(e)}"
                        })
                        st.rerun()
            except Exception as general_error:
                st.sidebar.error(f"Failed to process file: {str(general_error)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"I couldn't process the file '{uploaded_file.name}'. Error: {str(general_error)}"
                })
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

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
    
    # Chat input
    if prompt := st.chat_input("Ask me about any company..."):
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
                            response = st.session_state.chatbot.chat(user_message)
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                            st.markdown(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
