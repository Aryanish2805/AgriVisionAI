@echo off
REM Run the Streamlit app from the project root.
cd /d %~dp0
if exist .venv\Scripts\activate.bat (
    echo Activating local virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No local virtual environment found. Using system Python.
)
python -m streamlit run frontend\app.py
pause
