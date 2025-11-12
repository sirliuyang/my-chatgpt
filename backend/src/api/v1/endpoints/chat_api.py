# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.common.auth_bearer import get_current_user
from src.db.session import get_db
from src.schemas.chat import ChatRequest
from src.services.ai_service import stream_chat_response
from src.crud.crud_conversation import conversation
from src.crud.crud_message import create_message
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)
try:
    from src.crud.crud_message import get_messages_by_conversation
except Exception as e:
    logger.warning(f"未找到 get_messages_by_conversation 函数，将无法从 DB 拉取历史消息: {e}")
    # 如果不存在此函数，后面会回退为不从 DB 拉历史（但强烈建议实现该 CRUD）
    get_messages_by_conversation = None  # type: ignore

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=None)
async def chat(
        request: ChatRequest,
        db: Session = Depends(get_db),
        current_user: Dict = Depends(get_current_user)
):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # 确保会话存在
    conversation_id = conversation.create_conversation_if_not_exists(db, request.conversation_id)

    # --------- 构造 history（优先用 client 提供的 request.history，否则从 DB 拉取） ----------
    history: List[Dict[str, str]] = []
    try:
        if request.history and isinstance(request.history, list):
            # use client's provided history (defensive copy)
            history = [dict(r) for r in request.history]
        else:
            # client 未提供 history：尝试从 DB 读取历史消息（按时间顺序）
            if get_messages_by_conversation:
                try:
                    msgs = get_messages_by_conversation(db, conversation_id)
                    # msgs 期望是一个可迭代的 ORM 对象集合，每项含有 role/content/timestamp 等
                    history = []
                    for m in msgs:
                        # 兼容 ORM 属性或 dict
                        role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else None)
                        content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else None)
                        if role and content is not None:
                            history.append({"role": role, "content": content})
                except Exception as ex:
                    logging.exception(f"从 DB 获取会话历史失败，将降级为空历史: {ex}")
                    history = []
            else:
                # 没有可用的 DB 获取函数，降级为空历史（但建议实现）
                history = []
    except Exception as ex:
        logging.exception(f"history 构造异常，降级为空历史: {ex}")
        history = []

    # 在 history 基础上 append 本次 user 消息，形成发送给模型的完整上下文
    full_history = history + [{"role": "user", "content": request.message}]

    # 保存 user 消息到数据库（在构造好 full_history 后执行，避免读取历史时包含刚写入的一条造成重复）
    try:
        create_message(db, conversation_id, "user", request.message)
    except Exception as ex:
        logging.exception(f"保存 user 消息到 DB 失败（非致命）:{ex}")

    # ------------------------------------------------------------------------------

    async def event_generator():
        """
        event_generator 会不断 yield SSE 事件块（字符串），格式为 "data: <json>\n\n"。
        stream_chat_response 已保证返回 delta（新增后缀），但实现要兼容任意返回情况。
        """
        full_response = ""

        # 发一个 comment 以尽早触发代理 flush（对某些代理有帮助）
        yield ":\n\n"

        try:
            async for chunk in stream_chat_response(full_history):
                if not chunk:
                    continue
                # chunk 期望是“新增后缀”（delta）文本；追加并发送
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

            # 流结束，将完整 assistant 回答保存入 DB
            try:
                create_message(db, conversation_id, "assistant", full_response)
            except Exception as ep:
                logging.exception(f"保存 assistant 消息到 DB 失败（非致命）:{ep}")

            yield "data: [DONE]\n\n"
        except Exception as e:
            logging.exception("聊天流异常")
            error_msg = f"[Stream Error: {str(e)}]"
            try:
                create_message(db, conversation_id, "assistant", error_msg)
            except Exception as ep:
                logging.exception(f"保存错误消息到 DB 失败（非致命）:{ep}")
            yield f"data: {json.dumps({'content': error_msg}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    # 告诉中间代理不要缓冲或变换（提高流式交付的可能性）
    headers = {
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }

    return StreamingResponse(event_generator(), media_type="text/event-stream; charset=utf-8", headers=headers)
