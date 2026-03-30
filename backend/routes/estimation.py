import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["estimation"])

# ---------- 请求/响应模型 ----------
class FoodEstimateRequest(BaseModel):
    food_name: str

class FoodEstimateResponse(BaseModel):
    name: str
    calories: float
    serving_size: str = "100g"

class ExerciseEstimateRequest(BaseModel):
    exercise_type: str
    duration: int  # 分钟
    weight: float  # kg

class ExerciseEstimateResponse(BaseModel):
    total_calories: float

# ---------- 食物热量估算 ----------
@router.post("/estimate/food", response_model=FoodEstimateResponse)
async def estimate_food(request: FoodEstimateRequest):
    """
    通过 Open Food Facts 估算食物热量
    """
    food_name = request.food_name.strip()
    if not food_name:
        raise HTTPException(status_code=422, detail="食物名称不能为空")

    logger.info(f"🔍 估算食物: {food_name}")

    # Open Food Facts 搜索参数
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"📡 Open Food Facts 响应状态: {resp.status_code}")
    except httpx.TimeoutException:
        logger.error("外部服务响应超时")
        raise HTTPException(status_code=504, detail="外部服务响应超时，请稍后重试")
    except httpx.HTTPStatusError as e:
        logger.error(f"外部服务 HTTP 错误: {e.response.status_code}")
        raise HTTPException(status_code=502, detail=f"外部服务异常 (HTTP {e.response.status_code})")
    except Exception as e:
        logger.error(f"内部错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

    products = data.get("products", [])
    if not products:
        logger.warning(f"❌ 未找到食物: {food_name}")
        raise HTTPException(status_code=404, detail=f"未找到食物「{food_name}」的热量信息，请手动输入")

    # 提取第一个产品的热量信息
    product = products[0]
    nutriments = product.get("nutriments", {})
    calories = nutriments.get("energy-kcal_100g")
    if calories is None:
        # 部分产品使用 energy_100g 转换为千卡
        energy = nutriments.get("energy_100g")
        if energy and "kJ" in str(energy):
            # 粗略转换：1 kJ ≈ 0.239 kcal
            calories = energy * 0.239 if isinstance(energy, (int, float)) else None
        if calories is None:
            raise HTTPException(status_code=404, detail=f"食物「{food_name}」缺少热量信息，请手动输入")

    product_name = product.get("product_name", food_name)
    logger.info(f"✅ 估算成功: {product_name} - {calories} kcal/100g")

    return FoodEstimateResponse(
        name=product_name,
        calories=calories
    )

# ---------- 运动热量估算（保持不变，仅作示例） ----------
@router.post("/estimate/exercise", response_model=ExerciseEstimateResponse)
async def estimate_exercise(request: ExerciseEstimateRequest):
    """
    根据运动类型和体重估算消耗热量（简易MET算法）
    """
    # 运动代谢当量（MET）字典（示例值）
    met_values = {
        "跑步": 8.0,
        "快走": 5.0,
        "慢走": 3.0,
        "游泳": 7.0,
        "骑行": 6.0,
        "瑜伽": 2.5,
        "力量训练": 4.0,
    }
    met = met_values.get(request.exercise_type, 4.0)  # 默认4.0
    # 消耗热量（千卡）= MET * 体重(kg) * 时间(小时)
    hours = request.duration / 60.0
    calories = met * request.weight * hours
    return ExerciseEstimateResponse(total_calories=calories)