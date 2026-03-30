from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from dependencies import get_current_user
import models
import schemas
from services.recommend import RecommendationService

router = APIRouter(prefix="/api", tags=["推荐"])


@router.get("/recommendations/today", response_model=schemas.EnhancedRecommendationResponse)
def get_today_recommendation(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    existing = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == current_user.id,
        models.Recommendation.rec_date >= start,
        models.Recommendation.rec_date <= end
    ).first()

    if existing:
        return schemas.EnhancedRecommendationResponse(
            diet=schemas.DietRecommendation(
                totalCalories=existing.diet_target_calories,
                carbs=existing.diet_carbs,
                protein=existing.diet_protein,
                veggies=existing.diet_fat,
                suggestion=existing.diet_suggestion
            ),
            exercise=schemas.ExerciseRecommendation(
                type=existing.exercise_type,
                duration=existing.exercise_duration,
                caloriesBurned=existing.exercise_calories,
                suggestion=existing.exercise_suggestion
            ),
            insights=[],
            tips=[],
            alternative_options=[]
        )

    rec_service = RecommendationService(db)
    rec = rec_service.generate_recommendation(current_user)
    if rec is None:
        default_rec = {
            "diet": {
                "totalCalories": 1500,
                "carbs": 187.5,
                "protein": 112.5,
                "veggies": 15,
                "suggestion": "请先录入您的身体指标（体重、体脂等），以便为您生成更精准的个性化推荐。当前为系统默认建议。"
            },
            "exercise": {
                "type": "快走",
                "duration": 30,
                "caloriesBurned": 150,
                "suggestion": "建议从轻度运动开始，每周3-4次。请先录入身体指标获取个性化运动方案。"
            },
            "insights": ["建议先录入身体指标数据，系统将为您生成个性化推荐"],
            "tips": ["录入身体指标后，推荐会更精准"],
            "alternative_options": []
        }
        db_rec = models.Recommendation(
            user_id=current_user.id,
            rec_date=datetime.now(),
            diet_target_calories=default_rec["diet"]["totalCalories"],
            diet_carbs=default_rec["diet"]["carbs"],
            diet_protein=default_rec["diet"]["protein"],
            diet_fat=default_rec["diet"]["veggies"],
            diet_suggestion=default_rec["diet"]["suggestion"],
            exercise_type=default_rec["exercise"]["type"],
            exercise_duration=default_rec["exercise"]["duration"],
            exercise_calories=default_rec["exercise"]["caloriesBurned"],
            exercise_suggestion=default_rec["exercise"]["suggestion"]
        )
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)
        return schemas.EnhancedRecommendationResponse(
            diet=schemas.DietRecommendation(**default_rec["diet"]),
            exercise=schemas.ExerciseRecommendation(**default_rec["exercise"]),
            insights=default_rec["insights"],
            tips=default_rec["tips"],
            alternative_options=default_rec["alternative_options"]
        )

    db_rec = models.Recommendation(
        user_id=current_user.id,
        rec_date=datetime.now(),
        diet_target_calories=rec["diet"]["totalCalories"],
        diet_carbs=rec["diet"]["carbs"],
        diet_protein=rec["diet"]["protein"],
        diet_fat=rec["diet"]["veggies"],
        diet_suggestion=rec["diet"]["suggestion"],
        exercise_type=rec["exercise"]["type"],
        exercise_duration=rec["exercise"]["duration"],
        exercise_calories=rec["exercise"]["caloriesBurned"],
        exercise_suggestion=rec["exercise"]["suggestion"]
    )
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)

    return schemas.EnhancedRecommendationResponse(
        diet=schemas.DietRecommendation(**rec["diet"]),
        exercise=schemas.ExerciseRecommendation(**rec["exercise"]),
        insights=rec.get("insights", []),
        tips=rec.get("tips", []),
        alternative_options=rec.get("alternative_options", [])
    )