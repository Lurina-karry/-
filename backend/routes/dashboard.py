from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd

from database import get_db
from dependencies import get_current_user
import models
import schemas
from services.data_fusion import get_daily_summary

router = APIRouter(prefix="/api", tags=["仪表盘"])

@router.get("/dashboard/overview", response_model=schemas.OverviewData)
def get_overview(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    date_range = [start_date + timedelta(days=i) for i in range(7)]
    date_strs = [d.strftime("%Y-%m-%d") for d in date_range]

    weights = []
    for day in date_range:
        next_day = day + timedelta(days=1)
        record = db.query(models.BodyMetric).filter(
            models.BodyMetric.user_id == current_user.id,
            models.BodyMetric.record_date >= datetime.combine(day, datetime.min.time()),
            models.BodyMetric.record_date < datetime.combine(next_day, datetime.min.time())
        ).order_by(models.BodyMetric.record_date.desc()).first()
        weights.append(record.weight if record else None)

    # 填充 None 值
    last_weight = None
    for i in range(len(weights)):
        if weights[i] is not None:
            last_weight = weights[i]
        elif last_weight is not None:
            weights[i] = last_weight
        else:
            weights[i] = 0.0  # 避免 None 导致验证错误

    intake_list = []
    expenditure_list = []
    for day in date_range:
        summary = get_daily_summary(db, current_user.id, day)
        intake_list.append(summary["total_intake"])
        expenditure_list.append(summary["total_expenditure"])

    return schemas.OverviewData(
        weightDates=date_strs,
        weights=weights,
        dates=date_strs,
        intake=intake_list,
        expenditure=expenditure_list
    )