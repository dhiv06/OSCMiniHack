# ----- start_all.ps1 -----
Write-Host "🚀 Starting TerraLink-X full stack..."

# 1. Build and run the C++ mesh backend
Write-Host "[1/3] Building C++ mesh backend..."
cmake -S backend/cpp-mesh -B backend/cpp-mesh/build -DCMAKE_BUILD_TYPE=Debug
cmake --build backend/cpp-mesh/build --config Debug

Write-Host "[1/3] Running C++ mesh backend..."
Start-Process -NoNewWindow -FilePath ".\backend\cpp-mesh\build\Debug\terralink-x.exe"

# 2. Start Python AI backend (Flask/FastAPI)
Write-Host "[2/3] Starting Python AI backend..."
Start-Process -NoNewWindow "python" -ArgumentList "backend/python-ai/app.py"

# 3. Start React frontend (Vite)
Write-Host "[3/3] Starting React frontend..."
Start-Process -NoNewWindow "npm.cmd" -ArgumentList "start" -WorkingDirectory "frontend"

Write-Host "✅ All components started!"
Write-Host "Frontend: http://localhost:5173"
Write-Host "Backend API: http://localhost:5000"
Write-Host "C++ Mesh node is running in background."
# --------------------------