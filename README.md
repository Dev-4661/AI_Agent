# Lead Generation Chatbot

A Streamlit-based chatbot application for lead generation that can analyze company information and process documents (PDFs and images) using OCR technology.

## Features

- **Company Information Search**: Get detailed information about any company
- **Document Analysis**: Upload and analyze PDF documents and images
- **OCR Technology**: Extract text from images using Tesseract OCR
- **Rate Limiting**: Built-in rate limiting (3 searches per minute)
- **Interactive Chat Interface**: User-friendly Streamlit interface

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR (for image processing)

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd copy
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR:
   - **Windows**: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Ubuntu**: `sudo apt install tesseract-ocr`

5. Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### Running the Application

```bash
streamlit run streamlit_app.py
```

## Project Structure

```
copy/
├── src/
│   └── chatbot.py          # Main chatbot logic
├── templates/
│   └── prompts.py          # AI prompt templates
├── streamlit_app.py        # Streamlit frontend
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Usage

1. **Company Search**: Type any company name to get detailed information
2. **Document Upload**: Upload PDF or image files for analysis
3. **Chat Interface**: Ask follow-up questions about companies or documents

## API Keys Required

- **Google API Key**: For Gemini AI model
- **Tavily API Key**: For real-time search capabilities

## Rate Limits

- 3 searches per minute (includes both chat queries and file uploads)
- Greetings and simple responses don't count toward the limit

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.