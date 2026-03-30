import os
from datetime import timedelta

# JWT 配置
SECRET_KEY = "your-secret-key-please-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 数据库配置（根据实际修改）
DATABASE_URL = "mysql+pymysql://root:123456@localhost/health_recommend?charset=utf8mb4"
# DATABASE_URL = "sqlite:///./test.db"

# 推荐算法配置
RECOMMENDATION_CONFIG = {
    "daily_deficit": 500,
    "activity_factor": 1.2,
    "min_calories": 1200,
    "protein_ratio": 0.3,
    "carb_ratio": 0.5,
    "fat_ratio": 0.2,
    "exercise_target_calories": 300,
}

# 智能估算配置（使用免费 Open Food Facts API + 本地 MET 表）
USE_LLM_FOR_ESTIMATION = True   # 启用免费估算功能