from fastapi.responses import FileResponse
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image, ImageFilter
from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
import uvicorn
import torch
import os

app = FastAPI()

# Load the model and processor once to avoid reloading on every request
preprocessor = AutoImageProcessor.from_pretrained("google/deeplabv3_mobilenet_v2_1.0_513")
model = AutoModelForSemanticSegmentation.from_pretrained("google/deeplabv3_mobilenet_v2_1.0_513")

# Create the directory for saving output if it doesn’t exist
os.makedirs("output", exist_ok=True)

def get_segmentation_mask(image: Image.Image) -> Image.Image:
    """Generate a binary segmentation mask with feathered edges from an input image."""
    # Step 1: Preprocess and run model inference
    inputs = preprocessor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Step 2: Post-process the segmentation output to get a clean binary mask
    predicted_mask = preprocessor.post_process_semantic_segmentation(outputs)[0]
    mask_np = predicted_mask.cpu().numpy().astype("uint8") * 255  # Convert to binary values (0 or 255)
    binary_mask = Image.fromarray(mask_np)

    # Step 3: Apply a slight Gaussian blur to soften the edges
    feathered_mask = binary_mask.filter(ImageFilter.GaussianBlur(1))  # Adjust blur radius as needed
    feathered_mask = feathered_mask.resize(image.size, Image.BICUBIC)

    return feathered_mask

def apply_mask_to_image(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Apply the segmentation mask to the input image to create a transparent sticker."""
    image = image.convert("RGBA")  # Ensure image is in RGBA mode
    sticker = Image.new("RGBA", image.size)
    sticker.paste(image, (0, 0), mask)  # Use mask as the alpha channel
    return sticker

@app.post("/create_sticker/")
async def create_sticker(file: UploadFile = File(...)):
    """Endpoint to convert an uploaded image to a sticker."""
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Only PNG and JPEG are supported.")

    # Load the image
    input_image = Image.open(file.file).convert("RGB")

    # Generate segmentation mask and apply it to create a sticker
    mask = get_segmentation_mask(input_image)
    sticker = apply_mask_to_image(input_image, mask)

    # Save the output sticker
    output_path = f"output/sticker_{file.filename}"
    sticker.save(output_path, "PNG")

    return FileResponse(output_path, media_type="image/png")


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
