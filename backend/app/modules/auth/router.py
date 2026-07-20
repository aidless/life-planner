"""Auth API router: register, login, get current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth import schemas, services
from app.modules.auth.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.ApiResponse)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    if services.get_user_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被注册",
        )

    user = services.create_user(db, payload)
    token = services.create_access_token({"sub": str(user.id)})

    # W35: Auto-inject 30-day sample data so dashboard 12 dimensions
    # have meaningful values on day one.
    try:
        from scripts.init_user_data import init_sample_data
        init_sample_data(db, int(user.id))
    except Exception as e:
        # Don't fail registration on init error; log and continue.
        print(f"Warning: init_sample_data failed for user {user.id}: {e}")

    return schemas.ApiResponse(
        success=True,
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": schemas.UserResponse.model_validate(user).model_dump(),
        },
    )


@router.post("/login", response_model=schemas.ApiResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login and receive an access token."""
    user = services.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = services.create_access_token({"sub": str(user.id)})

    return schemas.ApiResponse(
        success=True,
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": schemas.UserResponse.model_validate(user).model_dump(),
        },
    )


@router.get("/me", response_model=schemas.ApiResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return schemas.ApiResponse(
        success=True,
        data=schemas.UserResponse.model_validate(current_user).model_dump(),
    )
