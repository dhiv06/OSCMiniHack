#!/usr/bin/env python3
"""
FeeLink Simple Startup - Just run the backend, no checks
"""
import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║        🚀 Starting FeeLink Backend 🚀     ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    system = platform.system()
    
    if system == "Windows":
        if Path("venv/Scripts/python.exe").exists():
            command = [r".\venv\Scripts\python.exe", r"backend\python-ai\app.py"]
        else:
            command = ["python", r"backend\python-ai\app.py"]
    else:
        if Path("venv/bin/python").exists():
            command = ["./venv/bin/python", "backend/python-ai/app.py"]
        else:
            command = ["python3", "backend/python-ai/app.py"]
    
    print("🐍 Starting FeeLink backend...")
    print("🌐 Will be available at: http://localhost:5000")
    print("⚠️  Press Ctrl+C to stop")
    print()
    
    try:
        # Run the backend directly
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\n🛑 FeeLink stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()