from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ....core.security import create_access_token, verify_password, get_password_hash
from ....models.user import UserInDB, UserBase
from ....db.mongodb import get_database
from datetime import timedelta
from ....config import get_settings
from email_validator import validate_email, EmailNotValidError
import random
from ....core.email_utils import send_verification_email

router = APIRouter()
settings = get_settings()

@router.post("/signup")
async def signup(user: UserBase):
    db = await get_database()
    
    # Check if email exists
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    
    # Create user
    user_dict = user.dict()
    user_dict["verification_code"] = otp
    user_dict["is_verified"] = False
    
    await db.users.insert_one(user_dict)
    
    # Send verification email
    await send_verification_email(user.email, otp)
    
    return {"message": "Signup successful. Please verify your email."}

@router.post("/verify-email")
async def verify_email(email: str, otp: str):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user["verification_code"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    await db.users.update_one(
        {"email": email},
        {"$set": {"is_verified": True}}
    )
    
    return {"message": "Email verified successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = await get_database()
    user = await db.users.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    if not user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

