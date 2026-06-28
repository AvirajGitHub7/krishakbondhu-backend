"""
KrishakBondhu - Expert Request Models
Pydantic schemas for expert consultation requests.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DiseaseResultBrief(BaseModel):
    """Brief disease result attached to an expert request."""
    disease_name: Optional[str] = None
    confidence: Optional[float] = None


class ExpertRequestCreate(BaseModel):
    """Request schema for creating an expert consultation request."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    disease_result: Optional[DiseaseResultBrief] = None


class ExpertResponseSubmit(BaseModel):
    """Request schema for an expert to respond."""
    response: str = Field(..., min_length=10, max_length=10000)


class ExpertRequestResponse(BaseModel):
    """Response schema for an expert request."""
    id: str
    user_id: str
    user_name: str
    title: str
    description: str
    image_url: Optional[str] = None
    disease_result: Optional[DiseaseResultBrief] = None
    status: str
    expert_id: Optional[str] = None
    expert_name: Optional[str] = None
    expert_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExpertRequestListResponse(BaseModel):
    """Paginated list of expert requests."""
    requests: List[ExpertRequestResponse]
    total: int
    page: int
    page_size: int
