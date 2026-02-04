from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_active_user, verify_password, get_password_hash
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    if user_update.email and user_update.email != current_user.email:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update.email
    
    if user_update.username and user_update.username != current_user.username:
        existing = db.query(User).filter(User.username == user_update.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already in use")
        current_user.username = user_update.username
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's password"""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account"""
    db.delete(current_user)
    db.commit()
    return None
