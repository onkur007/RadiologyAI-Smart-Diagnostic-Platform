# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites
- Python 3.9+
- PostgreSQL installed and running
- Gemini API key

## Quick Setup

### 1. Install Dependencies
```bash
cd RadiologyAI
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Setup Database
```sql
-- In PostgreSQL
CREATE DATABASE radiology_ai;
```

### 3. Configure Environment
Create `.env` file:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/radiology_ai
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run Application
```bash
uvicorn app.main:app --reload
```

### 6. Access API
Open: http://localhost:8000/docs

## Test Credentials
If you created sample users:
- **Patient**: `patient_demo` / `password123`
- **Doctor**: `doctor_demo` / `password123`

## Next Steps
1. Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
2. Check [API_GUIDE.md](API_GUIDE.md) for API usage
3. Explore API docs at `/docs`

## Common Issues

**Can't connect to database?**
- Check PostgreSQL is running
- Verify credentials in `.env`

**Import errors?**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**"GEMINI_API_KEY not found"?**
- Create `.env` file from `.env.example`
- Add your Gemini API key

Need help? Check INSTALLATION.md for detailed troubleshooting.
