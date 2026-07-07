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
API_URL = f"https://router.huggingface.co/hf-inference/models/{settings.HF_MODEL_NAME.strip()}"

def get_headers():
    """Retrieve headers with dynamically loaded token."""
    headers = {}
    if settings.HF_TOKEN:
        headers["Authorization"] = f"Bearer {settings.HF_TOKEN.strip()}"
    return headers

def load_model():
    """No-op for Inference API. We don't load the model locally anymore."""
    logger.info(f"Configured to use Hugging Face API for: {settings.HF_MODEL_NAME}")
    if not settings.HF_TOKEN:
        logger.warning("Warning: No HF_TOKEN found in environment. The Hugging Face API requires authentication and requests will likely fail with 401 Unauthorized.")

def predict_disease(image_bytes: bytes) -> dict:
    """
    Run disease prediction on raw image bytes by calling Hugging Face Inference API.
    Returns: {"disease_name": str, "confidence": float}
    """
    headers = get_headers()
    has_auth = "Authorization" in headers
    
    # 7. Log requested details (masking the token for security)
    masked_token = f"{settings.HF_TOKEN[:4]}...{settings.HF_TOKEN[-4:]}" if settings.HF_TOKEN and len(settings.HF_TOKEN) > 8 else "***"
    logger.info(f"--- Hugging Face API Request ---")
    logger.info(f"Request URL: {API_URL}")
    logger.info(f"Model ID: {settings.HF_MODEL_NAME}")
    logger.info(f"Authorization Header Present: {has_auth} (Token: {masked_token if has_auth else 'None'})")
    
    if not has_auth:
        raise RuntimeError("Missing Hugging Face API token (HF_TOKEN). Please configure the token in environment variables.")

    try:
        response = httpx.post(API_URL, headers=headers, content=image_bytes, timeout=30.0)
        
        logger.info(f"HTTP Status Code: {response.status_code}")
        
        # Log response body safely for debugging
        try:
            logger.info(f"Response Body: {response.text}")
        except Exception:
            pass
            
        if response.status_code == 401:
            raise RuntimeError("Hugging Face API token is invalid, expired, or revoked (401 Unauthorized). Please check your HF_TOKEN.")
            
        if response.status_code == 503:
            raise RuntimeError("The AI model is currently loading on Hugging Face servers. Please try again in about 30 seconds.")
            
        response.raise_for_status()
        results = response.json()
        
        if not results or not isinstance(results, list):
            raise RuntimeError(f"Unexpected response format from Hugging Face API: {results}")
            
        top_prediction = results[0]
        return {
            "disease_name": top_prediction.get("label", "Unknown"),
            "confidence": round(top_prediction.get("score", 0.0), 4),
        }
    except httpx.HTTPError as e:
        import traceback
        logger.error(f"HTTP Error calling HF API:\n{traceback.format_exc()}")
        raise RuntimeError(f"Failed to communicate with Hugging Face API. Network Error: {str(e)}")

def get_all_labels() -> dict:
    """Not supported when using Inference API without local config."""
    return {}
