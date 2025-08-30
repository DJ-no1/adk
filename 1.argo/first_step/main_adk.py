"""
FloatChat-Minimal Main Entry Point
Orchestrates the Google ADK-based ARGO assistant system
"""

import os
import sys
import subprocess
import argparse
import time
import signal
from pathlib import Path

def print_banner():
    """Print the FloatChat-Minimal banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    FloatChat-Minimal v0.1.0                  ║
║                                                              ║
║          🌊 ARGO Oceanographic Data Assistant 🌊             ║
║                                                              ║
║   Powered by Google ADK • INCOIS/MoES PoC • Built by DJ      ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_info():
    """Print system information"""
    print("\n📋 SYSTEM INFORMATION")
    print("="*50)
    print(f"🏛️  Owner: INCOIS/MoES — Proof of Concept by DJ")
    print(f"🔧  Stack: Google ADK + FastAPI + Streamlit")
    print(f"📦  Version: 0.1.0")
    print(f"🌐  Language: en-IN")
    print(f"🎯  Focus: ARGO/INCOIS oceanographic data assistance")
    print("\n🛠️  RUNTIME CONFIGURATION")
    print("="*50)
    print("✅ Google ADK Agent with integrated web search")
    print("✅ FastAPI backend (/chat and /search endpoints)")
    print("✅ Streamlit frontend (single-page app)")
    print("✅ No authentication (fully public)")
    print("✅ Real-time web search for ARGO facts")
    print("✅ Structured responses for non-experts")

def print_capabilities():
    """Print agent capabilities"""
    print("\n🎯 AGENT CAPABILITIES")
    print("="*50)
    print("📊 Intent Classification:")
    print("   • program_overview - What is Argo? How does it work?")
    print("   • indian_ocean_status - Argo floats in Arabian Sea, Bay of Bengal")
    print("   • find_data_access - GDAC portals, NetCDF downloads")
    print("   • nearest_floats_concept - Interactive maps, float finder tools")
    
    print("\n🔍 Data Sources (Priority Order):")
    domains = [
        "incois.gov.in", "argo.ucsd.edu", "doi.org", "www.ocean-ops.org",
        "www.usgodae.org", "www.seanoe.org", "www.ncei.noaa.gov", 
        "www.jcommops.org", "www.euro-argo.eu", "www.ifremer.fr"
    ]
    for i, domain in enumerate(domains, 1):
        print(f"   {i:2d}. {domain}")
    
    print("\n📱 Response Formats:")
    print("   • Text blocks (title, subtitle, body, caption)")
    print("   • Metrics displays")
    print("   • Data tables")
    print("   • Source link collections")
    print("   • Warning messages")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 DEPENDENCY CHECK")
    print("="*50)
    
    required_packages = {
        "google.adk": "google-adk",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn", 
        "streamlit": "streamlit",
        "requests": "requests",
        "pydantic": "pydantic"
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies satisfied")
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting API Server...")
    print("="*50)
    
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "api_adk:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload"
    ])
    
    print("🔗 API Server running at: http://localhost:8001")
    print("📖 API Documentation: http://localhost:8001/docs")
    return api_process

def start_streamlit_app():
    """Start the Streamlit app"""
    print("\n🎨 Starting Streamlit Frontend...")
    print("="*50)
    
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "streamlit_app_adk.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])
    
    print("🔗 Streamlit App running at: http://localhost:8501")
    return streamlit_process

def test_agent():
    """Test the agent functionality"""
    print("\n🧪 AGENT TEST")
    print("="*50)
    
    try:
        from agent_adk import floatchat_agent, floatchat_minimal
        print("✅ Agent initialization successful")
        
        # Test intent classification
        test_queries = [
            "What is Argo?",
            "Indian Ocean Argo status",
            "How to download Argo data?",
            "Find floats near coordinates"
        ]
        
        print("\n🎯 Intent Classification Test:")
        for query in test_queries:
            intent = floatchat_minimal.classify_intent(query)
            print(f"   '{query}' → {intent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="FloatChat-Minimal - ARGO Data Assistant")
    parser.add_argument("--info", action="store_true", help="Show system information")
    parser.add_argument("--test", action="store_true", help="Test agent functionality")
    parser.add_argument("--api-only", action="store_true", help="Start API server only")
    parser.add_argument("--streamlit-only", action="store_true", help="Start Streamlit only")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.info:
        print_system_info()
        print_capabilities()
        return
    
    if args.check_deps:
        check_dependencies()
        return
    
    if args.test:
        if check_dependencies():
            test_agent()
        return
    
    # Check dependencies before starting services
    if not check_dependencies():
        print("\n❌ Cannot start services due to missing dependencies")
        return
    
    # Test agent before starting services
    if not test_agent():
        print("\n❌ Agent test failed, aborting startup")
        return
    
    processes = []
    
    try:
        if args.api_only:
            api_process = start_api_server()
            processes.append(api_process)
            print("\n✅ API-only mode started. Press Ctrl+C to stop.")
        
        elif args.streamlit_only:
            streamlit_process = start_streamlit_app()
            processes.append(streamlit_process)
            print("\n✅ Streamlit-only mode started. Press Ctrl+C to stop.")
        
        else:
            # Start both services
            print("\n🚀 STARTING FLOATCHAT-MINIMAL SYSTEM")
            print("="*50)
            
            api_process = start_api_server()
            processes.append(api_process)
            
            # Wait a moment for API to start
            time.sleep(3)
            
            streamlit_process = start_streamlit_app()
            processes.append(streamlit_process)
            
            print("\n✅ SYSTEM READY")
            print("="*50)
            print("🔗 Streamlit App: http://localhost:8501")
            print("🔗 API Server: http://localhost:8000")
            print("📖 API Docs: http://localhost:8000/docs")
            print("\n💡 Try asking: 'What is the Argo program?'")
            print("\nPress Ctrl+C to stop all services...")
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping FloatChat-Minimal...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
