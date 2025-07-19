# 🏢 Lead Generation Chatbot

A Streamlit-based AI chatbot application for lead generation and company information analysis. Upload PDF documents or images, extract text using OCR, and get detailed company insights for sales and business development.

## ✨ Features

- **Document Analysis**: Upload and analyze PDF documents and images
- **OCR Text Extraction**: Extract text from images using Tesseract OCR
- **AI-Powered Insights**: Get detailed company information and lead generation insights
- **Interactive Chat Interface**: Natural conversation with the AI assistant
- **Real-time Processing**: Instant document processing and analysis

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** (for image text extraction)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd copy
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   - **Windows**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📁 Project Structure

```
copy/
├── streamlit_app.py          # Main Streamlit application
├── src/
│   └── chatbot.py           # Chatbot implementation
├── templates/
│   └── prompts.py           # AI prompt templates
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🚀 Usage

1. **Start the application**: Run `streamlit run streamlit_app.py`
2. **Upload documents**: Use the sidebar to upload PDF files or images (PNG, JPG, JPEG)
3. **Get insights**: The AI will automatically analyze uploaded documents
4. **Ask questions**: Chat with the AI about companies or uploaded documents
5. **Generate leads**: Get detailed company information for sales outreach

## 📋 Supported File Types

- **PDF Documents**: Automatic text extraction and analysis
- **Images**: PNG, JPG, JPEG with OCR text extraction
- **Content Types**: Company brochures, business documents, marketing materials

## 🔧 Configuration

### Tesseract OCR Setup
The application automatically detects Tesseract installation in common Windows paths:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Users\{USERNAME}\AppData\Local\Tesseract-OCR\tesseract.exe`

### API Keys Required
- **Google API Key**: For AI model access
- **Tavily API Key**: For web search capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**OCR not working?**
- Ensure Tesseract is properly installed and in your system PATH
- Check image quality and text clarity
- Verify pytesseract installation: `pip install pytesseract`

**API errors?**
- Verify your API keys in the `.env` file
- Check internet connection for API calls
- Ensure API quotas are not exceeded

**Streamlit issues?**
- Update Streamlit: `pip install --upgrade streamlit`
- Clear browser cache and reload the page
- Check console for detailed error messages

## 📞 Support

For issues or questions, please create an issue in the repository or contact the development team.