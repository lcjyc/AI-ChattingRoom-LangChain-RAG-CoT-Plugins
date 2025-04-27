from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.ask import router as ask_router
from routes.agent import router as agent_router
from routes.upload import router as upload_router
from routes.files import router as files_router

app = FastAPI()

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加入路由
app.include_router(ask_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(files_router, prefix="/api")

