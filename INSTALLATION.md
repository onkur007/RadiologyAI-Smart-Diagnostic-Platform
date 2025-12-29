# Installation and Setup Guide

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.9 or higher**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12 or higher**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** (optional): For cloning repositories
- **Google Gemini API Key**: [Get API Key](https://makersuite.google.com/app/apikey)

---

## 🚀 Step-by-Step Installation

### Step 1: PostgreSQL Setup

1. **Install PostgreSQL** on your system
2. **Create a database** for the application:

```sql
-- Open PostgreSQL command line (psql) or pgAdmin
CREATE DATABASE radiology_ai;

-- Create a user (optional, or use existing user)
CREATE USER radiology_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE radiology_ai TO radiology_user;
```

3. **Note your database credentials**:
   - Host: `localhost`
   - Port: `5432` (default)
   - Database: `radiology_ai`
   - Username: `radiology_user`
   - Password: `your_secure_password`

---

### Step 2: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (keep it secure!)

---

### Step 3: Project Setup

1. **Open Terminal/Command Prompt** and navigate to the project folder:

```bash
cd C:\Users\Sajjad\Documents\RadiologyAI
```

2. **Create a Python virtual environment**:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

3. **Install required packages**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all dependencies (FastAPI, SQLAlchemy, Gemini AI, etc.)

---

### Step 4: Environment Configuration

1. **Copy the example environment file**:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

2. **Edit the `.env` file** with your actual credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://radiology_user:your_secure_password@localhost:5432/radiology_ai

# Security (Generate a strong secret key)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Application Settings
DEBUG=True
APP_NAME=AI-Powered Radiology Assistant
VERSION=1.0.0

# File Upload Settings
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Important**: 
- Replace `your-gemini-api-key-here` with your actual Gemini API key
- Replace database credentials with your PostgreSQL setup
- Generate a strong SECRET_KEY (use: `openssl rand -hex 32` or any password generator)

---

### Step 5: Initialize Database

Run the initialization script to create tables and admin user:

```bash
python init_db.py
```

Follow the prompts to:
- Create database tables ✅
- Create admin user (choose username, email, password)
- Optionally create sample users for testing

Example:
```
Create admin user? (y/n): y
Enter admin username: admin
Enter admin email: admin@example.com
Enter admin full name: System Administrator
Enter admin password: ********
Confirm password: ********

Create sample users for testing? (y/n): y
```

---

### Step 6: Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Starting AI-Powered Radiology Assistant...
✅ Upload directory ready: uploads
✅ Database tables created/verified
INFO:     Application startup complete.
```

---

### Step 7: Access the Application

Open your web browser and go to:

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🧪 Testing the API

### Using Swagger UI (Recommended for Beginners)

1. Go to http://localhost:8000/docs
2. You'll see all available endpoints organized by category

#### Test Login:
1. Find **POST /auth/login** endpoint
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "your_admin_password"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from the response

#### Authorize:
1. Click the "Authorize" button at the top
2. Enter: `Bearer your_access_token_here`
3. Click "Authorize"
4. Now you can access protected endpoints!

---

## 📝 Sample API Workflows

### Workflow 1: Patient Uploads Image

1. **Register as Patient**:
   - Endpoint: `POST /auth/register`
   - Body:
     ```json
     {
       "email": "patient@example.com",
       "username": "patient1",
       "full_name": "John Doe",
       "password": "password123",
       "role": "patient"
     }
     ```

2. **Login**:
   - Endpoint: `POST /auth/login`
   - Get access token

3. **Upload Image**:
   - Endpoint: `POST /patients/upload-image`
   - Form data:
     - file: [select image file]
     - modality: "xray" / "ct" / "mri"
     - description: "Chest pain symptoms"

4. **Analyze Image**:
   - Endpoint: `POST /patients/scans/{scan_id}/analyze`
   - Get AI analysis results

5. **View Reports**:
   - Endpoint: `GET /patients/reports`

### Workflow 2: Doctor Reviews Patient

1. **Login as Doctor**
2. **View Patients**:
   - Endpoint: `GET /doctors/patients`

3. **View Patient Scans**:
   - Endpoint: `GET /doctors/patients/{patient_id}/scans`

4. **Generate Report**:
   - Endpoint: `POST /doctors/generate-report`

5. **Validate Report**:
   - Endpoint: `PUT /doctors/reports/{report_id}/validate`

---

## 🛠️ Troubleshooting

### Issue: "Module not found" errors
**Solution**: Make sure virtual environment is activated and packages are installed:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Database connection failed
**Solution**: 
- Check PostgreSQL is running
- Verify credentials in `.env` file
- Test connection: `psql -U radiology_user -d radiology_ai`

### Issue: "GEMINI_API_KEY not found"
**Solution**: 
- Make sure `.env` file exists
- Check API key is correctly set
- Restart the application after changing `.env`

### Issue: "Upload directory not found"
**Solution**: The app creates it automatically, but you can manually create:
```bash
mkdir uploads
```

---

## 📊 Database Management

### View Database Contents

```bash
# Connect to database
psql -U radiology_user -d radiology_ai

# List tables
\dt

# View users
SELECT id, username, email, role FROM users;

# Exit
\q
```

### Reset Database (Caution!)

```bash
# Drop and recreate database
psql -U postgres
DROP DATABASE radiology_ai;
CREATE DATABASE radiology_ai;
\q

# Run init script again
python init_db.py
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong SECRET_KEY** in production
3. **Change default passwords** immediately
4. **Use HTTPS** in production (not HTTP)
5. **Regularly update dependencies**: `pip install --upgrade -r requirements.txt`
6. **Set DEBUG=False** in production
7. **Implement rate limiting** for API endpoints

---

## 🚢 Deployment (Production)

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t radiology-ai .
docker run -p 8000:8000 radiology-ai
```

### Using Cloud Services

- **AWS**: Deploy on EC2 or ECS
- **Google Cloud**: Deploy on Cloud Run or Compute Engine
- **Heroku**: Use Heroku Postgres and deploy with `Procfile`
- **DigitalOcean**: Deploy on App Platform or Droplet

---

## 📞 Support

For issues:
1. Check this guide first
2. Review error messages in terminal
3. Check API documentation at `/docs`
4. Review log files
5. Create an issue in the project repository

---

## 🎓 Learning Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Tutorial**: https://docs.sqlalchemy.org/
- **PostgreSQL Guide**: https://www.postgresql.org/docs/
- **Gemini API Docs**: https://ai.google.dev/docs

---

**Congratulations! 🎉** Your AI-Powered Radiology Assistant is now ready to use!
