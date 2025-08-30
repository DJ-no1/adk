"""
Web Search Tool for FloatChat-Minimal
Uses Google ADK for web search functionality with focus on ARGO/INCOIS domains
"""

import requests
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    rank: int
    title: str
    url: str
    snippet: str
    published: Optional[str] = None
    updated: Optional[str] = None
    source: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


class WebSearchTool:
    """Google ADK-based web search tool for ARGO/oceanographic data queries"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.cx = "017576662512468239146:omuauf_lfve"  # Custom search engine ID
        
        # Priority domains as per specification
        self.priority_domains = [
            "incois.gov.in",
            "argo.ucsd.edu", 
            "doi.org",
            "www.ocean-ops.org",
            "www.usgodae.org",
            "www.seanoe.org",
            "www.ncei.noaa.gov",
            "www.jcommops.org",
            "www.euro-argo.eu",
            "www.ifremer.fr"
        ]
        
        # Disallowed pattern detection
        self.disallowed_patterns = [
            "facebook.com", "twitter.com", "instagram.com",
            "contentfarm", "ai-written", "generated-content"
        ]
    
    def search(
        self,
        query: str,
        site_filter: Optional[List[str]] = None,
        time_range: str = "year",
        top_k: int = 5
    ) -> SearchResponse:
        """
        Perform web search using Google Custom Search API
        
        Args:
            query: Natural language search query
            site_filter: List of domains to restrict search to
            time_range: Time filter (any, year, month, week)
            top_k: Maximum results to return (1-10)
        
        Returns:
            SearchResponse with structured results
        """
        try:
            # Build search parameters
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": min(top_k, 10),
                "safe": "active"
            }
            
            # Apply time filter
            if time_range != "any":
                date_restrict = {
                    "week": "d7",
                    "month": "m1", 
                    "year": "y1"
                }.get(time_range, "y1")
                params["dateRestrict"] = date_restrict
            
            # Apply site filter
            if site_filter:
                site_query = " OR ".join([f"site:{domain}" for domain in site_filter])
                params["q"] = f"{query} ({site_query})"
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse results
            results = []
            items = data.get("items", [])
            
            for idx, item in enumerate(items):
                # Extract domain
                url = item.get("link", "")
                domain = self._extract_domain(url)
                
                # Skip disallowed domains
                if self._is_disallowed_domain(domain):
                    continue
                
                result = SearchResult(
                    rank=idx + 1,
                    title=item.get("title", ""),
                    url=url,
                    snippet=item.get("snippet", ""),
                    source=domain
                )
                
                # Try to extract publication date from metadata
                if "pagemap" in item:
                    meta = item["pagemap"]
                    result.published = self._extract_date(meta)
                
                results.append(result)
            
            # Sort by domain priority, then by rank
            results = self._sort_by_priority(results)
            
            return SearchResponse(results=results[:top_k])
            
        except requests.RequestException as e:
            logger.error(f"Search API request failed: {e}")
            return SearchResponse(results=[])
        except Exception as e:
            logger.error(f"Search operation failed: {e}")
            return SearchResponse(results=[])
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def _is_disallowed_domain(self, domain: str) -> bool:
        """Check if domain should be filtered out"""
        domain_lower = domain.lower()
        return any(pattern in domain_lower for pattern in self.disallowed_patterns)
    
    def _extract_date(self, meta: Dict[str, Any]) -> Optional[str]:
        """Extract publication date from page metadata"""
        # Try various metadata fields for dates
        date_fields = [
            "metatags", "article", "webpage", "newsarticle"
        ]
        
        for field in date_fields:
            if field in meta:
                items = meta[field]
                if isinstance(items, list) and items:
                    item = items[0]
                    # Look for common date fields
                    for date_key in ["published_time", "modified_time", "date", "publishdate"]:
                        if date_key in item:
                            return item[date_key]
        
        return None
    
    def _sort_by_priority(self, results: List[SearchResult]) -> List[SearchResult]:
        """Sort results by domain priority and relevance"""
        def priority_score(result: SearchResult) -> tuple:
            domain = result.source
            
            # Check if domain is in priority list
            if domain in self.priority_domains:
                priority_idx = self.priority_domains.index(domain)
            else:
                priority_idx = len(self.priority_domains)
            
            # Check recency (prefer recent if date available)
            recency_score = 0
            if result.published or result.updated:
                try:
                    date_str = result.published or result.updated
                    # Simple year extraction for recency scoring
                    if "2024" in date_str or "2025" in date_str:
                        recency_score = -1  # More recent = lower score (better)
                    elif "2023" in date_str:
                        recency_score = 0
                    else:
                        recency_score = 1
                except:
                    recency_score = 0
            
            return (priority_idx, recency_score, result.rank)
        
        return sorted(results, key=priority_score)


# Example usage for testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        search_tool = WebSearchTool(api_key)
        
        # Test search
        response = search_tool.search(
            query="Argo program overview variables measured temperature salinity",
            site_filter=["argo.ucsd.edu", "euro-argo.eu"],
            time_range="year",
            top_k=5
        )
        
        print(f"Found {len(response.results)} results:")
        for result in response.results:
            print(f"{result.rank}. {result.title}")
            print(f"   {result.url}")
            print(f"   {result.snippet[:100]}...")
            print()
