@echo off
echo Starting AutoGate UNS - Pos Satpam...
echo.
echo Backend: http://localhost:3000
echo.

REM Cek virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

REM Jalankan server
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
