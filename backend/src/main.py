# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging
import uvicorn
from fastapi import FastAPI
from src.api.v1.api import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="GenAI Backend")
app.include_router(api_router)

logger.info("GenAI Backend API initialized")


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "GenAI Backend is running"}


# 添加这个入口点，让你可以直接在 IDE 中运行
if __name__ == "__main__":
    logger.info("Starting GenAI Backend server")
    # 在开发时，建议开启 reload，这样修改代码后服务器会自动重启
    # uvicorn.run(
    #     "src.main:app",  # 使用字符串形式，这是 reload=True 时推荐的方式
    #     host="0.0.0.0",
    #     port=7007,
    #     reload=True  # 开发时强烈推荐！
    # )
    uvicorn.run(app, host="0.0.0.0", port=7007)
