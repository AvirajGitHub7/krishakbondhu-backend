"""
KrishakBondhu - Expert Service
Business logic for expert consultation requests.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from app.db.mongodb import get_database


async def create_expert_request(
    user_id: str,
    title: str,
    description: str,
    image_url: Optional[str] = None,
    disease_result: Optional[dict] = None,
) -> dict:
    """Create a new expert consultation request."""
    db = get_database()
    now = datetime.now(timezone.utc)

    request_doc = {
        "user_id": ObjectId(user_id),
        "title": title,
        "description": description,
        "image_url": image_url,
        "disease_result": disease_result,
        "status": "pending",
        "expert_id": None,
        "expert_response": None,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.expert_requests.insert_one(request_doc)
    request_doc["_id"] = result.inserted_id
    return request_doc


async def get_user_requests(user_id: str, page: int = 1, page_size: int = 20) -> dict:
    """Get a user's expert requests with pagination."""
    db = get_database()
    skip = (page - 1) * page_size

    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
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
        {"$unwind": "$user"},
        {
            "$lookup": {
                "from": "users",
                "localField": "expert_id",
                "foreignField": "_id",
                "as": "expert",
            }
        },
        {
            "$unwind": {
                "path": "$expert",
                "preserveNullAndEmptyArrays": True,
            }
        },
    ]

    requests = []
    async for doc in db.expert_requests.aggregate(pipeline):
        requests.append(_format_request(doc))

    total = await db.expert_requests.count_documents({"user_id": ObjectId(user_id)})
    return {"requests": requests, "total": total, "page": page, "page_size": page_size}


async def get_request_by_id(request_id: str) -> Optional[dict]:
    """Get a single expert request with user and expert info."""
    db = get_database()

    pipeline = [
        {"$match": {"_id": ObjectId(request_id)}},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user",
            }
        },
        {"$unwind": "$user"},
        {
            "$lookup": {
                "from": "users",
                "localField": "expert_id",
                "foreignField": "_id",
                "as": "expert",
            }
        },
        {
            "$unwind": {
                "path": "$expert",
                "preserveNullAndEmptyArrays": True,
            }
        },
    ]

    async for doc in db.expert_requests.aggregate(pipeline):
        return _format_request(doc)
    return None


async def get_pending_requests(page: int = 1, page_size: int = 20) -> dict:
    """Get all pending expert requests (for experts to view)."""
    db = get_database()
    skip = (page - 1) * page_size

    pipeline = [
        {"$match": {"status": "pending"}},
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
        {"$unwind": "$user"},
    ]

    requests = []
    async for doc in db.expert_requests.aggregate(pipeline):
        requests.append(_format_request(doc))

    total = await db.expert_requests.count_documents({"status": "pending"})
    return {"requests": requests, "total": total, "page": page, "page_size": page_size}


async def respond_to_request(request_id: str, expert_id: str, response: str) -> dict:
    """Expert responds to a request."""
    db = get_database()

    req = await db.expert_requests.find_one({"_id": ObjectId(request_id)})
    if not req:
        raise ValueError("Expert request not found")

    if req["status"] not in ("pending", "in_progress"):
        raise ValueError("This request has already been resolved or closed")

    now = datetime.now(timezone.utc)
    await db.expert_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "expert_id": ObjectId(expert_id),
                "expert_response": response,
                "status": "resolved",
                "updated_at": now,
            }
        },
    )

    return await get_request_by_id(request_id)


async def get_all_requests(page: int = 1, page_size: int = 20, status_filter: str = None) -> dict:
    """Get all expert requests (admin view) with optional status filter."""
    db = get_database()
    skip = (page - 1) * page_size

    match_filter = {}
    if status_filter:
        match_filter["status"] = status_filter

    pipeline = [
        {"$match": match_filter},
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
        {"$unwind": "$user"},
        {
            "$lookup": {
                "from": "users",
                "localField": "expert_id",
                "foreignField": "_id",
                "as": "expert",
            }
        },
        {
            "$unwind": {
                "path": "$expert",
                "preserveNullAndEmptyArrays": True,
            }
        },
    ]

    requests = []
    async for doc in db.expert_requests.aggregate(pipeline):
        requests.append(_format_request(doc))

    total = await db.expert_requests.count_documents(match_filter)
    return {"requests": requests, "total": total, "page": page, "page_size": page_size}


def _format_request(doc: dict) -> dict:
    """Format an expert request document for response."""
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "user_name": doc.get("user", {}).get("name", "Unknown"),
        "user_location": doc.get("user", {}).get("location"),
        "title": doc["title"],
        "description": doc["description"],
        "image_url": doc.get("image_url"),
        "disease_result": doc.get("disease_result"),
        "status": doc["status"],
        "expert_id": str(doc["expert_id"]) if doc.get("expert_id") else None,
        "expert_name": doc.get("expert", {}).get("name") if doc.get("expert") else None,
        "expert_response": doc.get("expert_response"),
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
    }

async def delete_request(request_id: str) -> bool:
    """Delete an expert request."""
    db = get_database()
    result = await db.expert_requests.delete_one({"_id": ObjectId(request_id)})
    return result.deleted_count > 0

