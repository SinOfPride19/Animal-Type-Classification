"""Reports Endpoint — GET /api/v1/reports"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Classification, ATCScore
from app.schemas.schemas import ReportSummary, ClassDistribution, GradeDistribution, ScoreTrend

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/reports", response_model=ReportSummary)
async def get_reports(db: AsyncSession = Depends(get_db)):
    """Aggregate statistics for dashboard charts and report page."""

    # Total classifications
    total_q = await db.execute(
        select(func.count(Classification.id)).where(Classification.status == "completed")
    )
    total = total_q.scalar_one() or 0

    # Average confidence
    avg_conf_q = await db.execute(
        select(func.avg(Classification.confidence)).where(Classification.status == "completed")
    )
    avg_confidence = float(avg_conf_q.scalar_one() or 0)

    # Average score
    avg_score_q = await db.execute(select(func.avg(ATCScore.final_score)))
    avg_score = float(avg_score_q.scalar_one() or 0)

    # Class distribution
    class_q = await db.execute(
        select(Classification.predicted_class, func.count(Classification.id))
        .where(Classification.status == "completed")
        .group_by(Classification.predicted_class)
    )
    class_rows = class_q.all()
    class_dist = {"cow": 0, "buffalo": 0, "unknown": 0}
    for cls, count in class_rows:
        if cls in class_dist:
            class_dist[cls] = count

    # Grade distribution
    grade_q = await db.execute(
        select(ATCScore.grade, func.count(ATCScore.id)).group_by(ATCScore.grade)
    )
    grade_rows = grade_q.all()
    grade_dist = {"excellent": 0, "good_plus": 0, "good": 0, "average": 0}
    grade_map = {"Excellent": "excellent", "Good Plus": "good_plus", "Good": "good", "Average": "average"}
    for grade, count in grade_rows:
        key = grade_map.get(grade, "average")
        grade_dist[key] = count

    # Score trends: last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trend_q = await db.execute(
        select(
            func.date(ATCScore.created_at).label("date"),
            func.avg(ATCScore.final_score).label("avg_score"),
            func.count(ATCScore.id).label("count"),
        )
        .where(ATCScore.created_at >= thirty_days_ago)
        .group_by(func.date(ATCScore.created_at))
        .order_by(func.date(ATCScore.created_at))
    )
    trend_rows = trend_q.all()
    score_trends = [
        ScoreTrend(date=str(row.date), avg_score=round(float(row.avg_score), 2), count=row.count)
        for row in trend_rows
    ]

    top_grade_pct = 0.0
    if total > 0:
        top = grade_dist["excellent"] + grade_dist["good_plus"]
        top_grade_pct = round(100 * top / total, 1)

    return ReportSummary(
        total_classifications=total,
        avg_confidence=round(avg_confidence * 100, 1),
        avg_score=round(avg_score, 2),
        class_distribution=ClassDistribution(**class_dist),
        grade_distribution=GradeDistribution(**grade_dist),
        score_trends=score_trends,
        top_grade_percentage=top_grade_pct,
    )
