"""
Configuration settings for FloatChat-Minimal
"""

# Agent Configuration
AGENT_CONFIG = {
    "name": "FloatChat-Minimal",
    "version": "0.1.0",
    "owner": "INCOIS/MoES — PoC by DJ",
    "language": "en-IN"
}

# Runtime Configuration
RUNTIME_CONFIG = {
    "stack": "python-backend",
    "entrypoints": [
        "FastAPI service for /chat and /search endpoints",
        "Streamlit client (single-page app) launched from Python"
    ],
    "constraints": [
        "No authentication, fully public",
        "All factual data about ARGO must come from web search results in this session",
        "No local NetCDF parsing in Step 1 (links & summaries only)",
        "No background jobs; every reply completes in one turn"
    ]
}

# Data Sources Configuration
DATA_SOURCES = {
    "allowed_domains_priority_first": [
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
    ],
    "disallowed_domains": [
        "social media posts without institutional backing",
        "content farms and AI-written aggregators"
    ],
    "freshness_requirement": "Prefer pages updated within the last 24 months; if older, warn the user."
}

# Rate Limits
RATE_LIMITS = {
    "per_minute_search_calls": 5,
    "per_turn_max_search_calls": 3,
    "per_turn_max_tokens": 1800
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "title": "FloatChat-Minimal API",
    "description": "ARGO/INCOIS oceanographic data assistant API"
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "host": "localhost",
    "port": 8501,
    "page_title": "FloatChat — Argo Assistant (Step 1)",
    "page_icon": "🌊",
    "layout": "wide"
}

# Safety and Quality Rules
SAFETY_RULES = [
    "Never invent numbers or facts. If unknown, say so and offer links.",
    "Every factual claim must be attributable to at least one web.search result from this turn.",
    "Prefer official program pages, data portals, or peer-reviewed sources.",
    "If sources disagree, state it briefly and present both links."
]

# Intent Patterns
INTENT_PATTERNS = {
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
        r"argo india",
        r"incois argo"
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

# Example Queries for UI
EXAMPLE_QUERIES = [
    "What is Argo and what variables does it measure?",
    "Status of Argo floats in Indian Ocean",
    "How to download Argo data?",
    "Find nearest Argo floats to coordinates",
    "INCOIS Argo program activities",
    "Argo temperature and salinity measurements",
    "Bay of Bengal oceanographic data",
    "Arabian Sea float deployments"
]
