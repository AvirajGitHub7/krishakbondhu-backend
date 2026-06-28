"""
KrishakBondhu - Auth Routes
Endpoints for user registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_token_for_user,
    user_to_response,
    update_user_profile,
)
from app.services.post_service import upload_post_image_base64

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    """Register a new user and return JWT token."""
    try:
        user = await register_user(
            name=data.name,
            email=data.email,
            password=data.password,
            phone=data.phone,
            location=data.location,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    token = create_token_for_user(user)
    return TokenResponse(
        access_token=token,
        user=user_to_response(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login with email and password, returns JWT token."""
    try:
        user = await authenticate_user(email=data.email, password=data.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_token_for_user(user)
    return TokenResponse(
        access_token=token,
        user=user_to_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the current user's profile."""
    return user_to_response(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update the current user's profile."""
    update_data = data.model_dump(exclude_unset=True)
    
    # Handle avatar upload if provided
    if "avatar_base64" in update_data:
        base64_data = update_data.pop("avatar_base64")
        if base64_data:
            image_url = await upload_post_image_base64(base64_data)
            update_data["avatar_url"] = image_url

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated_user = await update_user_profile(current_user["id"], update_data)
    return user_to_response(updated_user)
