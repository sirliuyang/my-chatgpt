# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import jwt

from src.common.auth_handler import JWTHandler

logger = logging.getLogger(__name__)

EXPIRED_STATUS_CODE = 419
INVALID_TOKEN_STATUS = 420


class JWTBearer(HTTPBearer):
    """
    JWT Bearer认证类
    自动从请求头中提取和验证JWT token
    """

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        # 允许 OPTIONS 预检请求通过 — 不返回假 payload，直接返回 None
        if request.method == "OPTIONS":
            return None

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            # 未提供认证头
            raise HTTPException(
                status_code=INVALID_TOKEN_STATUS,
                detail="Invalid authorization code"
            )

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=INVALID_TOKEN_STATUS,
                detail="Invalid authentication scheme"
            )

        token = credentials.credentials

        try:
            # 假设 verify_jwt 要么返回 payload（dict），要么抛出 jwt.ExpiredSignatureError / jwt.InvalidTokenError
            payload = self.verify_jwt(token)
            # 可选：进一步校验 payload 必需字段，如 "user_id"
            if "user_id" not in payload:
                raise jwt.InvalidTokenError("missing user_id")
            return payload

        except jwt.ExpiredSignatureError as exc:
            # 记录审计日志（注意：不要记录 token）
            logging.info("Token expired for request %s %s: %s", request.method, request.url.path, str(exc))
            raise HTTPException(
                status_code=EXPIRED_STATUS_CODE,
                detail="Token expired",
                headers={
                    "WWW-Authenticate": "Bearer error='invalid_token' error_description='The access token expired'"
                }
            )

        except (jwt.InvalidTokenError, jwt.DecodeError) as exc:
            # token 无效（签名不对，结构错误等）
            logging.warning("Invalid token for request %s %s: %s", request.method, request.url.path, str(exc))
            raise HTTPException(
                status_code=INVALID_TOKEN_STATUS,
                detail="Invalid token",
                headers={
                    "WWW-Authenticate": "Bearer error='invalid_token' error_description='Token is invalid'"
                }
            )

        except Exception as exc:
            # 真正的未知错误 — 不吞掉，应当记录并返回 500，便于排错
            logging.exception("Unexpected error while verifying token for request %s %s", request.method,
                              request.url.path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=exc
            )

    @staticmethod
    def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        return JWTHandler.verify_token(token, token_type="access")


# 创建全局实例
jwt_bearer = JWTBearer()


# 依赖注入函数 - 获取当前用户
async def get_current_user(payload: Dict = Depends(jwt_bearer)) -> Dict[str, Any]:
    """
    从JWT token中获取当前用户信息

    Args:
        payload: JWT解码后的数据

    Returns:
        用户信息字典
    """
    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email")
    }
