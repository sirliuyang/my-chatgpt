# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from fastapi import APIRouter

router = APIRouter(tags=["test"])


@router.get("/test", response_model=None)
async def test():
    return {"message": "Hello World"}
