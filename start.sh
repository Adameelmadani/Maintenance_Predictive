#!/bin/bash
# PredMaint AI - Launch both servers (macOS/Linux)
echo "Starting Flask API on :5000..."
cd "$(dirname "$0")"
PYTHONIOENCODING=utf-8 python api/app.py &
sleep 3
echo "Starting React frontend on :5173..."
cd frontend && npm run dev &
echo ""
echo "Dashboard: http://localhost:5173"
echo "API:       http://localhost:5000/api/health"
wait
