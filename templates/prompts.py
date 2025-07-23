from langchain.prompts import PromptTemplate

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
   - Key features or benefits
   - Target audience or market
   - Any unique selling propositions
   - Technical specifications (if applicable)
   - Pricing information (if mentioned)

3. **Extract all available information from the OCR text first**, including:
   - Phone numbers
   - Email addresses
   - Physical addresses
   - Website URLs
   - Social media handles
   - Company description
   - Services/products
   - Key personnel

4. **For missing critical information**: If key business information is not found in the extracted text, you may search the internet to find:
   - Missing contact details (phone, email, address, website)
   - Social media profiles
   - Company address and location
   - Additional company background information
   - Recent news or updates about the company

5. **Provide a comprehensive summary** that includes:
   - Document overview (what type of document it is)
   - Main company/product information
   - Key highlights and important details
   - Complete contact information (clearly marked as OCR vs. web search)
   - Missing information found through web search
   - Any actionable insights for lead generation

6. **Format your response** in a clear, structured manner with:
   - Clear headings and bullet points
   - Emphasis on business-relevant information
   - Professional tone suitable for business analysis
   - Clearly indicate which information came from OCR vs. internet search
   - Highlight any missing information that couldn't be found

**Search Priority for Missing Information:**
- Complete contact details (address, phone, email, website)
- Social media profiles (LinkedIn, Twitter, Instagram, YouTube)
- Company headquarters/office locations
- Recent company news or press releases
- Additional product/service information

Please analyze the following extracted text and provide your detailed summary:
"""

# Comprehensive company information gathering prompt
MISSING_INFO_SEARCH_PROMPT = """
You are a business intelligence assistant specialized in gathering comprehensive company information.

Based on the initial analysis, the following information has been identified:

**Available Information:**
{available_info}

**Missing Information to Search For:**
{missing_info}

Your task is to search the internet and find the missing information listed above. For each piece of missing information:

1. **Search systematically** for the company using available identifiers (name, website, email domain, etc.)
2. **Verify information accuracy** by cross-referencing multiple sources
3. **Prioritize official sources** such as:
   - Company's official website
   - LinkedIn company page
   - Business directories
   - News articles and press releases
   - Government business registrations

4. **Provide structured results** including:
   - The missing information found
   - Source of the information
   - Confidence level (High/Medium/Low)
   - Any additional relevant details discovered

5. **If information cannot be found**, clearly state what remains missing and suggest alternative search strategies.

Please conduct a thorough search and provide a comprehensive update on the missing information:
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

def get_missing_info_search_prompt():
    """Get the missing information search prompt template"""
    return PromptTemplate(
        input_variables=["available_info", "missing_info"],
        template=MISSING_INFO_SEARCH_PROMPT
    )

# Email template generation prompt
EMAIL_TEMPLATE_PROMPT = """
You are a professional sales email writer specializing in B2B outreach. Based on the company analysis provided, create a personalized and compelling email template.

**Company Analysis:**
{company_analysis}

**Key Insights Identified:**
{key_insights}

**Your Task:**
Create a professional email template that:

1. **Personalization**: 
   - Address the specific company and industry
   - Reference specific details from the analysis
   - Show genuine understanding of their business

2. **Key Insights Integration**:
   - Naturally weave in the identified pain points or opportunities
   - Demonstrate knowledge of their current situation
   - Reference their products/services or recent developments

3. **Proposed Solution**:
   - Present a solution that directly addresses the identified insights
   - Explain how your offering solves their specific challenges
   - Include relevant benefits and value propositions
   - Make the connection between their needs and your solution clear

4. **Professional Structure**:
   - Engaging subject line
   - Professional greeting
   - Brief introduction and credibility
   - Value-focused body with insights and solution
   - Clear call-to-action
   - Professional closing

5. **Tone and Style**:
   - Professional yet conversational
   - Consultative approach, not pushy
   - Focus on value delivery
   - Respectful of their time

**Email Template Requirements:**
- Subject line (compelling and relevant)
- Email body (200-300 words)
- Clear value proposition
- Specific call-to-action
- Professional signature placeholder

Please generate a complete email template based on the provided analysis:
"""

# Follow-up email template prompt
FOLLOWUP_EMAIL_PROMPT = """
You are creating a follow-up email based on previous outreach. Generate a professional follow-up email that:

**Previous Context:**
{previous_context}

**Additional Insights:**
{additional_insights}

**Follow-up Strategy:**
1. Reference the previous email professionally
2. Provide additional value or insights
3. Address potential objections or concerns
4. Include new relevant information
5. Maintain professional persistence without being pushy

Create a follow-up email template that adds value and maintains engagement:
"""


def get_email_template_prompt():
    """Get the email template generation prompt"""
    return PromptTemplate(
        input_variables=["company_analysis", "key_insights"],
        template=EMAIL_TEMPLATE_PROMPT
    )

def get_followup_email_prompt():
    """Get the follow-up email template prompt"""
    return PromptTemplate(
        input_variables=["previous_context", "additional_insights"],
        template=FOLLOWUP_EMAIL_PROMPT
    )


