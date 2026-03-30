from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from dependencies import get_current_user
import models
import schemas

router = APIRouter(prefix="/api", tags=["数据录入"])

def calculate_body_fat(height_cm: float, weight_kg: float, age: int, gender: str) -> float:
    """
    估算体脂率（%）
    使用基于BMI和年龄的简化公式
    """
    bmi = weight_kg / ((height_cm / 100) ** 2)
    if gender == "男":
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    # 限制合理范围
    return max(5.0, min(45.0, body_fat))

def calculate_bmr(height_cm: float, weight_kg: float, age: int, gender: str) -> float:
    """
    计算基础代谢率（kcal/天），使用 Mifflin-St Jeor 公式
    """
    if gender == "男":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

@router.post("/body-metrics", response_model=schemas.BodyMetricResponse)
def create_body_metric(
    metric: schemas.BodyMetricCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 如果前端未提供 body_fat 或 bmr，但有 height、age、gender，则自动计算
        if (metric.body_fat is None or metric.bmr is None) and \
           metric.height is not None and metric.age is not None and metric.gender is not None:
            # 计算体脂率
            if metric.body_fat is None:
                metric.body_fat = calculate_body_fat(metric.height, metric.weight, metric.age, metric.gender)
            # 计算基础代谢
            if metric.bmr is None:
                metric.bmr = calculate_bmr(metric.height, metric.weight, metric.age, metric.gender)

        # 最终如果没有 body_fat 或 bmr，使用默认值（防止数据库报错）
        body_fat = metric.body_fat if metric.body_fat is not None else 25.0
        bmr = metric.bmr if metric.bmr is not None else 1500.0

        record_datetime = datetime.combine(metric.record_date, datetime.min.time())

        db_metric = models.BodyMetric(
            user_id=current_user.id,
            weight=metric.weight,
            body_fat=body_fat,
            bmr=bmr,
            record_date=record_datetime
        )
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存失败: {str(e)}")

@router.post("/diet-records", response_model=schemas.DietRecordResponse)
def create_diet_record(
    record: schemas.DietRecordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        record_datetime = datetime.combine(record.record_date, datetime.min.time())
        db_record = models.DietRecord(
            user_id=current_user.id,
            food_name=record.food_name,
            calories=record.calories,
            meal_type=record.meal_type,
            record_date=record_datetime
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存失败: {str(e)}")

@router.post("/exercise-records", response_model=schemas.ExerciseRecordResponse)
def create_exercise_record(
    record: schemas.ExerciseRecordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        record_datetime = datetime.combine(record.record_date, datetime.min.time())
        db_record = models.ExerciseRecord(
            user_id=current_user.id,
            exercise_type=record.exercise_type,
            duration=record.duration,
            calories_burned=record.calories_burned,
            record_date=record_datetime
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存失败: {str(e)}")