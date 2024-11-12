from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from celery import Celery
from celery.result import AsyncResult
import torch
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image, ImageFilter
from io import BytesIO

# FastAPI app setup
app = FastAPI()

# Celery app setup with Redis as the broker
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis URL
    backend="redis://localhost:6379/0",  # Redis as backend for result storage
)

# Load model and processor (only once for the worker)
preprocessor = AutoImageProcessor.from_pretrained("google/deeplabv3_mobilenet_v2_1.0_513")
model = AutoModelForSemanticSegmentation.from_pretrained("google/deeplabv3_mobilenet_v2_1.0_513")

# Celery task for generating a sticker in the background
@celery_app.task
def create_sticker_task(file_bytes: bytes):
    """Celery task for generating the sticker in the background without saving to disk."""
    # Load the image from the provided bytes
    input_image = Image.open(BytesIO(file_bytes)).convert("RGB")

    # Generate segmentation mask
    mask = get_segmentation_mask(input_image)

    # Apply mask to the image to create the sticker
    sticker = apply_mask_to_image(input_image, mask)

    # Save the output to a BytesIO stream to return as an in-memory image
    output_stream = BytesIO()
    sticker.save(output_stream, format="PNG")
    output_stream.seek(0)  # Reset stream position for reading
    return output_stream.getvalue()


def get_segmentation_mask(image: Image.Image) -> Image.Image:
    """Generate a binary segmentation mask with feathered edges from an input image."""
    inputs = preprocessor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    predicted_mask = preprocessor.post_process_semantic_segmentation(outputs)[0]
    mask_np = predicted_mask.cpu().numpy().astype("uint8") * 255  # Convert to binary
    binary_mask = Image.fromarray(mask_np)

    feathered_mask = binary_mask.filter(ImageFilter.GaussianBlur(1))
    feathered_mask = feathered_mask.resize(image.size, Image.BICUBIC)

    return feathered_mask


def apply_mask_to_image(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Apply the segmentation mask to the image to create the sticker."""
    image = image.convert("RGBA")
    sticker = Image.new("RGBA", image.size)
    sticker.paste(image, (0, 0), mask)
    return sticker


@app.post("/create_sticker/")
async def create_sticker(file: UploadFile = File(...)):
    """Endpoint to convert an uploaded image to a sticker using Celery for background processing."""
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Only PNG and JPEG are supported.")

    # Read the file's bytes
    file_bytes = await file.read()

    # Call the Celery task to process the image in the background
    task = create_sticker_task.apply_async(args=[file_bytes])

    # Return task id to the client
    return {"task_id": task.id, "message": "Processing in background. Please check back later."}


@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """Endpoint to check the status of the Celery task and return the image directly when done."""
    task = AsyncResult(task_id, app=celery_app)
    if task.state == "PENDING":
        return {"status": "Task is being processed"}
    elif task.state == "SUCCESS":
        # Get the image bytes from the task result
        image_bytes = task.result

        # Return the image as a streaming response
        return StreamingResponse(BytesIO(image_bytes), media_type="image/png")
    elif task.state == "FAILURE":
        return {"status": "Task failed", "error": str(task.info)}
    return {"status": "Unknown"}
