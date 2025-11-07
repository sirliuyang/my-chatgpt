# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import FastAPI
from src.api.v1.api import api_router

app = FastAPI(title="GenAI Backend")
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "GenAI Backend is running"}
