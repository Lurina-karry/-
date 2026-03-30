from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Union
from datetime import datetime, timedelta

from database import get_db
from dependencies import get_current_user
import models
import schemas

router = APIRouter(prefix="/api", tags=["历史记录"])

@router.get("/records/{record_type}", response_model=List[Union[
    schemas.BodyMetricResponse,
    schemas.DietRecordResponse,
    schemas.ExerciseRecordResponse
]])
def get_records(
    record_type: str,
    start_date: str = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime(2000, 1, 1)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    else:
        end = datetime.now()

    if record_type == "body":
        records = db.query(models.BodyMetric).filter(
            models.BodyMetric.user_id == current_user.id,
            models.BodyMetric.record_date >= start,
            models.BodyMetric.record_date <= end
        ).order_by(models.BodyMetric.record_date.desc()).all()
        return records
    elif record_type == "diet":
        records = db.query(models.DietRecord).filter(
            models.DietRecord.user_id == current_user.id,
            models.DietRecord.record_date >= start,
            models.DietRecord.record_date <= end
        ).order_by(models.DietRecord.record_date.desc()).all()
        return records
    elif record_type == "exercise":
        records = db.query(models.ExerciseRecord).filter(
            models.ExerciseRecord.user_id == current_user.id,
            models.ExerciseRecord.record_date >= start,
            models.ExerciseRecord.record_date <= end
        ).order_by(models.ExerciseRecord.record_date.desc()).all()
        return records
    else:
        return []