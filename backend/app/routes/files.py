from pathlib import Path
from fastapi.responses import JSONResponse
from fastapi import APIRouter

router = APIRouter()

UPLOAD_DIR = Path("uploaded_files")

@router.get("/files")
def list_uploaded_files():
    if not UPLOAD_DIR.exists():
        return []
    files = [str(UPLOAD_DIR / f.name).replace("\\", "/") for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return JSONResponse(content=files)
