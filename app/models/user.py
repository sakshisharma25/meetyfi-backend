from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    organization: str
    is_manager: bool = False

class UserInDB(UserBase):
    hashed_password: str
    is_verified: bool = False
    profile_photo: Optional[str] = None
    manager_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_photo: Optional[str] = None
    manager_id: Optional[str] = None
    organization: Optional[str] = None