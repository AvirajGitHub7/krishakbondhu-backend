"""
KrishakBondhu - Admin Routes
Endpoints for admin management of users, posts, and expert requests.
"""

from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import require_role
from app.db.mongodb import get_database
from app.models.user import UserResponse, UserRoleUpdate
from app.services.auth_service import user_to_response
from app.services.expert_service import get_all_requests, delete_request
from app.services.post_service import delete_post, get_posts

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(require_role(["admin"])),
):
    """Get dashboard statistics."""
    db = get_database()

    total_users = await db.users.count_documents({})
    total_posts = await db.posts.count_documents({})
    total_expert_requests = await db.expert_requests.count_documents({})
    pending_requests = await db.expert_requests.count_documents({"status": "pending"})
    total_predictions = await db.prediction_history.count_documents({})

    # Role breakdown
    user_count = await db.users.count_documents({"role": "user"})
    expert_count = await db.users.count_documents({"role": "expert"})
    admin_count = await db.users.count_documents({"role": "admin"})

    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_expert_requests": total_expert_requests,
        "pending_requests": pending_requests,
        "total_predictions": total_predictions,
        "role_breakdown": {
            "users": user_count,
            "experts": expert_count,
            "admins": admin_count,
        },
    }


@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_user: dict = Depends(require_role(["admin"])),
):
    """List all users with optional search and role filter."""
    db = get_database()
    skip = (page - 1) * page_size

    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]
    if role:
        query["role"] = role

    cursor = db.users.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    users = []
    async for user in cursor:
        users.append(user_to_response(user).model_dump())

    total = await db.users.count_documents(query)
    return {"users": users, "total": total, "page": page, "page_size": page_size}


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: str,
    data: UserRoleUpdate,
    current_user: dict = Depends(require_role(["admin"])),
):
    """Change a user's role (user, expert, admin)."""
    db = get_database()

    # Prevent self-demotion
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": data.role}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return user_to_response(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_role(["admin"])),
):
    """Delete a user account."""
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db = get_database()
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/posts")
async def list_all_posts(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(require_role(["admin"])),
):
    """List all posts (admin view)."""
    return await get_posts(page, page_size)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_post(
    post_id: str,
    current_user: dict = Depends(require_role(["admin"])),
):
    """Delete any post (admin only)."""
    deleted = await delete_post(post_id, current_user["id"], is_admin=True)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.get("/expert-requests")
async def list_all_expert_requests(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(require_role(["admin"])),
):
    """List all expert requests (admin view)."""
    return await get_all_requests(page, page_size, status_filter)


@router.delete("/expert-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_expert_request(
    request_id: str,
    current_user: dict = Depends(require_role(["admin"])),
):
    """Delete any expert request (admin only)."""
    deleted = await delete_request(request_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")



@router.get("/predictions")
async def list_all_predictions(
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(require_role(["admin"])),
):
    """List all global predictions (admin view)."""
    db = get_database()
    skip = (page - 1) * page_size

    # Use aggregation pipeline to join with users collection
    pred_pipeline = [
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": page_size},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user",
            }
        },
        {
            "$unwind": {
                "path": "$user",
                "preserveNullAndEmptyArrays": True,
            }
        },
    ]

    predictions = []
    async for doc in db.prediction_history.aggregate(pred_pipeline):
        predictions.append({
            "id": str(doc["_id"]),
            "user_id": str(doc["user_id"]),
            "user_name": doc.get("user", {}).get("name", "Unknown"),
            "user_location": doc.get("user", {}).get("location"),
            "disease_name": doc["disease_name"],
            "confidence": doc["confidence"],
            "image_url": doc["image_url"],
            "created_at": doc["created_at"].isoformat() if "created_at" in doc else None,
        })

    total = await db.prediction_history.count_documents({})
    
    # Get aggregated stats for the top 5 diseases
    pipeline = [
        {"$group": {"_id": "$disease_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_diseases_cursor = db.prediction_history.aggregate(pipeline)
    top_diseases = []
    async for doc in top_diseases_cursor:
        top_diseases.append({"disease_name": doc["_id"], "count": doc["count"]})

    return {
        "predictions": predictions, 
        "total": total, 
        "page": page, 
        "page_size": page_size,
        "top_diseases": top_diseases
    }
