# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from typing import List, Dict, AsyncIterable

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

from src.core.config import settings


# --- 1. 定义结构化输出模型 (可选，但推荐) ---
# 这能让 AI 的输出更规范，pydantic-ai 会自动验证。
class ChatResponse(BaseModel):
    content: str = Field(description="The assistant's response content.")


# --- 2. 正确初始化 Agent ---
# 步骤 A: 创建 DeepSeek Provider
deepseek_provider = DeepSeekProvider(api_key=settings.OPENAI_API_KEY)

# 步骤 B: 使用 Provider 创建 Model
# 'deepseek-chat' 是 DeepSeek 的模型名称
deepseek_model = OpenAIChatModel('deepseek-chat', provider=deepseek_provider)

# 步骤 C: 将 Model 实例传递给 Agent
agent = Agent(
    model=deepseek_model,
    # system_prompt 或 instructions 是一样的
    system_prompt="You are a helpful AI assistant. Respond based on the conversation history.",
    # output_type=ChatResponse, # 如果你需要结构化输出，可以取消这行注释
)


# --- 3. 实现真正的流式响应 ---
async def stream_chat_response(messages: List[Dict[str, str]]) -> AsyncIterable[str]:
    """
    使用 pydantic-ai Agent 的 run_stream 方法实现真正的流式响应。

    Args:
        messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]

    Yields:
        str: AI 回复的每一个文本块。
    """
    # pydantic-ai 的 run_stream 方法可以直接接收消息列表
    # 它返回一个异步迭代器，可以逐块获取结果
    async for chunk in agent.run_stream(messages):
        # chunk 对象有一个 content 属性，包含了当前生成的文本片段
        if chunk.content:
            yield chunk.content


# --- 4. (可选) 同步调用示例 ---
# 如果你需要非流式的完整回复，可以使用 run 方法
async def get_chat_response(messages: List[Dict[str, str]]) -> str:
    """
    获取完整的、非流式的 AI 回复。
    """
    result = await agent.run(messages)
    # 如果你使用了 output_type=ChatResponse，那么 result.data 就是 ChatResponse 对象
    # 否则，result.output 是一个 ModelOutput 对象，其 content 属性包含回复
    return result.output.content
