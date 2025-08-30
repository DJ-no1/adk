# FloatChat-Minimal: ARGO Data Assistant (Step 1)

## Overview

FloatChat-Minimal is an AI-powered assistant for ARGO oceanographic data discovery, focusing on the Indian Ocean region and INCOIS (Indian National Centre for Ocean Information Services) activities. This is Step 1 of a multi-phase project that provides web search-based information discovery.

**Owner**: INCOIS/MoES — PoC by DJ  
**Version**: 0.1.0  
**Language**: en-IN

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Streamlit     │    │    FastAPI       │    │   Web Search Tool   │
│   Frontend      │◄──►│    Backend       │◄──►│   (Google ADK)      │
│  (Port 8501)    │    │   (Port 8000)    │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
        │                       │                          │
        │                       │                          │
        ▼                       ▼                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   User Chat     │    │  Agent Logic     │    │  Priority Domains   │
│   Interface     │    │  Intent Classification│  - incois.gov.in    │
│                 │    │  Response Generation │  - argo.ucsd.edu     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Features

### Current Capabilities (Step 1)

- **Web Search-Based Information**: All factual data comes from real-time web search
- **Intent Classification**: Automatically categorizes user queries into supported patterns
- **Priority Domain Filtering**: Emphasizes authoritative ARGO/oceanographic sources
- **Streamlit UI**: Interactive chat interface with source tracking
- **FastAPI Backend**: RESTful endpoints for chat and search functionality
- **No Authentication**: Fully public access as specified

### Supported Query Types

1. **Program Overview**: General information about ARGO floats and variables
2. **Indian Ocean Status**: Regional float status and deployments
3. **Data Access**: Instructions for downloading ARGO data
4. **Float Discovery**: Guidance on finding nearby floats

### Constraints (Step 1)

- No local NetCDF file parsing
- No background processing or database storage
- All responses generated in single turn
- Web search results only (no cached/stored data)

## Installation

### Prerequisites

- Python 3.8+
- Google API key for Custom Search
- Internet connection

### Setup

1. **Clone/Navigate to Project Directory**

   ```bash
   cd "c:\Users\Dell\OneDrive\Desktop\Projects at github\adk\1.argo\first_step"
   ```

2. **Install Dependencies**

   ```bash
   pip install -r ../../../requirements.txt
   ```

3. **Configure Environment**
   Create/update `.env` file in the project root:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. **Verify Installation**
   ```bash
   python main.py --test
   ```

## Usage

### Quick Start

```bash
# Launch both API and Streamlit
python main.py

# Launch only API backend
python main.py --api-only

# Launch only Streamlit frontend
python main.py --streamlit-only

# Show system information
python main.py --info
```

### Web Interface

1. Open browser to `http://localhost:8501`
2. Enter ARGO-related queries in the text input
3. View structured responses with sources
4. Use advanced search for direct web queries

### API Endpoints

#### Chat Endpoint

```bash
POST http://localhost:8000/chat
Content-Type: application/json

{
  "query": "What is Argo and what variables does it measure?",
  "session_id": "optional-session-id"
}
```

#### Search Endpoint

```bash
POST http://localhost:8000/search
Content-Type: application/json

{
  "query": "Argo temperature profiles",
  "site_filter": ["argo.ucsd.edu", "incois.gov.in"],
  "time_range": "year",
  "top_k": 5
}
```

#### Other Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /intents` - Supported intent patterns
- `GET /rate_limits` - Current rate limits

## Example Queries

### Program Overview

- "What is Argo and what variables does it measure?"
- "How does the Argo program work?"
- "What oceanographic variables do Argo floats collect?"

### Indian Ocean Focus

- "Status of Argo floats in Indian Ocean"
- "INCOIS Argo program activities"
- "Bay of Bengal float deployments"
- "Arabian Sea temperature measurements"

### Data Access

- "How to download Argo data?"
- "Where can I access Argo NetCDF files?"
- "GDAC data portal instructions"

### Float Discovery

- "Find nearest Argo floats to coordinates"
- "Interactive Argo float maps"
- "How to locate floats in specific regions"

## Configuration

### Priority Domains

The system prioritizes these domains in search results:

1. incois.gov.in (INCOIS official)
2. argo.ucsd.edu (Argo program headquarters)
3. euro-argo.eu (European Argo)
4. ncei.noaa.gov (NOAA data centers)
5. ocean-ops.org (Ocean operations)

### Rate Limits

- Maximum 5 search calls per minute
- Maximum 3 search calls per turn
- Maximum 1800 tokens per response

## Development

### Project Structure

```
1.argo/first_step/
├── main.py              # Entry point and launcher
├── agent.py             # Core agent logic
├── web_search_tool.py   # Google search integration
├── api.py               # FastAPI backend
├── streamlit_app.py     # Streamlit frontend
├── config.py            # Configuration settings
└── README.md            # This file
```

### Testing

```bash
# Run basic tests
python main.py --test

# Test individual components
python web_search_tool.py
python agent.py
```

### Logging

Logs are written to console with INFO level by default. Key events:

- API requests and responses
- Search operations and results
- Intent classification
- Error conditions

## Troubleshooting

### Common Issues

1. **API Key Not Found**

   ```
   Error: GOOGLE_API_KEY not found in environment variables
   ```

   Solution: Ensure `.env` file contains valid Google API key

2. **API Service Offline**

   ```
   ⚠️ API service is not running
   ```

   Solution: Start FastAPI backend with `python main.py --api-only`

3. **Search Results Empty**

   - Check internet connection
   - Verify API key permissions
   - Try broader search terms

4. **Port Already in Use**
   ```
   Error: [Errno 48] Address already in use
   ```
   Solution: Kill existing processes or use different ports

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Roadmap

### Step 2 (Future)

- Local NetCDF file parsing
- Data visualization capabilities
- Profile analysis tools

### Step 3 (Future)

- Real-time data integration
- Advanced analytics
- User authentication and personalization

## Contributing

This is a Proof of Concept (PoC) project for INCOIS/MoES. For questions or contributions, please contact the development team.

## License

Developed for INCOIS/MoES research purposes.

---

**FloatChat-Minimal v0.1.0**  
INCOIS/MoES — PoC by DJ  
Step 1: Web Search-Based Discovery
