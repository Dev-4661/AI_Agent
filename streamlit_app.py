import streamlit as st
import sys
import os
import PyPDF2

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


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("<h1 class='main-header'>🏢 Lead Generation</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        
        # File Upload Section
        st.markdown("### 📁 Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload a PDF or Image file",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None and (not hasattr(st.session_state, 'last_uploaded_file') or 
                                      st.session_state.last_uploaded_file != uploaded_file.name):
            
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
                            summary = st.session_state.chatbot._process_file_content(
                                f"Document content from {uploaded_file.name}:\n\n{file_content}",
                                "Please provide a detailed summary of this document."
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
                                # Use Tesseract to extract text
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
                                    # Use the detailed analysis prompt for text extraction
                                    analysis = st.session_state.chatbot._process_file_content(
                                        file_content,
                                        analysis_prompt
                                    )
                                else:
                                    # Use the no text detected prompt
                                    analysis = NO_TEXT_DETECTED_PROMPT
                                
                                # Add to chat history
                                st.session_state.messages.extend([
                                    {"role": "user", "content": f"Please analyze this image: {uploaded_file.name}"},
                                    {"role": "assistant", "content": f"Here's an analysis of the uploaded image '{uploaded_file.name}':\n\n{analysis}"}
                                ])
                                
                                # Rerun to update the UI
                                st.rerun()
                                
                            except Exception as ocr_error:
                                st.sidebar.error(f"❌ OCR extraction failed: {str(ocr_error)}")
                                
                                # Check if it's a Tesseract path issue
                                if "tesseract is not installed" in str(ocr_error).lower() or "failed to execute tesseract" in str(ocr_error).lower():
                                    error_msg = """
                                    OCR failed. Please ensure Tesseract is properly installed:
                                    
                                    1. **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
                                    2. **Add to PATH**: Make sure tesseract.exe is in your system PATH
                                    3. **Alternative**: Set tesseract path manually:
                                       ```python
                                       pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
                                       ```
                                    
                                    Error details: {str(ocr_error)}
                                    """
                                else:
                                    error_msg = f"Failed to extract text from image: {str(ocr_error)}"
                                
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": error_msg
                                })
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
    
    # Handle file upload and display extracted content
  

            

    # Chat input
    if prompt := st.chat_input("Ask me about any company..."):
        # Add user message to chat history
        user_message = prompt
        
        # Include file content if available
        if 'file_content' in st.session_state:
            user_message = f"{st.session_state.file_content}\n\nUser question: {prompt}"
            # Clear file content after first use to avoid repeating
            del st.session_state.file_content
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing your request..."):
                try:
                    response = st.session_state.chatbot.chat(user_message)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
