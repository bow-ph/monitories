from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access forbidden",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if not isinstance(email, str):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise forbidden_exception
    return user

async def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to check if user is a superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )
    return current_user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_subscription_valid(user: User) -> bool:
    """Check if user's subscription is valid"""
    if not user.subscription_type:
        return False
    if not user.subscription_end_date:
        return False
    return user.subscription_end_date > datetime.utcnow()

def check_project_limit(user: User, db: Session) -> bool:
    """Check if user has reached their project limit"""
    from app.models.project import Project
    
    if user.subscription_type == "trial":
        project_count = db.query(Project).filter(Project.user_id == user.id).count()
        return project_count < 1
    elif user.subscription_type == "team":
        project_count = db.query(Project).filter(Project.user_id == user.id).count()
        return project_count < 10
    elif user.subscription_type == "enterprise":
        return True
    return False
