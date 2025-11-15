@echo off
title Instagram Scraper & Converter Setup
echo =================================================
echo 🧩 Setting up Instagram Scraper & Converter Environment
echo =================================================

REM --- Step 0: Check if conda is installed ---
where conda >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Conda not found! Please install Anaconda or Miniconda first.
    pause
    exit /b
)

REM --- Step 1: Create new environment ---
echo 🧱 Creating new environment: UziIsGay ...
conda create -n UziIsGay python=3.10 -y

REM --- Step 2: Activate the environment ---
echo 🚀 Activating environment...
call conda activate UziIsGay

REM --- Step 3: Install required Python packages ---
echo 📦 Installing Python dependencies...
pip install --upgrade pip
pip install apify-client
pip install python-dotenv
pip install tqdm
pip install requests
pip install pandas

REM --- Step 4: Completion message ---
echo =================================================
echo ✅ Environment setup complete!
echo ⚡ You can now run Scraper.py and Converter.py
echo =================================================
pause
