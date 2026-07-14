"""
Upload Endpoint — POST /api/v1/upload
Handles image upload, validation, storage, and DB record creation.
"""

import logging
import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Animal, AnimalImage
from app.schemas.schemas import AnimalCreate, UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    animal_id: str = Form(None),
    tag_number: str = Form(None),
    animal_name: str = Form(None),
    breed: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an animal image. Creates a new Animal record if animal_id not provided.
    Returns image metadata and URL.
    """

    # ── Validate file ─────────────────────────────────────────────────────────
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension {ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read content & check size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    # ── Get or create Animal ──────────────────────────────────────────────────
    if animal_id:
        from sqlalchemy import select
        result = await db.execute(select(Animal).where(Animal.id == animal_id))
        animal = result.scalar_one_or_none()
        if not animal:
            raise HTTPException(status_code=404, detail=f"Animal {animal_id} not found")
    else:
        animal = Animal(
            tag_number=tag_number,
            name=animal_name,
            breed=breed,
        )
        db.add(animal)
        await db.flush()  # Get generated ID

    # ── Save file ─────────────────────────────────────────────────────────────
    unique_name = f"{uuid.uuid4()}{ext}"
    upload_path = Path(settings.UPLOAD_DIR) / unique_name
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(str(upload_path), "wb") as f:
        await f.write(content)

    # Read image dimensions
    try:
        pil_img = PILImage.open(upload_path)
        width, height = pil_img.size
        mime_type = file.content_type
    except Exception:
        width, height, mime_type = None, None, file.content_type

    # ── Create DB record ──────────────────────────────────────────────────────
    image_record = AnimalImage(
        animal_id=animal.id,
        filename=unique_name,
        filepath=str(upload_path),
        original_name=file.filename,
        file_size=len(content),
        width=width,
        height=height,
        mime_type=mime_type,
    )
    db.add(image_record)
    await db.commit()
    await db.refresh(image_record)

    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/uploads/{unique_name}"

    logger.info("Image uploaded: %s → animal=%s", unique_name, animal.id)
    return UploadResponse(
        image_id=image_record.id,
        animal_id=animal.id,
        filename=unique_name,
        url=image_url,
        width=width,
        height=height,
    )
