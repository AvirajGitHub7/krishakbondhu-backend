"""
KrishakBondhu - Posts Routes
Endpoints for community forum posts and comments.
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File

from app.core.deps import get_current_user
from app.models.post import (
    CommentCreate,
    CommentResponse,
    PostListResponse,
    PostResponse,
)
from app.services.post_service import (
    create_comment,
    create_post,
    delete_post,
    get_comments,
    get_post_by_id,
    get_posts,
    toggle_like,
    upload_post_image,
)

router = APIRouter(prefix="/posts", tags=["Community Forum"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    title: str = Form(..., min_length=3, max_length=200),
    description: str = Form(..., min_length=10, max_length=5000),
    disease_result: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    """Create a new community post with optional image file."""
    image_url = None
    if image:
        image_url = await upload_post_image(image)

    disease_data = None
    if disease_result:
        try:
            disease_data = json.loads(disease_result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid disease_result JSON")

    post = await create_post(
        author_id=current_user["id"],
        title=title,
        description=description,
        image_url=image_url,
        disease_result=disease_data,
    )

    return await get_post_by_id(str(post["_id"]))


@router.get("/", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get paginated community feed."""
    result = await get_posts(page, page_size)
    return PostListResponse(**result)


@router.get("/{post_id}", response_model=PostResponse)
async def get_single_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single post by ID."""
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return PostResponse(**post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a post. Only the author or admin can delete."""
    is_admin = current_user.get("role") == "admin"
    try:
        deleted = await delete_post(post_id, current_user["id"], is_admin)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Toggle like on a post."""
    try:
        result = await toggle_like(post_id, current_user["id"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: str,
    data: CommentCreate,
    current_user: dict = Depends(get_current_user),
):
    """Add a comment to a post."""
    # Verify post exists
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = await create_comment(post_id, current_user["id"], data.content)
    return CommentResponse(
        id=str(comment["_id"]),
        post_id=post_id,
        author_id=current_user["id"],
        author_name=current_user["name"],
        author_avatar=current_user.get("avatar_url"),
        content=data.content,
        created_at=comment["created_at"],
    )


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    post_id: str,
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """Get comments for a post."""
    comments = await get_comments(post_id, page, page_size)
    return [CommentResponse(**c) for c in comments]
