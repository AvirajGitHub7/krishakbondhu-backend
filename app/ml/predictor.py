"""
KrishakBondhu - ML Disease Predictor
Loads a HuggingFace plant disease classification model and runs inference.
"""

import io
from typing import Optional

import torch
from PIL import Image
from transformers import AutoModelForImageClassification
from torchvision import transforms

from app.core.config import settings

# Global model references (loaded once at startup)
_processor = None
_model = None
_is_loaded = False


def load_model():
    """Load the HuggingFace model and processor. Called once at app startup."""
    global _processor, _model, _is_loaded

    if _is_loaded:
        return

    model_name = settings.HF_MODEL_NAME
    print(f"Loading ML model: {model_name}...")

    _processor = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    _model = AutoModelForImageClassification.from_pretrained(model_name)
    _model.eval()  # Set to evaluation mode

    _is_loaded = True
    print(f"ML model loaded successfully! Labels: {len(_model.config.id2label)}")


def predict_disease(image_bytes: bytes) -> dict:
    """
    Run disease prediction on raw image bytes.
    Returns: {"disease_name": str, "confidence": float}
    """
    if not _is_loaded:
        raise RuntimeError("ML model not loaded. Call load_model() first.")

    # Load and preprocess the image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Process image for the model
    input_tensor = _processor(image).unsqueeze(0)

    # Run inference (no gradient computation needed)
    with torch.no_grad():
        outputs = _model(input_tensor)

    # Get predicted class and confidence
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    predicted_class_idx = logits.argmax(-1).item()
    confidence = probabilities[0][predicted_class_idx].item()

    # Map index to label
    disease_name = _model.config.id2label[predicted_class_idx]

    return {
        "disease_name": disease_name,
        "confidence": round(confidence, 4),
    }


def get_all_labels() -> dict:
    """Get all label mappings from the model."""
    if not _is_loaded:
        return {}
    return _model.config.id2label
