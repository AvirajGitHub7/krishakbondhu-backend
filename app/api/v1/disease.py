"""
KrishakBondhu - Disease Detection Routes
Endpoints for uploading leaf images and getting disease predictions.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.deps import get_current_user
from app.models.disease import (
    DiseaseDetectionResponse,
    DiseaseInfoResponse,
    PredictionHistoryResponse,
)
from app.services.disease_service import (
    detect_disease,
    get_prediction_history,
    get_disease_info,
)

router = APIRouter(prefix="/disease", tags=["Disease Detection"])


@router.post("/predict", response_model=DiseaseDetectionResponse)
async def predict(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a leaf image for disease detection.
    - Stores image in Cloudinary
    - Runs ML prediction using HuggingFace model
    - Returns disease name, confidence, symptoms, and remedy
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, etc.)",
        )

    try:
        result = await detect_disease(file, current_user["id"])
        return DiseaseDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease detection failed: {str(e)}",
        )


@router.get("/history", response_model=PredictionHistoryResponse)
async def history(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get the current user's prediction history."""
    result = await get_prediction_history(current_user["id"], page, page_size)
    return PredictionHistoryResponse(**result)


@router.get("/info/{disease_name}", response_model=DiseaseInfoResponse)
async def disease_info(
    disease_name: str,
    current_user: dict = Depends(get_current_user),
):
    """Get detailed disease information from the database."""
    info = await get_disease_info(disease_name)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease info not found for: {disease_name}",
        )
    return DiseaseInfoResponse(**info)
