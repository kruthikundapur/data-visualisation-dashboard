# Data Visualization Dashboard

A comprehensive web-based data visualization platform built with React and FastAPI, allowing users to upload, analyze, and visualize data through interactive tables and charts.

## Features

### Core Features
- **User Authentication**: Secure signup and signin with JWT tokens
- **File Upload**: Support for CSV and Excel files (.csv, .xlsx, .xls)
- **Data Management**: Parse and store uploaded data in PostgreSQL database
- **Interactive Tables**: Paginated, sortable, and searchable data tables
- **Dynamic Charts**: Bar, Line, and Pie charts with customizable axes and aggregations
- **Synchronized Filters**: Filters applied to tables automatically update charts
- **Responsive Design**: Modern UI that works on desktop and mobile devices

### Bonus Features
- **Light/Dark Theme Toggle**: Switch between light and dark modes
- **Role-Based Access Control**: Admin and Member user roles
- **Real-time Filtering**: Server-side filtering and search for optimal performance

## Tech Stack

### Frontend
- **React 18** - UI framework
- **React Router** - Navigation
- **Chart.js** - Data visualization
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Vite** - Build tool

### Backend
- **FastAPI** - REST API framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Pandas** - Data processing
- **JWT** - Authentication
- **Bcrypt** - Password hashing

## Project Structure

```
data-visualization-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # Authentication utilities
│   │   ├── database.py      # Database configuration
│   │   └── utils.py          # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React contexts
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Or Node.js 18+ and Python 3.11+

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data-visualization-dashboard
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/data_dashboard
   SECRET_KEY=your-secret-key-change-in-production
   ```

5. **Start PostgreSQL database**
   ```bash
   # Using Docker
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=data_dashboard postgres:15-alpine
   ```

6. **Run database migrations**
   ```bash
   # The tables are auto-created on first run
   ```

7. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   Open http://localhost:3000 in your browser

## Usage

### 1. Create an Account
- Click "Sign up" on the login page
- Fill in your details (name, email, password, role)
- Role options: "Admin" or "Member"

### 2. Upload a Dataset
- Navigate to "Datasets" page
- Click "Upload Dataset"
- Enter dataset name and description
- Select a CSV or Excel file
- Click "Upload"

### 3. View and Analyze Data
- Click on a dataset card to view it
- Use the search bar to filter data across all columns
- Apply column-specific filters
- Sort columns by clicking on column headers
- Navigate through pages using pagination controls

### 4. Create Visualizations
- Select chart type (Bar, Line, or Pie)
- Choose X-axis column
- For Bar/Line charts, optionally select Y-axis and aggregation type
- Charts automatically update when filters change

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Datasets
- `GET /datasets` - Get all user's datasets
- `GET /datasets/{id}` - Get specific dataset
- `POST /datasets/upload` - Upload a new dataset

### Data
- `POST /data/filter` - Filter and paginate data
- `GET /data/columns/{dataset_id}` - Get dataset columns

### Charts
- `POST /charts/data` - Get chart data

## Sample Dataset

You can use any CSV or Excel file. Here's a sample dataset structure:

```csv
name,age,city,salary
John,25,New York,50000
Jane,30,San Francisco,60000
Bob,35,Chicago,55000
```

## Development

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production)

## Testing

To test the application:
1. Register a new account
2. Upload a sample CSV/Excel file
3. View the data in the table
4. Create visualizations with different chart types
5. Apply filters and see them sync between table and charts

## Deployment

For production deployment:
1. Update `SECRET_KEY` in backend environment
2. Use a production PostgreSQL database
3. Configure CORS settings in `backend/app/main.py`
4. Build frontend: `npm run build`
5. Serve static files with a production server

## License

This project is open source and available under the MIT License.

## Contributors

Built as a data visualization dashboard assignment demonstrating full-stack development capabilities.

