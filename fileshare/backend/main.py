import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# In Docker, we are in /app, and db is in /app/db
from db.functions import is_session_token_valid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SHARED_DIR = Path("files/shared")
SUPPORT_DIR = Path("files/support")

os.makedirs(SHARED_DIR, exist_ok=True)
os.makedirs(SUPPORT_DIR, exist_ok=True)

def check_auth(request: Request):
    token = request.cookies.get("token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not is_session_token_valid(token):
        raise HTTPException(status_code=401, detail="Not authorized. Valid support token required.")

@app.get("/shared")
def list_shared():
    files = [f.name for f in SHARED_DIR.iterdir() if f.is_file()]
    return {"files": files}

@app.get("/shared/{filename}")
def download_shared(filename: str):
    file_path = SHARED_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/support")
def list_support(request: Request):
    check_auth(request)
    files = [f.name for f in SUPPORT_DIR.iterdir() if f.is_file()]
    return {"files": files}

@app.get("/support/{filename}")
def download_support(filename: str, request: Request):
    check_auth(request)
    file_path = SUPPORT_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
