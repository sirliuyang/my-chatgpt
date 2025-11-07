# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.OPENAI_API_KEY:  # Reuse OPENAI_API_KEY as simple auth, or add separate
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return api_key


def verify_api_key(api_key: str):
    """Simple API key verification."""
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
