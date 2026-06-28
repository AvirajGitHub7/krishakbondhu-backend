"""
KrishakBondhu - Disease Models
Pydantic schemas for disease detection and disease info.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DiseaseDetectionResponse(BaseModel):
    """Response schema for disease detection prediction."""
    disease_name: str
    confidence: float
    plant: Optional[str] = None
    symptoms: List[str] = []
    remedy: Optional[str] = None
    prevention: Optional[str] = None
    image_url: str


class DiseaseInfoResponse(BaseModel):
    """Response schema for disease info from database."""
    id: str
    disease_name: str
    plant: str
    symptoms: List[str]
    remedy: str
    prevention: str
    image_url: Optional[str] = None
    created_at: datetime


class PredictionHistoryItem(BaseModel):
    """Schema for a prediction history entry."""
    id: str
    disease_name: str
    confidence: float
    image_url: str
    created_at: datetime


class PredictionHistoryResponse(BaseModel):
    """Paginated prediction history."""
    predictions: List[PredictionHistoryItem]
    total: int
