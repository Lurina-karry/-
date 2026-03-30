from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from database import get_db
from dependencies import get_current_user
import models
import schemas

router = APIRouter(prefix="/api", tags=["健康画像"])


@router.get("/profile", response_model=schemas.UserHealthProfileResponse)
def get_health_profile(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = db.query(models.UserHealthProfile).filter(
        models.UserHealthProfile.user_id == current_user.id
    ).first()
    if not profile:
        profile = models.UserHealthProfile(
            user_id=current_user.id,
            dietary_preferences=json.dumps([]),
            food_allergies=json.dumps([]),
            exercise_preferences=json.dumps([])
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    profile.dietary_preferences = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
    profile.food_allergies = json.loads(profile.food_allergies) if profile.food_allergies else []
    profile.exercise_preferences = json.loads(profile.exercise_preferences) if profile.exercise_preferences else []
    return profile


@router.put("/profile", response_model=schemas.UserHealthProfileResponse)
def update_health_profile(
        profile_data: schemas.UserHealthProfileCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = db.query(models.UserHealthProfile).filter(
        models.UserHealthProfile.user_id == current_user.id
    ).first()
    if not profile:
        profile = models.UserHealthProfile(user_id=current_user.id)
        db.add(profile)

    if profile_data.dietary_preferences is not None:
        profile.dietary_preferences = json.dumps(profile_data.dietary_preferences)
    if profile_data.food_allergies is not None:
        profile.food_allergies = json.dumps(profile_data.food_allergies)
    if profile_data.meal_pattern is not None:
        profile.meal_pattern = profile_data.meal_pattern
    if profile_data.exercise_preferences is not None:
        profile.exercise_preferences = json.dumps(profile_data.exercise_preferences)
    if profile_data.exercise_frequency is not None:
        profile.exercise_frequency = profile_data.exercise_frequency
    if profile_data.weekly_weight_loss_target is not None:
        profile.weekly_weight_loss_target = profile_data.weekly_weight_loss_target
    if profile_data.preferred_workout_time is not None:
        profile.preferred_workout_time = profile_data.preferred_workout_time

    db.commit()
    db.refresh(profile)
    profile.dietary_preferences = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
    profile.food_allergies = json.loads(profile.food_allergies) if profile.food_allergies else []
    profile.exercise_preferences = json.loads(profile.exercise_preferences) if profile.exercise_preferences else []
    return profile


@router.post("/feedback", response_model=schemas.RecommendationFeedbackResponse)
def submit_feedback(
        feedback: schemas.RecommendationFeedbackCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_feedback = models.RecommendationFeedback(
        user_id=current_user.id,
        recommendation_id=feedback.recommendation_id,
        feedback_type=feedback.feedback_type,
        rating=feedback.rating,
        is_followed=feedback.is_followed,
        comments=feedback.comments
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@router.get("/insights", response_model=List[schemas.HealthInsightResponse])
def get_health_insights(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10
):
    insights = db.query(models.HealthInsight).filter(
        models.HealthInsight.user_id == current_user.id
    ).order_by(models.HealthInsight.created_at.desc()).limit(limit).all()
    return insights