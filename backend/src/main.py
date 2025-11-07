# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# src/main.py

import uvicorn
from fastapi import FastAPI
from src.api.v1.api import api_router

app = FastAPI(title="GenAI Backend")
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "GenAI Backend is running"}


# 添加这个入口点，让你可以直接在 IDE 中运行
if __name__ == "__main__":
    # 在开发时，建议开启 reload，这样修改代码后服务器会自动重启
    # host="0.0.0.0" 可以让局域网内的其他设备访问你的服务
    uvicorn.run(
        "src.main:app",  # 使用字符串形式，这是 reload=True 时推荐的方式
        host="0.0.0.0",
        port=6007,
        reload=True  # 开发时强烈推荐！
    )
