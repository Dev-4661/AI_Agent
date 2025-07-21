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
