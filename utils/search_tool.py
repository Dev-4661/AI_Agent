from tavily import TavilyClient
from typing import List, Dict, Any
from config.settings import Config

class TavilySearchTool:
    """Tavily search tool for company information retrieval"""
    
    def __init__(self):
        """Initialize Tavily client"""
        try:
            Config.validate_config()
            self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
        except Exception as e:
            raise ValueError(f"Failed to initialize Tavily client: {str(e)}")
    
    def search_company_info(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Search for company information using Tavily
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results
        """
        if max_results is None:
            max_results = Config.MAX_SEARCH_RESULTS
            
        try:
            # Perform search with Tavily
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
            
            # Extract relevant information from results
            search_results = []
            
            if 'results' in response:
                for result in response['results']:
                    search_result = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', ''),
                        'score': result.get('score', 0)
                    }
                    search_results.append(search_result)
            
            # Add answer if available
            if 'answer' in response and response['answer']:
                search_results.insert(0, {
                    'title': 'Direct Answer',
                    'url': 'tavily_answer',
                    'content': response['answer'],
                    'score': 1.0
                })
            
            return search_results
            
        except Exception as e:
            print(f"Error during Tavily search: {str(e)}")
            return []
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for prompt inclusion
        
        Args:
            results (List[Dict[str, Any]]): Search results
            
        Returns:
            str: Formatted search results
        """
        if not results:
            return "No search results found."
        
        formatted_results = []
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Unknown Title')
            content = result.get('content', 'No content available')
            url = result.get('url', 'No URL')
            
            formatted_result = f"""
Result {i}:
Title: {title}
URL: {url}
Content: {content}
{'='*50}
"""
            formatted_results.append(formatted_result)
        
        return '\n'.join(formatted_results)
    
    def search_and_format(self, query: str, max_results: int = None) -> str:
        """
        Search for company information and return formatted results
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            str: Formatted search results
        """
        results = self.search_company_info(query, max_results)
        return self.format_search_results(results)
