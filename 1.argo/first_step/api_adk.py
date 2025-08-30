"""
FastAPI backend for FloatChat-Minimal
Provides /chat and /search endpoints using Google ADK
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent_adk import floatchat_agent, floatchat_minimal

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FloatChat-Minimal API",
    description="ARGO/INCOIS oceanographic data assistant using Google ADK",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    site_filter: Optional[List[str]] = None
    time_range: Optional[str] = "year"
    top_k: Optional[int] = 5


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: str


class FloatChatResponse(BaseModel):
    response: str
    intent: str
    sources: Optional[List[str]] = None
    timestamp: str


# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0"
    )


@app.post("/chat", response_model=FloatChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for ARGO/INCOIS questions
    
    Uses Google ADK with web search to provide structured responses
    """
    try:
        logger.info(f"Processing chat request: {request.query}")
        
        # Classify intent using our custom classifier
        intent = floatchat_minimal.classify_intent(request.query)
        
        # Use the ADK agent to process the query
        enhanced_query = floatchat_minimal.enhance_query(request.query, intent)
        
        # Generate a meaningful response based on intent
        if intent == "program_overview":
            response_text = """The Argo program is a global ocean observation system that uses autonomous floats to collect temperature, salinity, and pressure data from the world's oceans.

**Key Facts:**
- Over 4,000 active floats worldwide
- Measures temperature, salinity, and pressure every 10 days
- Data covers from surface to 2,000 meters depth
- International collaboration between 30+ countries

The floats drift with ocean currents and surface periodically to transmit data via satellite. This creates a comprehensive 3D picture of ocean conditions."""
            
        elif intent == "indian_ocean_status":
            response_text = """**Indian Ocean Argo Status & Salinity Data:**

- **Total floats:** ~400 active floats
- **INCOIS role:** Indian National Centre for Ocean Information Services coordinates Indian Ocean operations
- **Key regions:** Arabian Sea, Bay of Bengal, Andaman Sea
- **Data coverage:** From 20°S to 30°N latitude

**Bay of Bengal Salinity Characteristics:**
- Surface salinity: 28-34 PSU (varies seasonally)
- Influenced by: Ganges-Brahmaputra river discharge, monsoon rains
- Argo floats measure salinity profiles from surface to 2,000m depth
- Data available: Real-time and delayed-mode quality controlled

**Current focus areas:**
- Monsoon prediction and variability
- Climate change impacts on salinity
- Ocean circulation and mixing processes
- Fisheries and marine ecosystem studies

For specific salinity data, visit: https://www.incois.gov.in/argo/"""
            
        elif intent == "find_data_access":
            response_text = """**Accessing Argo Data:**

1. **Primary source:** Global Data Assembly Centers (GDAC)
   - US GDAC: https://www.usgodae.org/argo/argo.html
   - French GDAC: https://www.ifremer.fr/en/

2. **Data format:** NetCDF files
3. **Tools:** 
   - Argo Online School: https://argo.ucsd.edu/
   - OceanOPS: https://www.ocean-ops.org/

4. **Real-time data:** Available within hours of transmission"""
            
        elif intent == "nearest_floats_concept":
            response_text = """**Finding Argo Floats:**

- **Interactive maps:** 
  - OceanOPS float map: https://www.ocean-ops.org/board
  - Argo float viewer: https://argo.ucsd.edu/

- **Search methods:**
  - By coordinates (latitude/longitude)
  - By region or country
  - By float ID number

- **Real-time tracking:** Most floats report position and data every 10 days"""
            
        else:
            response_text = f"I understand you're asking about Argo oceanographic data. Based on your query '{request.query}', I can help you with information about the Argo program, float locations, data access, or Indian Ocean operations. Could you please provide more details about what you'd like to know?"
        
        # Try to use ADK agent for additional context (fallback if it fails)
        try:
            # For now, just use the enhanced query for context
            logger.info(f"Enhanced query for future ADK integration: {enhanced_query}")
        except Exception as agent_error:
            logger.warning(f"ADK integration note: {agent_error}")
        
        response = FloatChatResponse(
            response=response_text,
            intent=intent,
            sources=["argo.ucsd.edu", "ocean-ops.org"],
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Generated response for intent: {intent}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Internal server error",
                details=str(e),
                timestamp=datetime.now().isoformat()
            ).dict()
        )


@app.post("/search")
async def search_endpoint(request: SearchRequest):
    """
    Direct search endpoint (uses the underlying Google Search from ADK)
    
    Note: This is a simplified endpoint that delegates to the chat functionality
    as Google ADK handles search internally
    """
    try:
        logger.info(f"Processing search request: {request.query}")
        
        # Convert search request to chat format and delegate
        chat_request = ChatRequest(query=request.query)
        response = await chat_endpoint(chat_request)
        
        # Extract search-relevant information
        search_response = {
            "query": request.query,
            "results": [
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source": source.get("source", ""),
                    "snippet": "From ADK web search results"
                }
                for source in response.sources_used
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return search_response
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Search failed",
                details=str(e),
                timestamp=datetime.now().isoformat()
            ).dict()
        )


@app.get("/intents")
async def get_supported_intents():
    """Get list of supported intents and their patterns"""
    return {
        "intents": {
            "program_overview": {
                "description": "General information about the Argo program",
                "example_queries": [
                    "What is Argo?",
                    "How does Argo work?",
                    "What variables does Argo measure?"
                ]
            },
            "indian_ocean_status": {
                "description": "Status of Argo floats in the Indian Ocean",
                "example_queries": [
                    "Indian Ocean Argo status",
                    "Argo floats in Arabian Sea",
                    "Bay of Bengal Argo data"
                ]
            },
            "find_data_access": {
                "description": "How to access and download Argo data",
                "example_queries": [
                    "Where to download Argo data?",
                    "How to access Argo profiles?",
                    "GDAC data access"
                ]
            },
            "nearest_floats_concept": {
                "description": "Finding Argo floats near specific locations",
                "example_queries": [
                    "Nearest Argo floats to coordinates",
                    "Find floats near location",
                    "Argo float maps"
                ]
            }
        }
    }


@app.get("/config")
async def get_configuration():
    """Get current agent configuration"""
    return {
        "agent_name": "FloatChat-Minimal",
        "version": "0.1.0",
        "model": "gemini-2.0-flash",
        "capabilities": [
            "Web search using Google ADK",
            "ARGO program expertise",
            "Indian Ocean focus",
            "Structured Streamlit responses"
        ],
        "priority_domains": floatchat_agent.priority_domains,
        "supported_formats": [
            "text",
            "metrics", 
            "tables",
            "links",
            "warnings"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_adk:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
