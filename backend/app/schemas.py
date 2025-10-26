from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "member"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    file_name: str
    file_size: int
    file_type: str

class DatasetResponse(DatasetBase):
    id: int
    user_id: int
    file_name: str
    file_size: int
    file_type: str
    created_at: datetime
    updated_at: datetime
    row_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)

class DataRowBase(BaseModel):
    row_data: Dict[str, Any]

class DataRowCreate(DataRowBase):
    dataset_id: int

class DataRowResponse(DataRowBase):
    id: int
    dataset_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FilterRequest(BaseModel):
    dataset_id: int
    filters: Optional[Dict[str, Any]] = {}
    search_term: Optional[str] = None
    page: int = 1
    page_size: int = 50
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"

class PaginatedResponse(BaseModel):
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int

class ChartDataRequest(BaseModel):
    dataset_id: int
    chart_type: str
    x_axis: str
    y_axis: Optional[str] = None
    aggregation: Optional[str] = "count"
    filters: Optional[Dict[str, Any]] = {}

class ChartDataset(BaseModel):
    label: str
    data: List[Union[int, float]]
    backgroundColor: Optional[str] = None
    borderColor: Optional[str] = None
    borderWidth: Optional[int] = None

class ChartDataResponse(BaseModel):
    labels: List[str]
    datasets: List[ChartDataset]
    chart_type: str

class DatasetStats(BaseModel):
    total_rows: int
    columns: List[str]
    column_types: Dict[str, str]
    created_at: datetime
    file_size: str

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    dataset_count: int
    
    model_config = ConfigDict(from_attributes=True)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class MessageResponse(BaseModel):
    message: str
    success: bool

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

# Additional schemas for advanced features
class ColumnAnalysis(BaseModel):
    column_name: str
    data_type: str
    unique_count: int
    null_count: int
    sample_values: List[Any]

class DatasetAnalysis(BaseModel):
    dataset_id: int
    total_rows: int
    total_columns: int
    columns: List[ColumnAnalysis]
    memory_usage: str
