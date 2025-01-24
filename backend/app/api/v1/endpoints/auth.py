from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import (
    get_password_hash,
    create_access_token,
    get_current_active_user,
    verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Register new user"""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        subscription_type="trial",  # Default to trial
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email
    from app.services.email_service import EmailService
    email_service = EmailService()
    email_service.send_welcome_email(db_user.email, db_user.email)
    
    return db_user

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/test-token", response_model=UserSchema)
def test_token(current_user: User = Depends(get_current_active_user)) -> Any:
    """Test access token"""
    return current_user

@router.post("/reset-password/{email}")
def reset_password(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """Send password reset email"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system",
        )
    from app.services.email_service import EmailService
    email_service = EmailService()
    
    # Generate reset token
    reset_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(hours=24)
    )
    
    # Send reset email
    if email_service.send_password_reset_email(user.email, reset_token):
        return {"msg": "Password reset email sent"}
    raise HTTPException(status_code=500, detail="Failed to send reset email")
