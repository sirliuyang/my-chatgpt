# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from __future__ import annotations
import logging
from typing import Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)
try:
    from ddgs import DDGS
except Exception as e:
    logger.warning(f"DDGS library not installed: {e}")
    try:
        from duckduckgo_search import DDGS
    except Exception as e:
        logger.exception(f"duckduckgo_search.DDGS library not installed: {e}")
        DDGS = None

from src.common.config import settings

_agent_singleton = None


# ============================== 工具函数定义 ==============================
def get_or_create_agent() -> Agent:
    """获取或创建 Agent 实例"""
    global _agent_singleton
    if _agent_singleton is not None:
        logger.debug("Reusing existing AG-UI Agent")
        return _agent_singleton

    provider = OpenAIProvider(
        base_url='https://api.deepseek.com',
        api_key=settings.OPENAI_API_KEY
    )
    model = OpenAIChatModel(
        model_name="deepseek-chat",
        provider=provider,
    )
    agent = Agent(
        model=model,
        system_prompt=(
            "You are a helpful AI assistant. Answer directly when possible. "
            "Use 'duckduckgo_search' only for real-time info like weather or news."
        ),
    )

    # 关键：使用正确的工具名称注册
    @agent.tool(name='tool_search')
    async def tool_search(ctx: RunContext[Any], query: str, max_results: int = 5) -> str:
        """使用 DuckDuckGo 搜索引擎进行网络搜索"""
        logger.info(f"duckduckgo_search called with query: '{query}' (max_results: {max_results})")
        if DDGS is None:
            logger.warning("DDGS not installed - tool returning error")
            return "DDGS library not installed on server"

        try:
            raw_results = DDGS().text(query, max_results=max_results)
            if not isinstance(raw_results, list):
                raw_results = list(raw_results)

            logger.info(f"Raw results: {raw_results}")

            formatted_results = [
                {
                    "title": r.get("title") or r.get("heading") or "",
                    "url": r.get("href") or r.get("url") or r.get("link") or "",
                    "snippet": r.get("body") or r.get("snippet") or r.get("text") or "",
                }
                for r in raw_results
            ]

            # 重要：返回格式化的字符串而不是字典列表
            result_text = "\n\n".join([
                f"标题: {r['title']}\n链接: {r['url']}\n摘要: {r['snippet']}"
                for r in formatted_results[:max_results]
            ])

            logger.info(f"DDGS returned {len(formatted_results)} results for '{query}'")
            return result_text if result_text else "未找到相关结果"

        except Exception as ex:
            logger.exception(f"DDGS failed for query '{query}': {ex}")
            return f"搜索失败: {str(ex)}"

    _agent_singleton = agent
    logger.info("AG-UI Agent initialized successfully (DeepSeek + DuckDuckGo tool)")
    return _agent_singleton
