#!/usr/bin/env python3
"""
FeeLink Universal Startup Script
Automatically detects OS and runs the appropriate commands to start FeeLink
"""

import os
import sys
import platform
import subprocess
import time
import threading
from pathlib import Path

def print_banner():
    """Print FeeLink startup banner"""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║        🚀 Starting FeeLink System 🚀      ║
    ║                                           ║
    ║    Emotion-Aware P2P Communication       ║
    ║         with Mood Intelligence            ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

def run_command(command, cwd=None, shell=True):
    """Run a command and return the process"""
    try:
        if platform.system() == "Windows":
            # On Windows, use shell=True for PowerShell commands
            return subprocess.Popen(command, shell=shell, cwd=cwd)
        else:
            # On Linux/Mac, split the command if it's a string
            if isinstance(command, str):
                command = command.split()
            return subprocess.Popen(command, cwd=cwd)
    except Exception as e:
        print(f"❌ Error running command: {command}")
        print(f"   Error: {e}")
        return None

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python
    try:
        python_version = sys.version_info
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except:
        print("❌ Python not found")
        return False
    
    # Check if virtual environment exists
    system = platform.system()
    if system == "Windows":
        venv_python = Path("venv/Scripts/python.exe")
    else:
        venv_python = Path("venv/bin/python")
    
    if venv_python.exists():
        print("✅ Virtual environment found")
    else:
        print("⚠️  Virtual environment not found - will use system Python")
    
    # Check Node.js (optional - for frontend dev server)
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
            return True, True  # Python OK, Node.js OK
        else:
            print("⚠️  Node.js not found - will skip frontend dev server")
            return True, False  # Python OK, Node.js missing
    except:
        print("⚠️  Node.js not found - will skip frontend dev server")
        return True, False  # Python OK, Node.js missing

def start_backend():
    """Start the Python Flask backend"""
    print("\n🐍 Starting Python Backend...")
    
    system = platform.system()
    
    if system == "Windows":
        # Windows command
        if Path("venv/Scripts/python.exe").exists():
            command = r".\venv\Scripts\python.exe backend\python-ai\app.py"
        else:
            command = "python backend/python-ai/app.py"
    else:
        # Linux/Mac command
        if Path("venv/bin/python").exists():
            command = "./venv/bin/python backend/python-ai/app.py"
        else:
            command = "python3 backend/python-ai/app.py"
    
    backend_process = run_command(command)
    
    if backend_process:
        print("✅ Backend started successfully")
        return backend_process
    else:
        print("❌ Failed to start backend")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("\n⚛️  Starting Frontend...")
    
    # Change to frontend directory
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Check if node_modules exists, if not run npm install
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        install_process = run_command("npm install", cwd=frontend_dir)
        if install_process:
            install_process.wait()
            print("✅ Dependencies installed")
        else:
            print("❌ Failed to install dependencies")
            return None
    
    # Start development server
    dev_process = run_command("npm run dev", cwd=frontend_dir)
    
    if dev_process:
        print("✅ Frontend development server started")
        return dev_process
    else:
        print("❌ Failed to start frontend")
        return None

def wait_for_backend():
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to be ready...")
    
    import urllib.request
    import urllib.error
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = urllib.request.urlopen("http://localhost:5000", timeout=2)
            if response.getcode() == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        if attempt % 5 == 0:
            print(f"   Still waiting... ({attempt + 1}/{max_attempts})")
    
    print("⚠️  Backend might not be fully ready, but continuing...")
    return False

def main():
    """Main startup function"""
    print_banner()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"💻 Operating System: {platform.system()} {platform.release()}")
    
    # Check dependencies
    python_ok, node_ok = check_dependencies()
    if not python_ok:
        print("\n❌ Python environment issues. Please check your setup.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Wait for backend to be ready
    wait_for_backend()
    
    # Start frontend (only if Node.js is available)
    frontend_process = None
    if node_ok:
        frontend_process = start_frontend()
    else:
        print("⚠️  Skipping frontend dev server (Node.js not available)")
        print("💡 You can still access the static frontend at: http://localhost:5000")
    
    print("\n🎉 FeeLink is starting up!")
    print("\n📋 Services:")
    print("   🐍 Backend API: http://localhost:5000")
    print("   🌐 Static Frontend: http://localhost:5000 (served by Flask)")
    if frontend_process:
        print("   ⚛️  Frontend Dev: http://localhost:3000 (with hot reload)")
    print("\n🌐 Open your browser and navigate to: http://localhost:5000")
    print("💬 Start sending emotion-aware messages with mood intelligence!")
    
    print("\n⚠️  Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        processes = [backend_process]
        if frontend_process:
            processes.append(frontend_process)
        
        # Wait for any process to exit
        while True:
            for process in processes[:]:  # Copy list to avoid modification during iteration
                if process.poll() is not None:
                    print(f"\n⚠️  A service has stopped (exit code: {process.returncode})")
                    processes.remove(process)
            
            if not processes:
                print("❌ All services have stopped")
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down FeeLink...")
        
        # Terminate all processes
        for process in [backend_process, frontend_process]:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
        
        print("✅ FeeLink stopped successfully")

if __name__ == "__main__":
    main()