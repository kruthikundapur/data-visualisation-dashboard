# Quick Start Guide

## 🚀 Fastest Way to Run

### Option 1: Docker (Recommended - All-in-One)
```bash
docker-compose up --build
```
Then open http://localhost:3000

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

## 📋 Testing Checklist

1. **Register** - Create account at http://localhost:3000/register
2. **Login** - Sign in with your credentials
3. **Upload** - Go to Datasets page, upload a CSV/Excel file
4. **View Data** - Click on dataset to see table
5. **Filter** - Use search/filters in table
6. **Charts** - Select chart type and generate visualization
7. **Sync** - Apply filters and watch charts update
8. **Theme** - Toggle dark/light mode

## ✅ Assignment Requirements Status

- ✅ User Signup/Signin
- ✅ Upload CSV/Excel files
- ✅ Parse and save to database
- ✅ Paginated, sortable, searchable table
- ✅ Dynamic charts (bar, line, pie)
- ✅ Synchronized filters
- ✅ ReactJS frontend
- ✅ FastAPI backend
- ✅ SQL database
- ✅ Backend data processing
- ✅ Light/Dark theme (bonus)
- ✅ Role-based access (bonus)

**Everything is ready! 🎉**

