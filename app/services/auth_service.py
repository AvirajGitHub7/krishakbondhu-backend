"""
KrishakBondhu - Auth Service
Business logic for user registration and authentication.
"""

from datetime import datetime, timezone

from bson import ObjectId

from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongodb import get_database
from app.models.user import UserResponse


async def register_user(name: str, email: str, password: str, phone: str = None, location: str = None) -> dict:
    """Register a new user. Returns the created user document."""
    db = get_database()

    # Check if email already exists
    existing = await db.users.find_one({"email": email})
    if existing:
        raise ValueError("A user with this email already exists")

    now = datetime.now(timezone.utc)
    user_doc = {
        "name": name,
        "email": email,
        "hashed_password": hash_password(password),
        "role": "user",
        "avatar_url": None,
        "phone": phone,
        "location": location,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc


async def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user by email and password. Returns user document or raises ValueError."""
    db = get_database()
    user = await db.users.find_one({"email": email})

    if not user or not verify_password(password, user["hashed_password"]):
        raise ValueError("Invalid email or password")

    return user


def create_token_for_user(user: dict) -> str:
    """Create a JWT token for the given user."""
    return create_access_token(data={"sub": str(user["_id"]), "role": user["role"]})


def user_to_response(user: dict) -> UserResponse:
    """Convert a MongoDB user document to a UserResponse schema."""
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        avatar_url=user.get("avatar_url"),
        phone=user.get("phone"),
        location=user.get("location"),
        created_at=user["created_at"],
    )


async def update_user_profile(user_id: str, update_data: dict) -> dict:
    """Update user profile fields."""
    db = get_database()
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    return await db.users.find_one({"_id": ObjectId(user_id)})
