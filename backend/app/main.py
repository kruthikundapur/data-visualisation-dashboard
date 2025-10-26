from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict, cast, TYPE_CHECKING
import io
import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

from . import models, schemas
from .database import get_db, engine

if TYPE_CHECKING:
    # Provide pandas types to the type checker without importing at runtime.
    # This helps Pylance understand pandas symbols while we still lazily import
    # pandas at runtime where required.
    import pandas as pd  # type: ignore

# Create tables (safe: catch DB connection errors so the app can still start
# when a remote DB is not available during local development)
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    # Don't raise here — log for visibility and allow the app to start. A
    # missing / unreachable DB (for example when DATABASE_URL points to a
    # remote Postgres that isn't running) should not prevent the server from
    # starting during development.
    print(f"Warning: could not create DB tables at startup: {e}")

app = FastAPI(title="Data Visualization Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: Any) -> bool:
    # hashed_password may be reported as a Column by static checkers; cast at runtime
    return pwd_context.verify(plain_password, str(hashed_password))

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        user_id: Optional[int]
        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Accept either int or string subject
        if isinstance(user_id_raw, int):
            user_id = user_id_raw
        else:
            try:
                user_id = int(str(user_id_raw))
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Auth Routes
@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role or "member"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserResponse.model_validate(db_user)

@app.post("/auth/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)) -> schemas.Token:
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.id})
    return schemas.Token.model_validate({
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    })

# Dataset Routes
@app.post("/datasets/upload", response_model=schemas.DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
 ) -> schemas.DatasetResponse:
    # Validate file type (guard filename in case it's None)
    filename = file.filename or ""
    content_type = file.content_type or "application/octet-stream"
    if not filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel")
    
    try:
        # Lazy import pandas so server can start even if pandas isn't installed
        try:
            import pandas as pd
        except ImportError:
            raise HTTPException(status_code=500, detail="pandas is required to process uploaded files. Install pandas to enable file upload processing.")

        # Read file
        contents = await file.read()
        if filename.endswith('.csv'):
            # pandas signatures are complex and sometimes partially unknown to Pylance.
            # Suppress the specific unknown-member diagnostic on these calls.
            df: Any = pd.read_csv(io.BytesIO(contents))  # type: ignore[reportUnknownMemberType]
        else:
            df: Any = pd.read_excel(io.BytesIO(contents))  # type: ignore[reportUnknownMemberType]
        
        # Create dataset record
        dataset = models.Dataset(
            name=name,
            description=description,
            file_name=filename,
            file_size=len(contents),
            file_type=content_type,
            user_id=current_user.id
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        # Save data rows
        for _, row in df.iterrows():
            # Convert numpy types to Python native types
            row_data = {}
            for key, value in row.items():
                if pd.isna(value):
                    row_data[key] = None
                elif hasattr(value, 'item'):  # Convert numpy types
                    row_data[key] = value.item()
                else:
                    row_data[key] = value
            
            data_row = models.DataRow(
                dataset_id=dataset.id,
                row_data=row_data
            )
            db.add(data_row)
        
        db.commit()
        db.refresh(dataset)
        return schemas.DatasetResponse.model_validate(dataset)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/datasets", response_model=List[schemas.DatasetResponse])
def get_datasets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> List[schemas.DatasetResponse]:
    datasets: List[models.Dataset] = db.query(models.Dataset).filter(models.Dataset.user_id == current_user.id).all()
    return [schemas.DatasetResponse.model_validate(dataset) for dataset in datasets]

@app.get("/datasets/{dataset_id}", response_model=schemas.DatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> schemas.DatasetResponse:
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == dataset_id,
        models.Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return schemas.DatasetResponse.model_validate(dataset)

# Data Routes
@app.post("/data/filter", response_model=schemas.PaginatedResponse)
def filter_data(
    filter_request: schemas.FilterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> schemas.PaginatedResponse:
    # Verify dataset ownership
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == filter_request.dataset_id,
        models.Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Build query
    query = db.query(models.DataRow).filter(
        models.DataRow.dataset_id == filter_request.dataset_id
    )
    
    # Apply filters
    if filter_request.filters:
        for column, value in filter_request.filters.items():
            if value is not None and value != "":
                # Simple exact match filtering
                query = query.filter(models.DataRow.row_data[column].astext == str(value))
    
    # Get all matching rows for search processing
    all_rows: List[models.DataRow] = query.all()
    
    # Apply search if provided (server-side)
    if filter_request.search_term:
        search_lower = filter_request.search_term.lower()
        filtered_rows: List[models.DataRow] = []
        for row in all_rows:
            row_dict = row.row_data
            if any(
                search_lower in str(val).lower() 
                for val in row_dict.values() 
                if val is not None
            ):
                filtered_rows.append(row)
        total = len(filtered_rows)
    else:
        filtered_rows = all_rows
        total = len(filtered_rows)
    
    # Apply sorting
    if filter_request.sort_by:
        def sort_key(row: models.DataRow) -> str:
            value = row.row_data.get(filter_request.sort_by)
            if value is None:
                return ''
            return str(value).lower()
        
        reverse = filter_request.sort_order == "desc"
        filtered_rows = sorted(filtered_rows, key=sort_key, reverse=reverse)
    
    # Apply pagination
    start_idx = (filter_request.page - 1) * filter_request.page_size
    end_idx = start_idx + filter_request.page_size
    paginated_rows = filtered_rows[start_idx:end_idx]
    
    data: List[Dict[str, Any]] = [cast(Dict[str, Any], row.row_data) for row in paginated_rows]

    return schemas.PaginatedResponse.model_validate({
        "data": data,
        "total": total,
        "page": filter_request.page,
        "page_size": filter_request.page_size,
        "total_pages": (total + filter_request.page_size - 1) // filter_request.page_size
    })

@app.get("/data/columns/{dataset_id}")
def get_dataset_columns(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Dict[str, List[str]]:
    # Verify dataset ownership
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == dataset_id,
        models.Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Get first row to determine columns
    first_row = db.query(models.DataRow).filter(
        models.DataRow.dataset_id == dataset_id
    ).first()
    
    if not first_row:
        return {"columns": []}

    return {"columns": list(first_row.row_data.keys())}

@app.post("/charts/data", response_model=schemas.ChartDataResponse)
def get_chart_data(
    chart_request: schemas.ChartDataRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> schemas.ChartDataResponse:
    # Verify dataset ownership
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == chart_request.dataset_id,
        models.Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Get all data rows
    query = db.query(models.DataRow).filter(
        models.DataRow.dataset_id == chart_request.dataset_id
    )
    
    # Apply filters
    if chart_request.filters:
        for column, value in chart_request.filters.items():
            if value is not None and value != "":
                query = query.filter(models.DataRow.row_data[column].astext == str(value))
    
    rows: List[models.DataRow] = query.all()
    data: List[Dict[str, Any]] = [cast(Dict[str, Any], row.row_data) for row in rows]
    
    if not data:
        return schemas.ChartDataResponse.model_validate({
            "labels": [],
            "datasets": [],
            "chart_type": chart_request.chart_type
        })
    
    # Lazy import pandas for chart processing
    try:
        import pandas as pd
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas is required to generate chart data. Install pandas to enable chart processing.")

    df: Any = pd.DataFrame(data)
    
    # Process data based on chart type
    if chart_request.chart_type in ["bar", "line"]:
        if chart_request.y_axis and chart_request.y_axis in df.columns:
            # Convert y_axis to numeric if possible
            # Suppress partially-unknown signature warning from Pylance for to_numeric here.
            df[chart_request.y_axis] = pd.to_numeric(df[chart_request.y_axis], errors='coerce')  # type: ignore[reportUnknownMemberType]
            df = df.dropna(subset=[chart_request.y_axis])
            
            if chart_request.aggregation == "count":
                grouped = df.groupby(chart_request.x_axis)[chart_request.y_axis].count()
            elif chart_request.aggregation == "sum":
                grouped = df.groupby(chart_request.x_axis)[chart_request.y_axis].sum()
            elif chart_request.aggregation == "mean":
                grouped = df.groupby(chart_request.x_axis)[chart_request.y_axis].mean()
            else:
                grouped = df.groupby(chart_request.x_axis)[chart_request.y_axis].count()
        else:
            # Count occurrences if no y_axis specified
            grouped = df[chart_request.x_axis].value_counts().sort_index()
        
        labels = [str(x) for x in grouped.index.tolist()]
        values = [float(x) if isinstance(x, (int, float)) else x for x in grouped.values.tolist()]

        return schemas.ChartDataResponse.model_validate({
            "labels": labels,
            "datasets": [{
                "label": f"{chart_request.aggregation} of {chart_request.y_axis}" if chart_request.y_axis else "Count",
                "data": values,
                "backgroundColor": "rgba(54, 162, 235, 0.5)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }],
            "chart_type": chart_request.chart_type
        })
    
    elif chart_request.chart_type == "pie":
        if chart_request.x_axis in df.columns:
            counts = df[chart_request.x_axis].value_counts()
            labels = [str(x) for x in counts.index.tolist()]
            values = [float(x) if isinstance(x, (int, float)) else x for x in counts.values.tolist()]
        else:
            labels = []
            values = []

        return schemas.ChartDataResponse.model_validate({
            "labels": labels,
            "datasets": [{
                "data": values,
                "backgroundColor": [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(199, 199, 199, 0.5)',
                    'rgba(83, 102, 255, 0.5)',
                ]
            }],
            "chart_type": chart_request.chart_type
        })
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported chart type")

# Health check endpoint
@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Data Visualization Dashboard API is running"}

@app.get("/health")
def health_check() -> schemas.HealthCheck:
    return schemas.HealthCheck(status="healthy", timestamp=datetime.now(timezone.utc))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)