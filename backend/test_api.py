import httpx
import asyncio

async def test_deepseek_api():
    api_key = "sk-de88861d825548e2b56194025849a3dd"   # 替换为您的实际 Key
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "苹果的热量（千卡）只返回数字"}],
                "max_tokens": 20
            }
        )
        print("状态码:", response.status_code)
        print("响应内容:", response.text)

if __name__ == "__main__":
    asyncio.run(test_deepseek_api())