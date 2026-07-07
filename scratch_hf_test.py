import os
import httpx

model_name = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
API_URL = f"https://router.huggingface.co/hf-inference/models/{model_name}"

# Create a dummy image
from PIL import Image
import io

img = Image.new('RGB', (224, 224), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
image_bytes = img_byte_arr.getvalue()

try:
    response = httpx.post(API_URL, content=image_bytes, timeout=10.0)
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(e)
