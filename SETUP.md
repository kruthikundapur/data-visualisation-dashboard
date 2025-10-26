# Setup Guide

## Quick Start

### Option 1: Docker Compose (Recommended)

1. Make sure Docker and Docker Compose are installed
2. Run:
   ```bash
   docker-compose up --build
   ```
3. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file (optional, defaults to SQLite):
   ```env
   DATABASE_URL=sqlite:///./data_dashboard.db
   SECRET_KEY=your-secret-key-change-in-production
   ```

5. Start backend:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start frontend:
   ```bash
   npm run dev
   ```

4. Open http://localhost:3000

## Features Implemented

✅ User authentication (Signup/Login) with JWT
✅ File upload (CSV, Excel)
✅ Database storage with proper schema
✅ Paginated, sortable, searchable tables
✅ Dynamic charts (Bar, Line, Pie)
✅ Synchronized filters between table and charts
✅ Light/Dark theme toggle
✅ Role-based access control (Admin/Member)
✅ Responsive design
✅ Server-side data processing

## Testing the Application

1. Register a new account at http://localhost:3000/register
2. Login with your credentials
3. Upload a CSV or Excel file from the Datasets page
4. View your data in an interactive table
5. Create visualizations with different chart types
6. Apply filters and see them sync between table and charts
7. Toggle between light and dark themes

## Troubleshooting

### Backend Issues
- Make sure port 8000 is not in use
- Check database connection string in `.env`
- Ensure all Python dependencies are installed

### Frontend Issues
- Make sure port 3000 is not in use
- Clear browser cache if UI doesn't update
- Check browser console for errors

### Database Issues
- SQLite database will be created automatically
- For PostgreSQL, ensure the database exists and connection string is correct

