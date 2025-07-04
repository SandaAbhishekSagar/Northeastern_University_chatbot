@echo off
echo 🎓 Northeastern University Chatbot - Quick Start
echo ================================================

REM Activate the Python environment
echo 🔧 Activating Python environment...
call env_py3.9\Scripts\activate.bat

REM Check if Ollama is running
echo 🔍 Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not running!
    echo Please start Ollama with: ollama serve
    echo Then pull the model with: ollama pull llama2:7b
    pause
    exit /b 1
)

REM Start the system
echo 🚀 Starting Northeastern University Chatbot...
python start_system.py

pause 