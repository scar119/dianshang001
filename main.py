from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from starlette.concurrency import run_in_threadpool
import logging


# 设置基本的日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

class UserRequest(BaseModel):
    content: str

class AIResponse(BaseModel):
    messages: list

def call_moonshot_sync(content: str):
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        logging.error("MOONSHOT_API_KEY is not set.")
        return {"error": "API key not set."}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "system",
                "content": "想象一下，你是一位生活方式专家，以推荐各种家居产品解决日常问题而闻名。当被问及常见生活挑战时，你的本能反应是建议购买特定物品，并附有详细的解释。你不只是推荐；你是基于理解、经验和找到任何情况的完美解决方案的本领来指导。请提供一个详细清单的建议，确保每个建议都附有清晰简明的理由，阐明为什么它是解决手头问题的理想方案。在最后如果有你知道的明确的品牌产品，也可以直接说出具体哪款，但必须是中国品牌",
            },
            {"role": "user", "content": content},
        ],
        "temperature": 0.3
    }
    try:
        response = requests.post("https://api.moonshot.cn/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()  # 这将抛出异常，如果状态码不是200
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")  # Python 3.6
        return {"error": str(http_err)}
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return {"error": str(err)}
    data = response.json()
    logging.info(f"Moonshot API Response: {data}")
    return data

async def send_recommendation_request(content: str):
    data = await run_in_threadpool(call_moonshot_sync, content)
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    messages = [{"role": "assistant", "content": choice["message"]["content"]} for choice in data.get("choices", [])]
    return AIResponse(messages=messages)

@app.get("/")
async def read_root():
    return {"message": "Kimi AI API is ready to receive requests"}

@app.post("/get-recommendation/", response_model=AIResponse)
async def get_recommendation(user_request: UserRequest):
    return await send_recommendation_request(user_request.content)
