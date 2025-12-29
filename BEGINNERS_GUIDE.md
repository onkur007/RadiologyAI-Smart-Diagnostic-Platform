# Beginner's Guide to AI-Powered Radiology Assistant

Welcome! This guide will help you understand and use the AI-Powered Radiology Assistant, even if you're new to programming.

---

## 📚 Table of Contents

1. [What is this project?](#what-is-this-project)
2. [Understanding the basics](#understanding-the-basics)
3. [Installation walkthrough](#installation-walkthrough)
4. [Using the application](#using-the-application)
5. [Common scenarios](#common-scenarios)
6. [Troubleshooting](#troubleshooting)
7. [Learning resources](#learning-resources)

---

## What is this project?

The AI-Powered Radiology Assistant is a web application that helps doctors and patients manage medical imaging (X-rays, CT scans, MRI) with AI assistance.

### Key Features:
- 📤 **Upload medical images** (X-ray, CT, MRI)
- 🤖 **AI analyzes images** and detects abnormalities
- 📄 **Generates medical reports** automatically
- 💬 **Chat with AI** about medical questions
- 👥 **Role-based access**: Patients, Doctors, and Admins

### Important Note:
⚠️ This is an **AI-assisted** system, NOT a replacement for medical professionals. All AI outputs must be validated by qualified doctors.

---

## Understanding the Basics

### What is an API?
An **API** (Application Programming Interface) is like a waiter in a restaurant:
- You (the client) make a request (order food)
- The waiter (API) takes it to the kitchen (server)
- The kitchen prepares your order (processes data)
- The waiter brings back your food (returns response)

### Key Technologies Used:

1. **Python**: Programming language (like English for computers)
2. **FastAPI**: Framework to build web APIs quickly
3. **PostgreSQL**: Database to store information (like a digital filing cabinet)
4. **Gemini AI**: Google's AI that analyzes images and generates text
5. **JWT Tokens**: Digital keys for secure access

### Project Components:

```
🏠 Your Computer
├── 💾 Database (PostgreSQL) - Stores user data, reports
├── 🐍 Python Application (FastAPI) - Handles requests
├── 🤖 AI Service (Gemini) - Analyzes images
└── 📁 File Storage - Stores uploaded images
```

---

## Installation Walkthrough

### Step 1: Install Required Software

#### A. Install Python
1. Go to https://www.python.org/downloads/
2. Download Python 3.9 or higher
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   ```
   You should see something like: `Python 3.9.x`

#### B. Install PostgreSQL
1. Go to https://www.postgresql.org/download/
2. Download and install PostgreSQL
3. During installation:
   - Set a password (remember this!)
   - Keep default port: 5432
   - Remember your username (usually 'postgres')

#### C. Get Gemini API Key
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and save the key somewhere safe

### Step 2: Set Up the Project

#### A. Open Command Prompt (Windows)
1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Navigate to your project folder:
   ```bash
   cd C:\Users\Sajjad\Documents\RadiologyAI
   ```

#### B. Create Virtual Environment
A virtual environment is like a separate workspace for your project.

```bash
python -m venv venv
```

#### C. Activate Virtual Environment
```bash
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

#### D. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs all necessary Python packages. It may take a few minutes.

### Step 3: Configure Database

#### A. Create Database
1. Open pgAdmin (comes with PostgreSQL) or use command line:
   ```bash
   psql -U postgres
   ```
2. Enter your PostgreSQL password
3. Create database:
   ```sql
   CREATE DATABASE radiology_ai;
   ```
4. Exit:
   ```sql
   \q
   ```

#### B. Configure Environment Variables
1. Copy the example file:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` file in Notepad
3. Update these lines:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/radiology_ai
   SECRET_KEY=your-random-secret-key-here
   GEMINI_API_KEY=your-actual-gemini-api-key
   ```

Replace:
- `YOUR_PASSWORD`: Your PostgreSQL password
- `your-random-secret-key-here`: Any long random string (e.g., generate one at random.org)
- `your-actual-gemini-api-key`: The Gemini API key you got earlier

4. Save and close the file

### Step 4: Initialize Database

Run the setup script:
```bash
python init_db.py
```

Follow the prompts:
1. Create tables: `y`
2. Create admin user: `y`
   - Enter username: `admin`
   - Enter email: `admin@example.com`
   - Enter full name: `Admin User`
   - Enter password: (choose a secure password)
3. Create sample users: `y` (for testing)

### Step 5: Run the Application

```bash
uvicorn app.main:app --reload
```

You should see:
```
🚀 Starting AI-Powered Radiology Assistant...
✅ Upload directory ready: uploads
✅ Database tables created/verified
INFO:     Uvicorn running on http://127.0.0.1:8000
```

🎉 **Congratulations!** Your application is now running!

---

## Using the Application

### Accessing the API Documentation

1. Open your web browser
2. Go to: http://localhost:8000/docs
3. You'll see the **Swagger UI** - an interactive API documentation

### Understanding Swagger UI

Swagger UI lets you test the API directly from your browser:

- **Green**: GET requests (retrieve data)
- **Blue**: POST requests (send/create data)
- **Orange**: PUT requests (update data)
- **Red**: DELETE requests (delete data)

### Your First API Request

#### 1. Test the Welcome Endpoint
1. Find **GET /** in the docs
2. Click on it to expand
3. Click "Try it out"
4. Click "Execute"
5. See the response below!

#### 2. Register a Patient Account
1. Find **POST /auth/register**
2. Click "Try it out"
3. Modify the JSON:
   ```json
   {
     "email": "patient1@example.com",
     "username": "patient1",
     "full_name": "John Doe",
     "password": "password123",
     "role": "patient"
   }
   ```
4. Click "Execute"
5. If successful, you'll see status code `201 Created`

#### 3. Login
1. Find **POST /auth/login**
2. Click "Try it out"
3. Enter:
   - username: `patient1`
   - password: `password123`
4. Click "Execute"
5. Copy the `access_token` from the response

#### 4. Authorize Your Session
1. Click the green **"Authorize"** button at the top
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
   (Replace YOUR_ACCESS_TOKEN with the token you copied)
3. Click "Authorize"
4. Click "Close"

Now you can access protected endpoints!

#### 5. Get Your Profile
1. Find **GET /patients/me**
2. Click "Try it out"
3. Click "Execute"
4. See your profile information!

---

## Common Scenarios

### Scenario 1: Patient Uploads an X-Ray

1. **Login as patient** (get token)
2. **Upload image**:
   - Endpoint: `POST /patients/upload-image`
   - Click "Try it out"
   - Click "Choose File" and select an X-ray image
   - Select modality: `xray`
   - Add description: "Chest X-ray for persistent cough"
   - Click "Execute"
   - Note the `scan_id` from response

3. **Request AI analysis**:
   - Endpoint: `POST /patients/scans/{scan_id}/analyze`
   - Replace `{scan_id}` with your scan ID
   - Click "Execute"
   - View AI analysis results!

4. **View all reports**:
   - Endpoint: `GET /patients/reports`
   - Click "Execute"

### Scenario 2: Doctor Reviews Patient

1. **Login as doctor**:
   - Username: `doctor_demo`
   - Password: `password123`
   - Get token and authorize

2. **View patients**:
   - Endpoint: `GET /doctors/patients`
   - Click "Execute"
   - See list of patients

3. **View patient's scans**:
   - Endpoint: `GET /doctors/patients/{patient_id}/scans`
   - Enter patient ID
   - Click "Execute"

4. **Generate report**:
   - Endpoint: `POST /doctors/generate-report`
   - Body:
     ```json
     {
       "patient_id": 1,
       "scan_id": 1,
       "report_type": "AI Generated"
     }
     ```
   - Click "Execute"
   - AI generates comprehensive report

5. **Validate report**:
   - Endpoint: `PUT /doctors/reports/{report_id}/validate`
   - Add doctor notes and validation
   - Change status to "validated"

### Scenario 3: Chat with AI

1. **Start chat**:
   - Endpoint: `POST /ai/chat`
   - Body:
     ```json
     {
       "message": "What does opacity in lungs mean?",
       "session_id": null
     }
     ```
   - Click "Execute"
   - Get AI response and `session_id`

2. **Continue conversation**:
   - Use same endpoint
   - Include `session_id` from previous response
   - AI remembers conversation context!

### Scenario 4: Admin Manages Users

1. **Login as admin**
2. **View all users**:
   - Endpoint: `GET /admin/users`

3. **Update user role**:
   - Endpoint: `PUT /admin/users/{user_id}/role`
   - Change patient to doctor, etc.

4. **View system statistics**:
   - Endpoint: `GET /admin/system-stats`
   - See total users, scans, reports, etc.

---

## Troubleshooting

### Problem: "Module not found" error
**Solution**:
```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Problem: "Connection refused" to database
**Solutions**:
1. Check PostgreSQL is running:
   - Windows: Open Services, find "PostgreSQL", make sure it's running
2. Verify database exists:
   ```bash
   psql -U postgres -l
   ```
3. Check `.env` file has correct credentials

### Problem: Can't access http://localhost:8000
**Solutions**:
1. Check if app is running (should see "Uvicorn running" message)
2. Try http://127.0.0.1:8000 instead
3. Check if another program is using port 8000
4. Try different port:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

### Problem: "Unauthorized" error
**Solutions**:
1. Make sure you logged in and got a token
2. Click "Authorize" button and enter token
3. Token format must be: `Bearer YOUR_TOKEN`
4. Token expires after 30 minutes - login again

### Problem: Image upload fails
**Solutions**:
1. Check file size (max 10MB)
2. Only JPG, JPEG, PNG allowed
3. Make sure `uploads` folder exists
4. Check disk space

### Problem: AI analysis fails
**Solutions**:
1. Verify Gemini API key in `.env`
2. Check internet connection
3. Verify API key is valid at Google AI Studio
4. Check for API quota limits

---

## Learning Resources

### Understanding APIs
- [What is an API?](https://www.youtube.com/watch?v=s7wmiS2mSXY) (Video)
- [REST API Tutorial](https://restfulapi.net/)

### Python Basics
- [Python for Beginners](https://www.python.org/about/gettingstarted/)
- [Python Tutorial](https://www.w3schools.com/python/)

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

### Databases
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [SQL Basics](https://www.w3schools.com/sql/)

### AI & Machine Learning
- [AI for Everyone](https://www.coursera.org/learn/ai-for-everyone)
- [Google AI Documentation](https://ai.google.dev/)

---

## Next Steps

1. ✅ **Experiment**: Try all the endpoints in Swagger UI
2. ✅ **Read code**: Look at files in `app/routers/` to understand how endpoints work
3. ✅ **Modify**: Try changing small things and see what happens
4. ✅ **Build**: Add your own features!
5. ✅ **Learn**: Follow the learning resources above

---

## Getting Help

1. **Read documentation**:
   - README.md - Project overview
   - INSTALLATION.md - Setup details
   - API_GUIDE.md - API reference
   - PROJECT_STRUCTURE.md - Code organization

2. **Check error messages**: They usually tell you what's wrong

3. **Google it**: Copy error message and search

4. **Ask for help**: Reach out to the community

---

## Key Concepts Summary

### API Request Flow:
```
1. User makes request → 2. Check authentication → 
3. Validate data → 4. Process in database/AI → 
5. Return response
```

### User Roles:
- **Patient**: Upload scans, view own reports
- **Doctor**: Review all patients, validate reports
- **Admin**: Manage users, monitor system

### Important Files:
- `.env` - Configuration (NEVER commit to git!)
- `app/main.py` - Application entry point
- `app/routers/` - API endpoints
- `app/models/` - Database structure
- `init_db.py` - Database setup

### Commands to Remember:
```bash
# Activate environment
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload

# Initialize database
python init_db.py

# Run tests
pytest tests/
```

---

## Congratulations! 🎉

You now have a working AI-powered radiology assistant and understand how to use it. Keep experimenting and learning!

**Remember**: Practice makes perfect. Don't be afraid to make mistakes - that's how you learn!

Happy coding! 🚀
