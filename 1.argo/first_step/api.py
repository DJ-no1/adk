"""
FastAPI Backend for FloatChat-Minimal
Provides /chat and /search endpoints as specified
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent import FloatChatAgent, AgentResponse
from web_search_tool import WebSearchTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FloatChat-Minimal API",
    description="ARGO/INCOIS oceanographic data assistant API",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise RuntimeError("Missing GOOGLE_API_KEY")

agent = FloatChatAgent(api_key)


# Request/Response models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    assistant_summary_md: str
    streamlit_blocks: List[Dict[str, Any]]
    sources_used: List[Dict[str, str]]
    session_id: str
    timestamp: str


class SearchRequest(BaseModel):
    query: str
    site_filter: Optional[List[str]] = None
    time_range: str = "year"
    top_k: int = 5


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
    timestamp: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "FloatChat-Minimal",
        "version": "0.1.0",
        "owner": "INCOIS/MoES — PoC by DJ",
        "language": "en-IN",
        "status": "running",
        "endpoints": {
            "/chat": "Main chat interface for ARGO queries",
            "/search": "Direct web search interface",
            "/health": "Health check endpoint"
        },
        "constraints": [
            "No authentication, fully public",
            "All factual data about ARGO must come from web search results in this session",
            "No local NetCDF parsing in Step 1 (links & summaries only)",
            "No background jobs; every reply completes in one turn"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test search functionality
        search_tool = WebSearchTool(api_key)
        test_response = search_tool.search("test", top_k=1)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "agent": "ok",
                "search_tool": "ok" if test_response else "error",
                "api_key": "configured" if api_key else "missing"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for ARGO queries
    
    Processes natural language queries about ARGO floats, oceanographic data,
    and related topics. Returns structured response suitable for Streamlit rendering.
    """
    try:
        logger.info(f"Chat request: {request.query[:100]}...")
        
        # Process query through agent
        agent_response = agent.process_query(request.query)
        
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Format response
        response = ChatResponse(
            assistant_summary_md=agent_response.assistant_summary_md,
            streamlit_blocks=agent_response.streamlit_blocks,
            sources_used=[
                {
                    "title": src.title,
                    "url": src.url,
                    "domain": src.domain
                }
                for src in agent_response.sources_used
            ],
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Chat response generated with {len(response.sources_used)} sources")
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Direct web search endpoint
    
    Provides direct access to web search functionality with domain filtering
    and time range constraints as specified in the agent requirements.
    """
    try:
        logger.info(f"Search request: {request.query[:100]}...")
        
        # Validate parameters
        if request.top_k < 1 or request.top_k > 10:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 10")
        
        if request.time_range not in ["any", "year", "month", "week"]:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        # Perform search
        search_tool = WebSearchTool(api_key)
        search_response = search_tool.search(
            query=request.query,
            site_filter=request.site_filter,
            time_range=request.time_range,
            top_k=request.top_k
        )
        
        # Format response
        response = SearchResponse(
            results=[
                SearchResult(
                    rank=result.rank,
                    title=result.title,
                    url=result.url,
                    snippet=result.snippet,
                    published=result.published,
                    updated=result.updated,
                    source=result.source
                )
                for result in search_response.results
            ],
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Search response generated with {len(response.results)} results")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/intents")
async def get_supported_intents():
    """
    Get list of supported intents and their patterns
    """
    return {
        "intents_supported": [
            {
                "name": "program_overview",
                "user_patterns": ["what is argo", "how does argo work", "variables measured by argo"],
                "description": "General information about the Argo program"
            },
            {
                "name": "indian_ocean_status", 
                "user_patterns": ["indian ocean argo", "status of argo floats in arabian sea", "bay of bengal floats"],
                "description": "Status of Argo floats in Indian Ocean region"
            },
            {
                "name": "find_data_access",
                "user_patterns": ["where to download argo data", "get argo profiles", "how to access argo netcdf"],
                "description": "Information about accessing Argo data"
            },
            {
                "name": "nearest_floats_concept",
                "user_patterns": ["nearest argo floats to", "floats near", "closest argo to coordinates"],
                "description": "Finding nearby Argo floats (guidance to tools)"
            }
        ]
    }


@app.get("/rate_limits")
async def get_rate_limits():
    """
    Get current rate limits and usage guidelines
    """
    return {
        "rate_limits": {
            "per_minute_search_calls": 5,
            "per_turn_max_search_calls": 3,
            "per_turn_max_tokens": 1800
        },
        "guidelines": [
            "Never invent numbers or facts. If unknown, say so and offer links.",
            "Every factual claim must be attributable to at least one web.search result from this turn.",
            "Prefer official program pages, data portals, or peer-reviewed sources.",
            "If sources disagree, state it briefly and present both links."
        ]
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}


if __name__ == "__main__":
    import uvicorn
    
    # For development
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
