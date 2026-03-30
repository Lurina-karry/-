import httpx

# 运动 MET 表（代谢当量，单位：千卡/公斤/小时）
MET_TABLE = {
    '慢跑': 7.0,
    '快走': 4.0,
    '游泳': 8.0,
    '骑行': 6.0,
    '瑜伽': 2.5,
    '高强度间歇训练': 12.0,
    '跳绳': 11.8,
    '椭圆机': 5.5,
    '爬楼梯': 8.0,
    '力量训练': 6.0,
    '普拉提': 3.0,
    '散步': 3.5,
}

async def estimate_food_calories(food_name: str) -> float:
    """
    使用 Open Food Facts 免费 API 估算食物热量（千卡/100g）
    返回数值，失败返回 None
    """
    print(f"🔍 估算食物: {food_name}")
    if not food_name:
        return None

    # 构建搜索 URL（按名称搜索，返回第一条结果）
    search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_name}&search_simple=1&json=1&page_size=1"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(search_url)
            print(f"📡 Open Food Facts 响应状态: {response.status_code}")

            if response.status_code != 200:
                return None

            data = response.json()
            products = data.get("products", [])
            if not products:
                print(f"❌ 未找到食物: {food_name}")
                return None

            product = products[0]
            # 获取每100克能量（千卡）
            energy_kcal = product.get("nutriments", {}).get("energy-kcal_100g")
            if energy_kcal is None:
                # 尝试用千焦换算
                energy_kj = product.get("nutriments", {}).get("energy-kj_100g")
                if energy_kj:
                    energy_kcal = energy_kj / 4.184
                else:
                    return None

            print(f"✅ 找到 {food_name}，热量: {energy_kcal} 千卡/100g")
            return float(energy_kcal)
    except Exception as e:
        print(f"❌ Open Food Facts API 调用失败: {e}")
        return None


async def estimate_exercise_calories(exercise_type: str, duration_minutes: int, weight_kg: float = 70) -> float:
    """
    使用 MET 公式估算运动消耗（千卡）
    消耗 = MET × 体重(kg) × 时长(小时)
    """
    print(f"🏃 估算运动: {exercise_type}, 时长: {duration_minutes} 分钟, 体重: {weight_kg} kg")
    if not exercise_type or duration_minutes <= 0:
        return None

    # 精确匹配
    met = MET_TABLE.get(exercise_type, 0)
    if met == 0:
        # 模糊匹配
        for key in MET_TABLE:
            if key in exercise_type or exercise_type in key:
                met = MET_TABLE[key]
                break
    if met == 0:
        print(f"❌ 未找到运动类型: {exercise_type}")
        return None

    hours = duration_minutes / 60
    calories = met * weight_kg * hours
    print(f"✅ 估算消耗: {calories} 千卡")
    return round(calories, 1)