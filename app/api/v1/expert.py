"""
KrishakBondhu - Expert Routes
Endpoints for expert consultation requests and responses.
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.deps import get_current_user, require_role
from app.models.expert import (
    ExpertRequestResponse,
    ExpertRequestListResponse,
    ExpertResponseSubmit,
)
from app.services.expert_service import (
    create_expert_request,
    get_user_requests,
    get_request_by_id,
    get_pending_requests,
    respond_to_request,
)
from app.services.post_service import upload_post_image

router = APIRouter(prefix="/expert", tags=["Expert Consultation"])


@router.post("/requests", response_model=ExpertRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    title: str = Form(...),
    description: str = Form(...),
    disease_result: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    """Create a new expert consultation request."""
    image_url = None
    if image and image.content_type and image.content_type.startswith("image/"):
        image_url = await upload_post_image(image)

    disease_data = None
    if disease_result:
        import json
        try:
            disease_data = json.loads(disease_result)
        except json.JSONDecodeError:
            pass

    request = await create_expert_request(
        user_id=current_user["id"],
        title=title,
        description=description,
        image_url=image_url,
        disease_result=disease_data,
    )

    return await get_request_by_id(str(request["_id"]))


@router.get("/requests", response_model=ExpertRequestListResponse)
async def list_my_requests(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get the current user's expert requests."""
    result = await get_user_requests(current_user["id"], page, page_size)
    return ExpertRequestListResponse(**result)


@router.get("/requests/{request_id}", response_model=ExpertRequestResponse)
async def get_single_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single expert request by ID."""
    request = await get_request_by_id(request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return ExpertRequestResponse(**request)


@router.get("/pending", response_model=ExpertRequestListResponse)
async def list_pending(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(require_role(["expert", "admin"])),
):
    """Get all pending expert requests (experts and admins only)."""
    result = await get_pending_requests(page, page_size)
    return ExpertRequestListResponse(**result)


@router.put("/requests/{request_id}/respond", response_model=ExpertRequestResponse)
async def submit_response(
    request_id: str,
    data: ExpertResponseSubmit,
    current_user: dict = Depends(require_role(["expert", "admin"])),
):
    """Expert responds to a consultation request."""
    try:
        result = await respond_to_request(
            request_id=request_id,
            expert_id=current_user["id"],
            response=data.response,
        )
        return ExpertRequestResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
