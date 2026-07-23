#!/bin/bash
echo "Starting AutoGate UNS - Pos Satpam..."
echo ""
echo "Backend: http://localhost:3000"
echo ""

# Cek virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Jalankan server
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
