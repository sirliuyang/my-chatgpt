# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import json
import logging
from typing import List, Dict, AsyncIterable, Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.common.config import settings

debug = False


class ChatResponse(BaseModel):
    content: str = Field(..., description="Assistant's response")


# 初始化 provider / model（你原来的配置）
deepseek_provider = OpenAIProvider(
    base_url='https://api.deepseek.com',
    api_key=settings.OPENAI_API_KEY
)
deepseek_model = OpenAIChatModel(model_name="deepseek-chat", provider=deepseek_provider)
agent = Agent(
    model=deepseek_model,
    system_prompt="You are a helpful AI assistant.",
    output_type=ChatResponse,
)


def _extract_text_from_partial(partial: Any) -> str:
    """
    将 result.stream_output 或 validate_response 输出的 partial / model response 转为可读文本。
    优先抽取 'content' 字段；否则将对象 JSON 序列化为字符串。
    """
    try:
        # dict-like
        if isinstance(partial, dict):
            if 'content' in partial and isinstance(partial['content'], str):
                return partial['content']
            # 尝试将整个 dict 序列化
            return json.dumps(partial, ensure_ascii=False, default=str)
        # pydantic model
        if hasattr(partial, 'dict'):
            d = partial.dict()
            if 'content' in d:
                return d.get('content') or ''
            return json.dumps(d, ensure_ascii=False, default=str)
        # string
        if isinstance(partial, str):
            return partial
        # fallback
        return str(partial)
    except Exception as e:
        logging.warning(f"_extract_text_from_partial 错误: {e}")
        return str(partial)


def _compute_delta(prev: str, new: str) -> str:
    """
    计算 new 相对于 prev 的最小新增后缀（避免重复）。
    算法：寻找 prev 的最大后缀等于 new 的前缀的长度 k，返回 new[k:].
    另外处理 new 中包含 prev 的情况（直接去掉 prev 前缀）。
    """
    if not prev:
        return new
    if not new:
        return ''
    # 如果 new 完全包含 prev（作为子串），但最常见场景是 prev 是 new 的前缀 -> 快速处理
    if new.startswith(prev):
        return new[len(prev):]
    # 如果 prev 出现在 new 中其他位置（极少），则返回 new 后缀（避免插入重复）
    idx = new.find(prev)
    if idx != -1:
        return new[idx + len(prev):]
    # 否则寻找最大后缀/前缀重叠
    max_overlap = min(len(prev), len(new))
    for k in range(max_overlap, 0, -1):
        if prev.endswith(new[:k]):
            return new[k:]
    # 没有任何重叠，返回整个 new（视为新的补充）
    return new


async def stream_chat_response(messages: List[Dict[str, str]]) -> AsyncIterable[str]:
    """
    返回 AsyncIterable[str]，每次 yield 一个**仅新增的文本后缀（delta）**（不带 data: 前缀）。
    兼容多种 agent 流接口；对每次从模型得到的“片段”，我们会合成 current_text（最新完整文本），
    然后计算相对于 last_sent_text 的 delta 并取出发送。
    """
    last_sent = ""
    last_full = ""  # 跟踪模型当前的“完整文本”状态
    try:
        # 聚合用户输入（原有逻辑）
        user_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content += (msg.get("content", "") or "") + "\n"
        user_content = user_content.strip()

        if not user_content:
            yield "错误：没有有效的用户消息"
            return

        async with agent.run_stream(user_content) as result:
            # 直接使用结构化流（stream_output）处理DeepSeek API的结构化响应
            try:
                if debug: print("使用结构化流 (stream_output)")
                async for partial in result.stream_output():
                    text = _extract_text_from_partial(partial)
                    if text is None:
                        continue
                    # candidate full text 判断（如果 partial 看起来是累计文本则直接用 text，否则 append）
                    if text.startswith(last_full):
                        candidate_full = text
                    else:
                        candidate_full = last_full + text

                    delta = _compute_delta(last_sent, candidate_full)
                    if delta:
                        if debug: print("Yield delta (output):", delta)
                        yield delta
                        last_sent += delta
                    last_full = candidate_full
                return
            except Exception as e:
                logging.warning(f"结构化流处理异常: {e}")

            # 3) 降级到 stream_responses + validate_response_output
            try:
                if debug: print("尝试 stream_responses + validate_response_output")
                async for model_response, last in result.stream_responses(debounce_by=0.01):
                    try:
                        validated = await result.validate_response_output(model_response, allow_partial=not last)
                    except Exception as e:
                        logging.warning(f"validate_response_output 失败: {e}")
                        continue
                    text = _extract_text_from_partial(validated)
                    if text is None:
                        continue
                    # 合并逻辑同上
                    if text.startswith(last_full):
                        candidate_full = text
                    else:
                        candidate_full = last_full + text

                    delta = _compute_delta(last_sent, candidate_full)
                    if delta:
                        if debug: print("Yield delta (validated):", delta)
                        yield delta
                        last_sent += delta
                    last_full = candidate_full
                return
            except Exception as e:
                logging.warning(f"stream_responses 路径失败: {e}")
                yield f"请求失败: {e}"
                return

    except Exception as outer:
        logging.warning(f"stream_chat_response 最外层异常: {outer}")
        yield f"请求失败: {outer}"
