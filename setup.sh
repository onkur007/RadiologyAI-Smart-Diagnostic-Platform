#!/bin/bash
# Quick setup script for Linux/Mac
# Run with: bash setup.sh

echo "========================================"
echo "AI-Powered Radiology Assistant"
echo "Quick Setup Script for Linux/Mac"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python is installed"
python3 --version
echo ""

# Check if PostgreSQL is accessible
if ! command -v psql &> /dev/null; then
    echo "[WARNING] PostgreSQL command line tools not found"
    echo "Make sure PostgreSQL is installed"
    echo ""
fi

echo "Step 1: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "[INFO] Virtual environment already exists"
else
    python3 -m venv venv
    echo "[OK] Virtual environment created"
fi
echo ""

echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "[OK] Virtual environment activated"
echo ""

echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi
echo "[OK] Dependencies installed"
echo ""

echo "Step 4: Checking configuration..."
if [ -f ".env" ]; then
    echo "[OK] .env file exists"
else
    echo "[INFO] Creating .env file from template..."
    cp .env.example .env
    echo "[WARNING] Please edit .env file with your credentials:"
    echo "  - DATABASE_URL"
    echo "  - SECRET_KEY"
    echo "  - GEMINI_API_KEY"
    echo ""
    read -p "Open .env file now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
fi
echo ""

echo "Step 5: Database setup..."
read -p "Would you like to initialize the database now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python init_db.py
fi
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Make sure PostgreSQL is running"
echo "2. Update .env file with your credentials"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Open: http://localhost:8000/docs"
echo ""
echo "Quick commands:"
echo "  - Start app: uvicorn app.main:app --reload"
echo "  - Run tests: pytest tests/"
echo "  - Init DB: python init_db.py"
echo ""
echo "Documentation:"
echo "  - Quick Start: QUICKSTART.md"
echo "  - Installation: INSTALLATION.md"
echo "  - Beginners: BEGINNERS_GUIDE.md"
echo ""
