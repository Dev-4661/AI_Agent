from langchain.prompts import PromptTemplate

"""
Prompt templates for various AI tasks
"""

# Company information search and response template
COMPANY_INFO_TEMPLATE = """
You are a helpful AI assistant specialized in providing accurate company information. 
You have been provided with search results about a company from reliable sources.

Context from search results:
{search_results}

User Question: {question}

Instructions:
1. Analyze the provided search results carefully
2. Extract relevant information that directly answers the user's question
3. Provide a comprehensive but concise response
4. If the search results don't contain enough information to answer the question, clearly state what information is missing
5. Always cite or reference the sources when providing specific details
6. Maintain a professional and informative tone

Response:
"""

# Follow-up question template
FOLLOWUP_TEMPLATE = """
Based on the previous conversation about {company_name}, here is additional information:

Previous Context:
{previous_context}

New Search Results:
{search_results}

User Question: {question}

Please provide a comprehensive answer incorporating both the previous context and new information:
"""

# Company search query optimization template
SEARCH_QUERY_TEMPLATE = """
Convert the following user question about a company into an optimized search query that will help find the most relevant information:

User Question: {question}

Create a focused search query (maximum 10 words) that will help find the most relevant company information:
"""

# Image analysis and summarization prompt
IMAGE_ANALYSIS_PROMPT = """
You are an expert document analyst specializing in extracting and summarizing information from business documents, brochures, and company materials.

The user has uploaded an image that has been processed through OCR (Optical Character Recognition). Your task is to:

1. **Analyze the extracted text** to understand the document type and content
2. **Identify key information** such as:
   - Company name and branding
   - Products or services offered
   - Contact information
   - Key features or benefits
   - Target audience or market
   - Any unique selling propositions
   - Technical specifications (if applicable)
   - Pricing information (if mentioned)

3. **Provide a comprehensive summary** that includes:
   - Document overview (what type of document it is)
   - Main company/product information
   - Key highlights and important details
   - Any actionable insights for lead generation

4. **Format your response** in a clear, structured manner with:
   - Clear headings and bullet points
   - Emphasis on business-relevant information
   - Professional tone suitable for business analysis

If the extracted text appears to be incomplete, corrupted, or unclear due to OCR limitations, mention this and work with whatever information is available.

If no meaningful text was extracted, provide guidance on potential reasons (image quality, text size, image format, etc.) and suggest improvements.

Please analyze the following extracted text and provide your detailed summary:
"""

# Prompt for when no text is detected in image
NO_TEXT_DETECTED_PROMPT = """
The image you uploaded appears to contain no readable text that could be extracted through OCR (Optical Character Recognition).

This could be due to several reasons:
- **Image Quality**: The image might be too blurry, low resolution, or have poor contrast
- **Text Size**: The text in the image might be too small to be accurately recognized
- **Image Format**: Some image formats or compression levels can affect OCR accuracy
- **Content Type**: The image might contain only graphics, logos, or diagrams without text
- **Language**: The text might be in a language not supported by the OCR engine
- **Handwriting**: OCR typically works best with printed text, not handwritten content

**Suggestions to improve OCR results:**
1. Ensure the image is high resolution and clear
2. Make sure there's good contrast between text and background
3. Try uploading the image in PNG or JPEG format
4. If possible, scan or photograph documents at 300 DPI or higher
5. Ensure the text is clearly visible and not too small

If you believe this image should contain readable text, please try uploading a clearer version or a different format of the same document.
"""

# PDF analysis prompt
PDF_ANALYSIS_PROMPT = """
You are an expert business document analyst. The user has uploaded a PDF document that needs to be analyzed for lead generation purposes.

Please analyze the provided document content and extract key business information including:

1. **Company Information**:
   - Company name and description
   - Business model and industry
   - Products or services offered
   - Target market and customer base

2. **Contact and Location Details**:
   - Contact information (address, phone, email, website)
   - Geographic presence or service areas
   - Office locations or branches

3. **Business Insights**:
   - Company size and scale indicators
   - Key partnerships or clients mentioned
   - Technology stack or tools used
   - Competitive advantages or unique selling points

4. **Lead Generation Opportunities**:
   - Potential business needs or pain points
   - Decision makers or key personnel mentioned
   - Budget indicators or financial information
   - Upcoming projects or expansion plans

5. **Summary and Recommendations**:
   - Overall company profile summary
   - Lead qualification insights
   - Recommended approach for outreach
   - Key talking points for sales conversations

Please provide a comprehensive analysis in a structured format with clear headings and actionable insights.
"""

def get_company_info_prompt():
    """Get the main company information prompt template"""
    return PromptTemplate(
        input_variables=["search_results", "question"],
        template=COMPANY_INFO_TEMPLATE
    )

def get_followup_prompt():
    """Get the follow-up question prompt template"""
    return PromptTemplate(
        input_variables=["company_name", "previous_context", "search_results", "question"],
        template=FOLLOWUP_TEMPLATE
    )

def get_search_query_prompt():
    """Get the search query optimization prompt template"""
    return PromptTemplate(
        input_variables=["question"],
        template=SEARCH_QUERY_TEMPLATE
    )
