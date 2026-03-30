from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

# ---------- 用户 ----------
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    height: Optional[float] = None
    initial_weight: Optional[float] = None
    target_weight: Optional[float] = None
    target_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ---------- 身体指标 ----------
class BodyMetricBase(BaseModel):
    weight: float
    body_fat: Optional[float] = None
    bmr: Optional[float] = None
    record_date: date

class BodyMetricCreate(BodyMetricBase):
    # 新增可选字段，用于后端自动计算
    height: Optional[float] = None      # cm
    age: Optional[int] = None
    gender: Optional[str] = None

class BodyMetricResponse(BodyMetricBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- 饮食 ----------
class DietRecordBase(BaseModel):
    food_name: str
    calories: float
    meal_type: Optional[str] = None
    record_date: date

class DietRecordCreate(DietRecordBase):
    pass

class DietRecordResponse(DietRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- 运动 ----------
class ExerciseRecordBase(BaseModel):
    exercise_type: str
    duration: int
    calories_burned: Optional[float] = None
    record_date: date

class ExerciseRecordCreate(ExerciseRecordBase):
    pass

class ExerciseRecordResponse(ExerciseRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- 推荐 ----------
class DietRecommendation(BaseModel):
    totalCalories: float
    carbs: float
    protein: float
    veggies: float
    suggestion: str

class ExerciseRecommendation(BaseModel):
    type: str
    duration: int
    caloriesBurned: float
    suggestion: Optional[str] = None

class EnhancedRecommendationResponse(BaseModel):
    diet: DietRecommendation
    exercise: ExerciseRecommendation
    insights: Optional[List[str]] = None
    tips: Optional[List[str]] = None
    alternative_options: Optional[List[Dict[str, Any]]] = None

# ---------- 仪表盘 ----------
class OverviewData(BaseModel):
    weightDates: List[str]
    weights: List[float]
    dates: List[str]
    intake: List[float]
    expenditure: List[float]

# ---------- 健康画像 ----------
class UserHealthProfileBase(BaseModel):
    dietary_preferences: Optional[List[str]] = None
    food_allergies: Optional[List[str]] = None
    meal_pattern: Optional[str] = None
    exercise_preferences: Optional[List[str]] = None
    exercise_frequency: Optional[int] = None
    weekly_weight_loss_target: Optional[float] = None
    preferred_workout_time: Optional[str] = None

class UserHealthProfileCreate(UserHealthProfileBase):
    pass

class UserHealthProfileResponse(UserHealthProfileBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# ---------- 反馈 ----------
class RecommendationFeedbackBase(BaseModel):
    recommendation_id: Optional[int] = None
    feedback_type: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_followed: bool = False
    comments: Optional[str] = None

class RecommendationFeedbackCreate(RecommendationFeedbackBase):
    pass

class RecommendationFeedbackResponse(RecommendationFeedbackBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- 健康洞察 ----------
class HealthInsightResponse(BaseModel):
    id: int
    user_id: int
    insight_type: str
    title: str
    description: str
    insight_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- 通用 ----------
class Message(BaseModel):
    detail: str