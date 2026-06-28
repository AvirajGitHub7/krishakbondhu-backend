"""
KrishakBondhu - Post Service
Business logic for community forum posts and comments.
"""

from datetime import datetime, timezone
from typing import Optional

import cloudinary
import cloudinary.uploader
from bson import ObjectId
from fastapi import UploadFile

from app.db.mongodb import get_database


async def upload_post_image(file: UploadFile) -> str:
    """Upload a post image to Cloudinary."""
    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder="krishakbondhu/posts",
        resource_type="image",
    )
    return result["secure_url"]


async def upload_post_image_base64(base64_data: str) -> str:
    """Upload a base64-encoded image to Cloudinary."""
    import base64

    # Handle data URI format (e.g., "data:image/jpeg;base64,/9j/4AAQ...")
    if "," in base64_data:
        base64_data = base64_data.split(",", 1)[1]

    image_bytes = base64.b64decode(base64_data)
    result = cloudinary.uploader.upload(
        image_bytes,
        folder="krishakbondhu/posts",
        resource_type="image",
    )
    return result["secure_url"]


async def create_post(
    author_id: str,
    title: str,
    description: str,
    image_url: Optional[str] = None,
    disease_result: Optional[dict] = None,
) -> dict:
    """Create a new community post."""
    db = get_database()
    now = datetime.now(timezone.utc)

    post_doc = {
        "author_id": ObjectId(author_id),
        "title": title,
        "description": description,
        "image_url": image_url,
        "disease_result": disease_result,
        "likes": [],
        "comment_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.posts.insert_one(post_doc)
    post_doc["_id"] = result.inserted_id
    return post_doc


async def get_posts(page: int = 1, page_size: int = 20) -> dict:
    """Get paginated posts with author info."""
    db = get_database()
    skip = (page - 1) * page_size

    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": page_size},
        {
            "$lookup": {
                "from": "users",
                "localField": "author_id",
                "foreignField": "_id",
                "as": "author",
            }
        },
        {"$unwind": "$author"},
    ]

    posts = []
    async for doc in db.posts.aggregate(pipeline):
        posts.append(_format_post(doc))

    total = await db.posts.count_documents({})
    return {"posts": posts, "total": total, "page": page, "page_size": page_size}


async def get_post_by_id(post_id: str) -> Optional[dict]:
    """Get a single post with author info."""
    db = get_database()

    pipeline = [
        {"$match": {"_id": ObjectId(post_id)}},
        {
            "$lookup": {
                "from": "users",
                "localField": "author_id",
                "foreignField": "_id",
                "as": "author",
            }
        },
        {"$unwind": "$author"},
    ]

    async for doc in db.posts.aggregate(pipeline):
        return _format_post(doc)
    return None


async def delete_post(post_id: str, user_id: str, is_admin: bool = False) -> bool:
    """Delete a post. Only the author or admin can delete."""
    db = get_database()
    post = await db.posts.find_one({"_id": ObjectId(post_id)})

    if not post:
        return False

    if not is_admin and str(post["author_id"]) != user_id:
        raise PermissionError("You can only delete your own posts")

    await db.posts.delete_one({"_id": ObjectId(post_id)})
    # Also delete associated comments
    await db.comments.delete_many({"post_id": ObjectId(post_id)})
    return True


async def toggle_like(post_id: str, user_id: str) -> dict:
    """Toggle like on a post. Returns updated like status."""
    db = get_database()
    user_oid = ObjectId(user_id)
    post = await db.posts.find_one({"_id": ObjectId(post_id)})

    if not post:
        raise ValueError("Post not found")

    likes = post.get("likes", [])
    if user_oid in likes:
        await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": user_oid}},
        )
        liked = False
    else:
        await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$addToSet": {"likes": user_oid}},
        )
        liked = True

    updated_post = await db.posts.find_one({"_id": ObjectId(post_id)})
    return {"liked": liked, "like_count": len(updated_post.get("likes", []))}


async def create_comment(post_id: str, author_id: str, content: str) -> dict:
    """Create a comment on a post."""
    db = get_database()
    now = datetime.now(timezone.utc)

    comment_doc = {
        "post_id": ObjectId(post_id),
        "author_id": ObjectId(author_id),
        "content": content,
        "created_at": now,
    }

    result = await db.comments.insert_one(comment_doc)
    comment_doc["_id"] = result.inserted_id

    # Increment comment count on the post
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {"comment_count": 1}},
    )

    return comment_doc


async def get_comments(post_id: str, page: int = 1, page_size: int = 50) -> list:
    """Get comments for a post with author info."""
    db = get_database()
    skip = (page - 1) * page_size

    pipeline = [
        {"$match": {"post_id": ObjectId(post_id)}},
        {"$sort": {"created_at": 1}},
        {"$skip": skip},
        {"$limit": page_size},
        {
            "$lookup": {
                "from": "users",
                "localField": "author_id",
                "foreignField": "_id",
                "as": "author",
            }
        },
        {"$unwind": "$author"},
    ]

    comments = []
    async for doc in db.comments.aggregate(pipeline):
        comments.append({
            "id": str(doc["_id"]),
            "post_id": str(doc["post_id"]),
            "author_id": str(doc["author_id"]),
            "author_name": doc["author"]["name"],
            "author_avatar": doc["author"].get("avatar_url"),
            "content": doc["content"],
            "created_at": doc["created_at"],
        })

    return comments


def _format_post(doc: dict) -> dict:
    """Format a post document with author info for response."""
    return {
        "id": str(doc["_id"]),
        "author_id": str(doc["author_id"]),
        "author_name": doc["author"]["name"],
        "author_avatar": doc["author"].get("avatar_url"),
        "title": doc["title"],
        "description": doc["description"],
        "image_url": doc.get("image_url"),
        "disease_result": doc.get("disease_result"),
        "likes": [str(lid) for lid in doc.get("likes", [])],
        "like_count": len(doc.get("likes", [])),
        "comment_count": doc.get("comment_count", 0),
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
    }
