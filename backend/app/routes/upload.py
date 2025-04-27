import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from vectorstore import create_vectorstore_from_file

router = APIRouter()

# 儲存路徑
UPLOAD_DIR = "uploaded_files"
VECTORSTORE_DIR = "vectorstores"

# 確保路徑存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

def get_unique_filename(directory: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}({counter}){ext}"
        counter += 1
    return new_filename

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 自動重新命名重複檔案
        unique_filename = get_unique_filename(UPLOAD_DIR, file.filename)
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # 儲存檔案
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 向量儲存資料夾
        vectorstore_path = os.path.join(VECTORSTORE_DIR, "default")

        # 建立向量資料庫
        create_vectorstore_from_file(file_path, embed_type="openai", save_path=vectorstore_path)

        return JSONResponse(content={
            "status": "success",
            "message": "File uploaded and vectorstore created",
            "file_name": unique_filename
        })

    except Exception as e:
        print(f"[ERROR] Upload Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
