# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import json
import logging

from fastapi import APIRouter, Request, Depends
# 在文件顶部确保导入以下
from fastapi import HTTPException
from pydantic_ai.ag_ui import handle_ag_ui_request
from pydantic_ai.ui.ag_ui import AGUIAdapter

# ToolReturn is optional if you want to wrap results; ToolReturn / ModelRetry can also be used if needed

from src.services.agentic_service import get_or_create_agent
from src.common.auth_bearer import get_current_user
from typing import Dict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agui", tags=["agui"])


@router.post("/agent", response_model=None)
async def agui_agent_endpoint(
        request: Request,
        current_user: Dict = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        body = await request.json()
        logging.info(f"AG-UI /agent body: {json.dumps(body, ensure_ascii=False)}")
    except Exception as e:
        logging.warning(f"Failed to log body: {e}")

    agent = get_or_create_agent()

    try:
        # handle_ag_ui_request 会返回 StreamingResponse
        response = await handle_ag_ui_request(request=request, agent=agent)
        return response
    except Exception as e:
        logging.exception("AG-UI run failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deferred_results")
async def agui_deferred_results(
        request: Request,
        current_user: Dict = Depends(get_current_user),
):
    try:
        request_json = await request.json()
        logging.info(f"Request AG-UI /deferred_results, json: {json.dumps(request_json, ensure_ascii=False)}")
    except Exception as e:
        logging.exception(f"Failed to parse deferred_results body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    agent = get_or_create_agent()

    # 关键修改：处理 deferred_results 中的工具调用批准
    deferred_results = request_json.get('deferred_results', [])

    # 为每个批准的工具调用执行实际的工具函数
    for deferred in deferred_results:
        tool_call_id = deferred.get('tool_call_id')
        approval = deferred.get('approval')

        if not approval:
            logging.info(f"Tool call {tool_call_id} was denied")
            continue

        # 从前端传来的请求中找到对应的工具调用信息
        # 注意：你需要在首次 /agent 调用时保存工具调用的参数
        # 或者从 run context 中获取
        logging.info(f"Tool call {tool_call_id} approved, will be executed by AG-UI framework")

    try:
        # AGUIAdapter.dispatch_request 会处理工具结果的返回
        return await AGUIAdapter.dispatch_request(request, agent=agent)
    except Exception as e:
        logging.exception("AG-UI deferred_results dispatch failed")
        raise HTTPException(status_code=500, detail=str(e))
