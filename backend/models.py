from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    gender = Column(String(10), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    height = Column(Float, nullable=True)
    initial_weight = Column(Float, nullable=True)
    target_weight = Column(Float, nullable=True)
    target_date = Column(DateTime, nullable=True)

    body_metrics = relationship("BodyMetric", back_populates="user", cascade="all, delete-orphan")
    diet_records = relationship("DietRecord", back_populates="user", cascade="all, delete-orphan")
    exercise_records = relationship("ExerciseRecord", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    health_profile = relationship("UserHealthProfile", back_populates="user", uselist=False,
                                  cascade="all, delete-orphan")
    feedbacks = relationship("RecommendationFeedback", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("HealthInsight", back_populates="user", cascade="all, delete-orphan")


class BodyMetric(Base):
    __tablename__ = "body_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    body_fat = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    record_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="body_metrics")


class DietRecord(Base):
    __tablename__ = "diet_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_name = Column(String(100), nullable=False)
    calories = Column(Float, nullable=False)
    meal_type = Column(String(20), nullable=True)
    record_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diet_records")


class ExerciseRecord(Base):
    __tablename__ = "exercise_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_type = Column(String(50), nullable=False)
    duration = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=True)
    record_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exercise_records")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rec_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    diet_target_calories = Column(Float, nullable=True)
    diet_carbs = Column(Float, nullable=True)
    diet_protein = Column(Float, nullable=True)
    diet_fat = Column(Float, nullable=True)
    diet_suggestion = Column(Text, nullable=True)
    exercise_type = Column(String(50), nullable=True)
    exercise_duration = Column(Integer, nullable=True)
    exercise_calories = Column(Float, nullable=True)
    exercise_suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")
    feedbacks = relationship("RecommendationFeedback", back_populates="recommendation")


class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    feature_vector = Column(Text, nullable=True)
    dietary_preferences = Column(Text, nullable=True)
    food_allergies = Column(Text, nullable=True)
    meal_pattern = Column(String(50), nullable=True)
    exercise_preferences = Column(Text, nullable=True)
    exercise_frequency = Column(Integer, nullable=True)
    weekly_weight_loss_target = Column(Float, nullable=True)
    preferred_workout_time = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="health_profile")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    feedback_type = Column(String(20), nullable=False)
    rating = Column(Integer, nullable=True)
    is_followed = Column(Boolean, default=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
    recommendation = relationship("Recommendation", back_populates="feedbacks")


class HealthInsight(Base):
    __tablename__ = "health_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    insight_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    insight_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="insights")