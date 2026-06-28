"""
KrishakBondhu - Disease Service
Business logic for disease detection: image upload, ML prediction, and info lookup.
"""

from datetime import datetime, timezone
from typing import Optional

import cloudinary
import cloudinary.uploader
from bson import ObjectId
from fastapi import UploadFile

from app.core.config import settings
from app.db.mongodb import get_database
from app.ml.predictor import predict_disease

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


async def upload_image_to_cloudinary(file: UploadFile) -> str:
    """Upload an image file to Cloudinary and return the URL."""
    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder="krishakbondhu/disease",
        resource_type="image",
    )
    return result["secure_url"]


async def detect_disease(file: UploadFile, user_id: str) -> dict:
    """
    Full disease detection pipeline:
    1. Upload image to Cloudinary
    2. Run ML prediction
    3. Look up disease info from DB
    4. Save prediction to history
    5. Return combined result
    """
    # 1. Upload to Cloudinary
    image_url = await upload_image_to_cloudinary(file)

    # 2. Reset file position and run prediction
    await file.seek(0)
    contents = await file.read()
    prediction = predict_disease(contents)

    disease_name = prediction["disease_name"]
    confidence = prediction["confidence"]

    # 3. Look up disease info from DB
    db = get_database()
    disease_info = await db.disease_info.find_one({"disease_name": disease_name})

    symptoms = []
    remedy = None
    prevention = None
    plant = None

    if disease_info:
        symptoms = disease_info.get("symptoms", [])
        remedy = disease_info.get("remedy")
        prevention = disease_info.get("prevention")
        plant = disease_info.get("plant")

    # 4. Save to prediction history
    history_doc = {
        "user_id": ObjectId(user_id),
        "disease_name": disease_name,
        "confidence": confidence,
        "image_url": image_url,
        "created_at": datetime.now(timezone.utc),
    }
    await db.prediction_history.insert_one(history_doc)

    # 5. Return combined result
    return {
        "disease_name": disease_name,
        "confidence": confidence,
        "plant": plant,
        "symptoms": symptoms,
        "remedy": remedy,
        "prevention": prevention,
        "image_url": image_url,
    }


async def get_prediction_history(user_id: str, page: int = 1, page_size: int = 20) -> dict:
    """Get a user's prediction history with pagination."""
    db = get_database()
    skip = (page - 1) * page_size

    cursor = db.prediction_history.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1).skip(skip).limit(page_size)

    predictions = []
    async for doc in cursor:
        predictions.append({
            "id": str(doc["_id"]),
            "disease_name": doc["disease_name"],
            "confidence": doc["confidence"],
            "image_url": doc["image_url"],
            "created_at": doc["created_at"],
        })

    total = await db.prediction_history.count_documents({"user_id": ObjectId(user_id)})

    return {"predictions": predictions, "total": total}


async def get_disease_info(disease_name: str) -> Optional[dict]:
    """Look up disease info by name."""
    db = get_database()
    doc = await db.disease_info.find_one({"disease_name": disease_name})
    if doc:
        doc["id"] = str(doc["_id"])
    return doc
