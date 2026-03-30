from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Dict
import models

def get_daily_summary(db: Session, user_id: int, day: date) -> Dict[str, float]:
    start = datetime.combine(day, datetime.min.time())
    end = datetime.combine(day, datetime.max.time())

    diet_records = db.query(models.DietRecord).filter(
        models.DietRecord.user_id == user_id,
        models.DietRecord.record_date >= start,
        models.DietRecord.record_date <= end
    ).all()
    total_intake = sum(r.calories for r in diet_records)

    exercise_records = db.query(models.ExerciseRecord).filter(
        models.ExerciseRecord.user_id == user_id,
        models.ExerciseRecord.record_date >= start,
        models.ExerciseRecord.record_date <= end
    ).all()
    total_exercise = sum(r.calories_burned or 0 for r in exercise_records)

    bmr_record = db.query(models.BodyMetric).filter(
        models.BodyMetric.user_id == user_id,
        models.BodyMetric.record_date <= end
    ).order_by(models.BodyMetric.record_date.desc()).first()
    if bmr_record and bmr_record.bmr:
        bmr = bmr_record.bmr
    elif bmr_record:
        bmr = bmr_record.weight * 24
    else:
        bmr = 1500

    total_expenditure = bmr + total_exercise
    return {
        "total_intake": total_intake,
        "total_expenditure": total_expenditure,
        "bmr": bmr
    }