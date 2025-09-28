#!/bin/bash
# ----- start_all.sh -----
echo "🚀 Starting FeeLink full stack..."

# 1. Build and run the C++ mesh backend
echo "[1/3] Building C++ mesh backend..."
cmake -S backend/cpp-mesh -B backend/cpp-mesh/build -DCMAKE_BUILD_TYPE=Debug
cmake --build backend/cpp-mesh/build --config Debug

echo "[1/3] Running C++ mesh backend..."
./backend/cpp-mesh/build/feelink &

# 2. Start Python AI backend (Flask/FastAPI)
echo "[2/3] Starting Python AI backend..."
if [ -d "venv" ]; then
    ./venv/bin/python backend/python-ai/app.py &
else
    python3 backend/python-ai/app.py &
fi

# 3. Build and run the frontend (React/Vue)
echo "[3/3] Building and starting frontend..."
cd frontend
npm install
npm run dev &

echo "✅ All services started!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
wait
