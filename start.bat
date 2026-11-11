@echo off
echo Starting Sunbeam Samanvay 1.0 (Ace One National Conclave) Server...
echo Theme: Green and White | Wavy Dynamic Frontend | FastAPI SQLite Backend
echo.
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
pause
