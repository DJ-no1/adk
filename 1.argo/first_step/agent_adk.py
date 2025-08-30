"""
FloatChat-Minimal Agent using Google ADK
ARGO Oceanographic Data Assistant powered by Google ADK components
"""

import re
import logging
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools import google_search

logger = logging.getLogger(__name__)


class FloatChatMinimal:
    """ARGO Oceanographic Data Assistant using Google ADK"""
    
    def __init__(self):
        # Intent classification patterns
        self.intent_patterns = {
            "program_overview": [
                r"what is argo",
                r"how does argo work", 
                r"variables measured by argo",
                r"argo program",
                r"argo floats",
                r"argo network"
            ],
            "indian_ocean_status": [
                r"indian ocean argo",
                r"status of argo floats in arabian sea", 
                r"bay of bengal floats",
                r"bay of bengal",
                r"bengal salinity",
                r"salinity level",
                r"argo india",
                r"incois argo",
                r"indian ocean status"
            ],
            "find_data_access": [
                r"where to download argo data",
                r"get argo profiles",
                r"how to access argo netcdf",
                r"argo data download",
                r"gdac",
                r"argo ftp"
            ],
            "nearest_floats_concept": [
                r"nearest argo floats to",
                r"floats near",
                r"closest argo to coordinates",
                r"argo map", 
                r"find argo floats"
            ]
        }
        
        # Enhanced query generators based on intent
        self.enhanced_queries = {
            "program_overview": "Argo program overview what variables measured temperature salinity pressure ocean profiling floats how it works",
            "indian_ocean_status": "Indian Ocean Argo floats status current number active INCOIS Arabian Sea Bay Bengal distribution",
            "find_data_access": "Argo data download access GDAC global data assembly centers netCDF files instructions how to",
            "nearest_floats_concept": "Argo float interactive map finder location coordinates nearest search tools ocean-ops"
        }
    
    def classify_intent(self, user_text: str) -> str:
        """Classify user intent from input text"""
        user_text_lower = user_text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_text_lower):
                    logger.info(f"Intent classified: {intent}")
                    return intent
        
        logger.info("Intent classified: program_overview (default)")
        return "program_overview"
    
    def enhance_query(self, user_text: str, intent: str) -> str:
        """Generate enhanced search query based on intent and user input"""
        base_query = self.enhanced_queries.get(intent, self.enhanced_queries["program_overview"])
        
        # Combine user text with enhanced query for better search results
        enhanced = f"{user_text} {base_query}"
        
        logger.info(f"Enhanced query: {enhanced}")
        return enhanced


# Create the ADK agent instance
floatchat_agent = Agent(
    name="FloatChat_Minimal",
    model="gemini-2.0-flash",
    description="ARGO oceanographic data assistant specializing in float information, data access, and Indian Ocean operations",
    instruction="""You are FloatChat-Minimal, an expert assistant for ARGO oceanographic data and float operations.

CORE EXPERTISE:
- ARGO program overview and float technology
- Indian Ocean float status and INCOIS operations  
- Data download and access instructions (GDAC, NetCDF)
- Float location and mapping tools

RESPONSE GUIDELINES:
1. Use Google Search to get current, accurate information
2. Prioritize official ARGO sources (argo.ucsd.edu, euro-argo.eu, ocean-ops.org)
3. For Indian Ocean queries, include INCOIS (incois.gov.in) information
4. Provide practical, actionable guidance for data access
5. Keep responses focused and concise
6. Always cite your sources

When users ask about:
- "What is Argo" → Explain program, variables measured, how floats work
- "Indian Ocean status" → Current float numbers, distribution, INCOIS role
- "Data access" → GDAC portals, download instructions, file formats  
- "Finding floats" → Interactive map tools, coordinate search methods

Use Google Search to ensure information is current and accurate.""",
    
    tools=[google_search]
)

# Create the intent classifier instance  
floatchat_minimal = FloatChatMinimal()

# Export both for backward compatibility
root_agent = floatchat_agent
