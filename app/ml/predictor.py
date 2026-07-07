"""
KrishakBondhu - ML Disease Predictor
Uses HuggingFace Inference API to predict plant diseases.
"""

import os
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# We use the inference API directly so we don't load a huge model into memory.
API_URL = f"https://api-inference.huggingface.co/models/{settings.HF_MODEL_NAME.strip()}"
headers = {}
if hf_token := os.getenv("HF_TOKEN"):
    headers["Authorization"] = f"Bearer {hf_token}"
else:
    logger.warning("No HF_TOKEN found in environment. The Hugging Face API might rate-limit anonymous requests.")

def load_model():
    """No-op for Inference API. We don't load the model locally anymore."""
    logger.info(f"Configured to use Hugging Face API for: {settings.HF_MODEL_NAME}")
    if not os.getenv("HF_TOKEN"):
        logger.warning("Warning: No HF_TOKEN found in environment. The Hugging Face API might rate-limit anonymous requests.")

def predict_disease(image_bytes: bytes) -> dict:
    """
    Run disease prediction on raw image bytes by calling Hugging Face Inference API.
    Returns: {"disease_name": str, "confidence": float}
    """
    try:
        response = httpx.post(API_URL, headers=headers, content=image_bytes, timeout=30.0)
        
        # Hugging Face sometimes returns a 503 while the model is loading in their servers
        if response.status_code == 503:
            raise RuntimeError("The AI model is currently loading on Hugging Face servers. Please try again in about 30 seconds.")
            
        response.raise_for_status()
        results = response.json()
        
        if not results or not isinstance(results, list):
            raise RuntimeError(f"Unexpected response from API: {results}")
            
        # The result is a list of predictions sorted by score
        top_prediction = results[0]
        
        return {
            "disease_name": top_prediction.get("label", "Unknown"),
            "confidence": round(top_prediction.get("score", 0.0), 4),
        }
    except httpx.HTTPError as e:
        logger.error(f"HTTP Error calling HF API: {e}")
        raise RuntimeError(f"Failed to communicate with Hugging Face API: {str(e)}")

def get_all_labels() -> dict:
    """Not supported when using Inference API without local config."""
    return {}
