"""
KrishakBondhu - Post & Comment Models
Pydantic schemas for community forum posts and comments.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DiseaseResultEmbed(BaseModel):
    """Embedded disease result within a post (when sharing from detection)."""
    disease_name: Optional[str] = None
    confidence: Optional[float] = None
    symptoms: Optional[List[str]] = None
    remedy: Optional[str] = None


class PostCreate(BaseModel):
    """Request schema for creating a post."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    disease_result: Optional[DiseaseResultEmbed] = None
    image_base64: Optional[str] = None  # Base64-encoded image data


class PostResponse(BaseModel):
    """Response schema for a single post."""
    id: str
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    title: str
    description: str
    image_url: Optional[str] = None
    disease_result: Optional[DiseaseResultEmbed] = None
    likes: List[str] = []
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    """Paginated list of posts."""
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int


class CommentCreate(BaseModel):
    """Request schema for creating a comment."""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """Response schema for a single comment."""
    id: str
    post_id: str
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    content: str
    created_at: datetime
