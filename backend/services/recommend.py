import json
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
import models
from config import RECOMMENDATION_CONFIG

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def generate_recommendation(self, user: models.User) -> Optional[Dict]:
        latest_metric = self.db.query(models.BodyMetric).filter(
            models.BodyMetric.user_id == user.id
        ).order_by(models.BodyMetric.record_date.desc()).first()
        if not latest_metric:
            return None

        weight = latest_metric.weight
        bmr = latest_metric.bmr if latest_metric.bmr else weight * 24

        profile = self.db.query(models.UserHealthProfile).filter(
            models.UserHealthProfile.user_id == user.id
        ).first()

        target_calories = self._calculate_target_calories(bmr, profile)
        nutrition = self._calculate_macros(target_calories, profile)
        diet_suggestion = self._generate_diet_suggestion(target_calories, nutrition, profile)
        exercise = self._generate_exercise_recommendation(weight, profile)
        insights = self._generate_insights(user)
        tips = self._generate_tips(user, profile)

        return {
            "diet": {
                "totalCalories": round(target_calories, 1),
                "carbs": round(nutrition["carbs"], 1),
                "protein": round(nutrition["protein"], 1),
                "veggies": round(nutrition["veggies"], 1),
                "suggestion": diet_suggestion
            },
            "exercise": {
                "type": exercise["type"],
                "duration": exercise["duration"],
                "caloriesBurned": exercise["caloriesBurned"],
                "suggestion": exercise["suggestion"]
            },
            "insights": insights,
            "tips": tips,
            "alternative_options": self._generate_alternatives(user, target_calories, exercise)
        }

    def _calculate_target_calories(self, bmr: float, profile: Optional[models.UserHealthProfile]) -> float:
        tdee = bmr * RECOMMENDATION_CONFIG["activity_factor"]
        daily_deficit = RECOMMENDATION_CONFIG["daily_deficit"]
        if profile and profile.weekly_weight_loss_target:
            daily_deficit = (profile.weekly_weight_loss_target * 7700) / 7
        target = tdee - daily_deficit
        return max(target, RECOMMENDATION_CONFIG["min_calories"])

    def _calculate_macros(self, target_calories: float, profile: Optional[models.UserHealthProfile]) -> Dict:
        protein_ratio = RECOMMENDATION_CONFIG["protein_ratio"]
        carb_ratio = RECOMMENDATION_CONFIG["carb_ratio"]
        fat_ratio = RECOMMENDATION_CONFIG["fat_ratio"]
        if profile and profile.dietary_preferences:
            prefs = json.loads(profile.dietary_preferences) if isinstance(profile.dietary_preferences, str) else profile.dietary_preferences
            if "high_protein" in prefs:
                protein_ratio, carb_ratio, fat_ratio = 0.35, 0.45, 0.20
        protein_cal = target_calories * protein_ratio
        carb_cal = target_calories * carb_ratio
        fat_cal = target_calories * fat_ratio
        return {
            "protein": protein_cal / 4,
            "carbs": carb_cal / 4,
            "fat": fat_cal / 9,
            "veggies": target_calories / 100
        }

    def _generate_diet_suggestion(self, target_calories: float, nutrition: Dict, profile: Optional[models.UserHealthProfile]) -> str:
        suggestion = f"建议每日摄入约{int(target_calories)}千卡热量。蛋白质{int(nutrition['protein'])}g，碳水化合物{int(nutrition['carbs'])}g，脂肪{int(nutrition['fat'])}g。"
        if profile and profile.dietary_preferences:
            prefs = json.loads(profile.dietary_preferences) if isinstance(profile.dietary_preferences, str) else profile.dietary_preferences
            if "vegetarian" in prefs:
                suggestion += " 您偏好素食，建议多食用豆制品、藜麦等优质植物蛋白。"
        suggestion += " 主食推荐全麦面包、糙米、燕麦等粗粮；蛋白质优选鸡胸肉、鱼虾、鸡蛋；多吃绿叶蔬菜。"
        return suggestion

    def _generate_exercise_recommendation(self, weight: float, profile: Optional[models.UserHealthProfile]) -> Dict:
        target_calories = RECOMMENDATION_CONFIG["exercise_target_calories"]
        preferred_types = []
        if profile and profile.exercise_preferences:
            preferred_types = json.loads(profile.exercise_preferences) if isinstance(profile.exercise_preferences, str) else profile.exercise_preferences
        if "swimming" in preferred_types:
            exercise_type = "游泳"
            duration = int(target_calories / (weight * 0.1))
        elif "cycling" in preferred_types:
            exercise_type = "骑行"
            duration = int(target_calories / (weight * 0.08))
        elif "yoga" in preferred_types:
            exercise_type = "瑜伽"
            duration = int(target_calories / (weight * 0.05))
        else:
            run_minutes = int(target_calories / (weight * 0.1))
            if run_minutes > 60:
                exercise_type = "快走"
                duration = int(target_calories / (weight * 0.05))
            else:
                exercise_type = "慢跑"
                duration = run_minutes
        suggestion = f"建议进行{exercise_type}{duration}分钟，预计消耗约{target_calories}千卡。"
        if profile and profile.exercise_frequency:
            suggestion += f" 建议每周保持{profile.exercise_frequency}次运动频率。"
        return {
            "type": exercise_type,
            "duration": min(duration, 90),
            "caloriesBurned": target_calories,
            "suggestion": suggestion
        }

    def _generate_insights(self, user: models.User) -> List[str]:
        insights = []
        metrics = self.db.query(models.BodyMetric).filter(
            models.BodyMetric.user_id == user.id
        ).order_by(models.BodyMetric.record_date.desc()).limit(7).all()
        if len(metrics) >= 2:
            weight_change = metrics[0].weight - metrics[-1].weight
            if weight_change > 0:
                insights.append(f"最近一周体重增加{weight_change:.1f}kg，建议适当减少热量摄入或增加运动量。")
            elif weight_change < -0.5:
                insights.append(f"最近一周减重{abs(weight_change):.1f}kg，效果显著！继续保持！")
        return insights

    def _generate_tips(self, user: models.User, profile: Optional[models.UserHealthProfile]) -> List[str]:
        tips = [
            "建议每餐细嚼慢咽，每口咀嚼20次以上",
            "每天喝足2000ml水，促进新陈代谢",
            "保证7-8小时优质睡眠，有助于体重控制",
            "餐前喝一杯水，可以增加饱腹感"
        ]
        if profile and profile.dietary_preferences:
            prefs = json.loads(profile.dietary_preferences) if isinstance(profile.dietary_preferences, str) else profile.dietary_preferences
            if "vegetarian" in prefs:
                tips.append("素食者注意补充维生素B12和铁质，推荐食用发酵豆制品和深绿色蔬菜")
        return tips[:3]

    def _generate_alternatives(self, user: models.User, target_calories: float, exercise: Dict) -> List[Dict]:
        return [
            {
                "type": "low_calorie",
                "diet_calories": round(target_calories - 200, 1),
                "exercise": {"type": "瑜伽", "duration": 30, "caloriesBurned": 120},
                "description": "低强度方案，适合恢复期或运动新手"
            },
            {
                "type": "high_intensity",
                "diet_calories": round(target_calories + 100, 1),
                "exercise": {"type": "高强度间歇训练", "duration": 20, "caloriesBurned": 300},
                "description": "高强度方案，适合有一定运动基础的用户"
            }
        ]