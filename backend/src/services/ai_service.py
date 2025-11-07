# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from openai import OpenAI
from src.core.config import settings

client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)


def stream_chat(messages):
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
