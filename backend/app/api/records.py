"""Records Endpoint — GET /records"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Animal, AnimalImage, Classification, ATCScore
from app.schemas.schemas import PaginatedRecords, RecordSummary

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────────────────────
#  GET ALL RECORDS (PAGINATED)
# ─────────────────────────────────────────────────────────────
@router.get("/records", response_model=PaginatedRecords)
async def get_records(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    animal_class: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated classification records"""

    base_url = str(request.base_url).rstrip("/")

    # COUNT QUERY
    count_q = select(func.count(Classification.id)).where(Classification.status == "completed")

    if animal_class:
        count_q = count_q.where(Classification.predicted_class == animal_class)

    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    #  DATA QUERY
    data_q = (
        select(Classification)
        .options(
            selectinload(Classification.animal),
            selectinload(Classification.score),
            selectinload(Classification.image)
        )
        .where(Classification.status == "completed")
    )

    if animal_class:
        data_q = data_q.where(Classification.predicted_class == animal_class)

    if grade:
        data_q = data_q.join(ATCScore, ATCScore.classification_id == Classification.id)\
                       .where(ATCScore.grade == grade)

    data_q = (
        data_q.order_by(desc(Classification.created_at))
              .offset((page - 1) * page_size)
              .limit(page_size)
    )

    result = await db.execute(data_q)
    classifications = result.scalars().all()

    #  FORMAT RESPONSE
    items = []
    for clf in classifications:
        image_url = f"{base_url}/uploads/{clf.image.filename}" if clf.image else None

        items.append(
            RecordSummary(
                id=clf.id,
                tag_number=clf.animal.tag_number if clf.animal else None,
                name=clf.animal.name if clf.animal else None,
                breed=clf.animal.breed if clf.animal else None,
                predicted_class=clf.predicted_class,
                confidence=clf.confidence,
                final_score=clf.score.final_score if clf.score else None,
                grade=clf.score.grade if clf.score else None,
                image_url=image_url,
                created_at=clf.created_at,
            )
        )

    return PaginatedRecords(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# ─────────────────────────────────────────────────────────────
#  GET SINGLE RECORD DETAILS
# ─────────────────────────────────────────────────────────────
@router.get("/records/{classification_id}")
async def get_record_detail(
    classification_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get full details for a single classification"""

    result = await db.execute(
        select(Classification)
        .options(
            selectinload(Classification.animal),
            selectinload(Classification.score),
            selectinload(Classification.image),
        )
        .where(Classification.id == classification_id)
    )

    clf = result.scalar_one_or_none()

    if not clf:
        raise HTTPException(status_code=404, detail="Record not found")

    return {
        "classification": {
            "id": clf.id,
            "predicted_class": clf.predicted_class,
            "confidence": clf.confidence,
            "status": clf.status,
            "created_at": clf.created_at.isoformat(),
            "processing_time_ms": clf.processing_time_ms,
        },
        "animal": {
            "id": clf.animal.id,
            "tag_number": clf.animal.tag_number,
            "name": clf.animal.name,
            "breed": clf.animal.breed,
            "age_years": clf.animal.age_years,
            "sex": clf.animal.sex,
            "owner_name": clf.animal.owner_name,
            "location": clf.animal.location,
        } if clf.animal else None,
        "measurements": {
            "body_length_cm": clf.body_length_cm,
            "height_cm": clf.height_cm,
            "chest_girth_cm": clf.chest_girth_cm,
            "body_depth_cm": clf.body_depth_cm,
            "rump_width_cm": clf.rump_width_cm,
        },
        "score": {
            "final_score": clf.score.final_score,
            "grade": clf.score.grade,
            "components": {
                "body_length": clf.score.body_length_score,
                "height": clf.score.height_score,
                "chest_girth": clf.score.chest_girth_score,
                "rump_angle": clf.score.rump_angle_score,
                "rump_width": clf.score.rump_width_score,
                "body_depth": clf.score.body_depth_score,
                "dairy_character": clf.score.dairy_character_score,
                "feet_legs": clf.score.feet_legs_score,
                "udder": clf.score.udder_score,
            },
        } if clf.score else None,
    }