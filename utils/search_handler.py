"""
Search Handler Module
Fetches real-time data from free search engines
"""

import requests
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import streamlit as st


class SearchHandler:
    """Handles real-time data fetching from search engines"""
    
    def __init__(self):
        self.ddgs = None
        self._init_ddgs()
    
    def _init_ddgs(self):
        """Initialize DuckDuckGo search"""
        try:
            self.ddgs = DDGS()
        except Exception as e:
            st.warning(f"Search initialization warning: {e}")
    
    def search_web(
        self,
        query: str,
        max_results: int = 10,
        region: str = "wt-wt"
    ) -> List[Dict]:
        """Search the web using DuckDuckGo"""
        if not self.ddgs:
            self._init_ddgs()
        
        try:
            results = list(self.ddgs.text(
                keywords=query,
                region=region,
                safesearch="moderate",
                max_results=max_results
            ))
            return results
        except Exception as e:
            st.warning(f"Search error: {e}")
            return []
    
    def search_news(
        self,
        query: str,
        max_results: int = 10,
        time_range: str = "w"
    ) -> List[Dict]:
        """Search for news articles"""
        if not self.ddgs:
            self._init_ddgs()
        
        try:
            results = list(self.ddgs.news(
                keywords=query,
                region="wt-wt",
                safesearch="moderate",
                timelimit=time_range,
                max_results=max_results
            ))
            return results
        except Exception as e:
            st.warning(f"News search error: {e}")
            return []
    
    def get_instant_answer(self, query: str) -> Optional[Dict]:
        """Get instant answer from DuckDuckGo"""
        if not self.ddgs:
            self._init_ddgs()
        
        try:
            results = self.ddgs.answers(query)
            if results:
                return results[0]
            return None
        except Exception as e:
            return None
    
    def compile_research_data(
        self,
        topic: str,
        include_news: bool = True,
        include_web: bool = True
    ) -> str:
        """Compile research data from multiple sources"""
        compiled_data = []
        
        if include_web:
            web_results = self.search_web(topic, max_results=5)
            if web_results:
                compiled_data.append("## Web Search Results\n")
                for result in web_results:
                    compiled_data.append(f"**{result.get('title', 'No title')}**")
                    compiled_data.append(f"{result.get('body', 'No description')}")
                    compiled_data.append(f"Source: {result.get('href', '')}\n")
        
        if include_news:
            news_results = self.search_news(topic, max_results=5)
            if news_results:
                compiled_data.append("\n## Recent News\n")
                for result in news_results:
                    compiled_data.append(f"**{result.get('title', 'No title')}**")
                    compiled_data.append(f"Date: {result.get('date', 'Unknown')}")
                    compiled_data.append(f"{result.get('body', 'No description')}")
                    compiled_data.append(f"Source: {result.get('source', '')}\n")
        
        # Get instant answer if available
        instant = self.get_instant_answer(topic)
        if instant:
            compiled_data.append("\n## Quick Facts\n")
            compiled_data.append(instant.get('text', ''))
        
        return "\n".join(compiled_data) if compiled_data else "No data found."
