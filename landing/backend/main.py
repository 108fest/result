import os
import shutil
import sys
import mimetypes
import urllib.request
import threading
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.functions import create_new_user, cleanup_expired_users, is_session_token_valid

mimetypes.add_type('application/javascript', '.js')

app = FastAPI()

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src *;"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

orders = []

class LoginData(BaseModel):
    username: str = ""
    password: str = ""

@app.post("/api/login")
def login(data: LoginData):
    cleanup_expired_users(24)
    if data.password != "Sup3r_Str0ng_B0t_P4ssw0rd_999!":
        raise HTTPException(status_code=401, detail="There's nothing to get, try another route")
    new_user, new_session = create_new_user()
    return {"token": new_session.token}

@app.post("/api/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_url": f"/uploads/{file.filename}"}

def trigger_bot():
    try:
        urllib.request.urlopen("http://landing-bot:3000/visit?secret=AstraBotSecret99", timeout=2)
    except Exception as e:
        print(f"Failed to trigger bot: {e}")

@app.post("/api/order")
def create_order(company: str = Form(...), description: str = Form(...)):
    orders.append({"company": company, "description": description})
    threading.Thread(target=trigger_bot).start()
    return {"status": "success"}

@app.get("/api/admin/orders")
def get_orders(request: Request):
    cleanup_expired_users(24)
    token = request.cookies.get("token")
    if not token or not is_session_token_valid(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"orders": orders}

@app.get("/uploads/{filename}")
def get_upload(filename: str):
    file_path = f"uploads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "application/javascript" if filename.endswith(".js") else None
    return FileResponse(file_path, media_type=media_type)

@app.get("/{catchall:path}")
def serve_frontend(catchall: str):
    dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    file_path = os.path.join(dist_path, catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(dist_path, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built yet."}
