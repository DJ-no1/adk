"""
FloatChat-Minimal - Main Entry Point
ARGO/INCOIS Oceanographic Data Assistant - Step 1

This is the main launcher for the FloatChat-Minimal system that provides:
- FastAPI backend for /chat and /search endpoints  
- Streamlit frontend for user interaction
- Web search-based ARGO data assistance

Usage:
    python main.py                    # Launch both API and Streamlit
    python main.py --api-only         # Launch only FastAPI backend
    python main.py --streamlit-only   # Launch only Streamlit frontend
    python main.py --test            # Run basic tests
"""

import os
import sys
import time
import subprocess
import argparse
import threading
import logging
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'requests', 
        'pydantic', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def check_environment():
    """Check environment configuration"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment variables")
        logger.info("Please set GOOGLE_API_KEY in your .env file")
        return False
    
    logger.info("Environment configuration OK")
    return True


def launch_api():
    """Launch FastAPI backend"""
    logger.info("Starting FastAPI backend...")
    try:
        import uvicorn
        from api import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start API: {e}")


def launch_streamlit():
    """Launch Streamlit frontend"""
    logger.info("Starting Streamlit frontend...")
    try:
        # Wait a moment for API to start
        time.sleep(3)
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(current_dir / "streamlit_app.py"),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except Exception as e:
        logger.error(f"Failed to start Streamlit: {e}")


def launch_both():
    """Launch both API and Streamlit in separate threads"""
    logger.info("Launching FloatChat-Minimal system...")
    
    # Start API in a separate thread
    api_thread = threading.Thread(target=launch_api, daemon=True)
    api_thread.start()
    
    # Start Streamlit in main thread
    launch_streamlit()


def run_tests():
    """Run basic system tests"""
    logger.info("Running basic tests...")
    
    try:
        # Test imports
        from agent import FloatChatAgent
        from web_search_tool import WebSearchTool
        logger.info("✓ All imports successful")
        
        # Test environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            logger.info("✓ API key configured")
            
            # Test agent initialization
            agent = FloatChatAgent(api_key)
            logger.info("✓ Agent initialization successful")
            
            # Test intent classification
            intent = agent.classify_intent("What is Argo?")
            logger.info(f"✓ Intent classification working: '{intent}'")
            
            # Test search tool
            search_tool = WebSearchTool(api_key)
            logger.info("✓ Search tool initialization successful")
            
        logger.info("✅ All basic tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def show_system_info():
    """Display system information and usage"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    FloatChat-Minimal v0.1.0                 ║
║              ARGO/INCOIS Data Assistant - Step 1            ║
║                    INCOIS/MoES — PoC by DJ                  ║
╚══════════════════════════════════════════════════════════════╝

🌊 ARGO Oceanographic Data Assistant
📍 Focus: Indian Ocean observations
🔍 Step 1: Web search-based information discovery

Components:
• FastAPI backend (localhost:8000)
  - /chat endpoint for conversational queries
  - /search endpoint for direct web search
  - /health for system status

• Streamlit frontend (localhost:8501)  
  - Interactive chat interface
  - Direct search capabilities
  - Session management and source tracking

Supported Queries:
• Program overview: "What is Argo and what variables does it measure?"
• Regional status: "Status of Argo floats in Indian Ocean"
• Data access: "How to download Argo data?"
• Float discovery: "Find nearest Argo floats to coordinates"

Constraints (Step 1):
• No authentication required
• All data from web search results only
• No local NetCDF parsing
• No background processing
""")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="FloatChat-Minimal: ARGO/INCOIS Data Assistant"
    )
    parser.add_argument(
        "--api-only", 
        action="store_true", 
        help="Launch only FastAPI backend"
    )
    parser.add_argument(
        "--streamlit-only", 
        action="store_true", 
        help="Launch only Streamlit frontend"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run basic system tests"
    )
    parser.add_argument(
        "--info", 
        action="store_true", 
        help="Show system information"
    )
    
    args = parser.parse_args()
    
    # Show system info
    if args.info:
        show_system_info()
        return
    
    # Run tests
    if args.test:
        if not check_dependencies():
            sys.exit(1)
        if not check_environment():
            sys.exit(1)
        if run_tests():
            logger.info("All tests passed! System ready to launch.")
        else:
            sys.exit(1)
        return
    
    # Check prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    # Launch based on arguments
    try:
        if args.api_only:
            launch_api()
        elif args.streamlit_only:
            launch_streamlit()
        else:
            show_system_info()
            launch_both()
            
    except KeyboardInterrupt:
        logger.info("Shutting down FloatChat-Minimal...")
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()