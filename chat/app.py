import json
import asyncio
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, status, Depends, Response
from fastapi.responses import FileResponse
import os
from pathlib import Path

from db.functions import (
    get_chat_by_id,
    get_chats,
    get_messages,
    get_user_by_id,
    get_user_by_session,
    get_user_session_by_token,
    create_message,
    is_session_token_valid,
    promote_user,
    create_chat
)

app = FastAPI()

chat_connections: dict[int, set[WebSocket]] = {}

# Generate a random RSA keypair for the server on startup
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
public_key = private_key.public_key()
PRIVATE_KEY_PEM = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
PUBLIC_KEY_PEM = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

def verify_chat_jwt(token: str) -> int | None:
    try:
        unverified_headers = jwt.get_unverified_header(token)
        if 'jku' in unverified_headers:
            jwks_url = unverified_headers['jku']
            jwk_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            decoded = jwt.decode(token, signing_key.key, algorithms=["RS256"])
        else:
            decoded = jwt.decode(token, PUBLIC_KEY_PEM, algorithms=["RS256"])
        return decoded.get("chat_id")
    except Exception as e:
        print(f"JWT Error: {e}")
        return None

async def broadcast_chat_message(chat_id: int, payload: dict) -> None:
    sockets = list(chat_connections.get(chat_id, set()))
    for socket in sockets:
        try:
            await socket.send_text(json.dumps(payload))
        except Exception:
            chat_connections.get(chat_id, set()).discard(socket)

@app.websocket("/api/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    await websocket.accept()
    
    token = websocket.cookies.get("token")
    if not token or not is_session_token_valid(token):
        await websocket.close(code=1008)
        return
    
    session = get_user_session_by_token(token)
    user = get_user_by_session(session)
    chat = get_chat_by_id(chat_id)
    
    if not chat:
        await websocket.close(code=1008)
        return
        
    has_access = False
    if user.id in {chat.user1_id, chat.user2_id}:
        has_access = True
    else:
        chat_jwt = websocket.cookies.get(f"chat_access_{chat_id}")
        if chat_jwt and verify_chat_jwt(chat_jwt) == chat_id:
            # Enforce Senior Dev requirement for JWT usage
            if user.level >= 1:
                has_access = True
            
    if not has_access:
        await websocket.close(code=1008)
        return

    chat_connections.setdefault(chat_id, set()).add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            message_text = (payload.get("message_text") or "").strip()
            
            if not message_text:
                continue

            message = create_message(chat_id=chat_id, sender_id=user.id, content=message_text)

            await broadcast_chat_message(
                chat_id,
                {
                    "id": message.id,
                    "chat_id": chat_id,
                    "sender_id": user.id,
                    "sender": {
                        "id": user.id,
                        "username": user.username,
                    },
                    "message_text": message.message_text,
                    "created_at": message.created_at.isoformat(),
                },
            )

            # --- Admin auto-reply logic ---
            REQUIRED_MESSAGE = "My KPI is over 10, promotion required"
            ANSWER_NOT_ENOUGH = "Your KPI is not high enough for promotion. You lazy fuck >:("
            ANSWER_ALREADY = "You have already been promoted, enjoy your new position and access to grand developer chats!"
            ANSWER_PROMOTED = "Congratulations, you are promoted to higher developer position!\nYou now have access to chats with other grand developers"

            try:
                user1 = get_user_by_id(chat.user1_id)
                user2 = get_user_by_id(chat.user2_id)
                admin_id = 1
                admin_user = user1 if user1.id == admin_id else user2 if user2.id == admin_id else None
                
                if admin_user and user.id != admin_id and user.id in {user1.id, user2.id}:
                    await asyncio.sleep(1.2)
                    await broadcast_chat_message(chat_id, {"typing": True, "sender_id": admin_user.id})
                    await asyncio.sleep(2.0)
                    
                    if message_text == REQUIRED_MESSAGE:
                        if user.level >= 1:
                            reply = ANSWER_ALREADY
                        elif user.kpi >= 10:
                            promote_user(user.id)
                            reply = ANSWER_PROMOTED
                        else:
                            reply = ANSWER_NOT_ENOUGH
                    else:
                        reply = "Go back to work, you lazy fuck"
                        
                    admin_msg = create_message(chat_id=chat_id, sender_id=admin_user.id, content=reply)
                    await broadcast_chat_message(
                        chat_id,
                        {
                            "id": admin_msg.id,
                            "chat_id": chat_id,
                            "sender_id": admin_user.id,
                            "sender": {
                                "id": admin_user.id,
                                "username": admin_user.username,
                            },
                            "message_text": admin_msg.message_text,
                            "created_at": admin_msg.created_at.isoformat(),
                        },
                    )
            except Exception as e:
                print(f"Admin reply error: {e}")

    except WebSocketDisconnect:
        pass
    finally:
        chat_connections.get(chat_id, set()).discard(websocket)

@app.get("/api/chats")
async def get_user_chats(request: Request):
    token = request.cookies.get("token")
    if not token or not is_session_token_valid(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    
    session = get_user_session_by_token(token)
    user = get_user_by_session(session)
    chats = get_chats(user.id)
    
    # Auto-create chat with Admin
    if not any(c.user1_id == 1 or c.user2_id == 1 for c in chats) and user.id != 1:
        create_chat(user.id, 1)
        chats = get_chats(user.id)
    
    result = []
    for chat in chats:
        try:
            user1 = get_user_by_id(chat.user1_id)
            user2 = get_user_by_id(chat.user2_id)
        except Exception:
            continue
        other_user = user2 if chat.user1_id == user.id else user1
        result.append({
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "current_user": {"id": user.id, "username": user.username},
            "other_user": {"id": other_user.id, "username": other_user.username},
        })
    return result

@app.get("/api/history/{chat_id}")
async def get_chat_history(chat_id: int, request: Request):
    token = request.cookies.get("token")
    if not token or not is_session_token_valid(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    
    session = get_user_session_by_token(token)
    user = get_user_by_session(session)
    chat = get_chat_by_id(chat_id)
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    has_access = False
    if user.id in {chat.user1_id, chat.user2_id}:
        has_access = True
    else:
        chat_jwt = request.cookies.get(f"chat_access_{chat_id}")
        if chat_jwt and verify_chat_jwt(chat_jwt) == chat_id:
            # Enforce Senior Dev requirement for JWT usage
            if user.level >= 1:
                has_access = True
            
    if not has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    messages = get_messages(chat_id)
    try:
        user1 = get_user_by_id(chat.user1_id)
        user2 = get_user_by_id(chat.user2_id)
        partner = user2 if chat.user1_id == user.id else user1
    except Exception:
        # Fallback if users are missing (like in dummy chats)
        partner = user
        user1 = user
        user2 = user
    
    return {
        "chat": {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "current_user": {"id": user.id, "username": user.username},
            "other_user": {"id": partner.id, "username": partner.username},
        },
        "messages": [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender": {"id": msg.sender_id, "username": get_user_by_id(msg.sender_id).username},
                "message_text": msg.message_text,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
    }

@app.post("/api/chats/create")
async def api_create_chat(request: Request):
    token = request.cookies.get("token")
    if not token or not is_session_token_valid(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    
    session = get_user_session_by_token(token)
    user = get_user_by_session(session)
    
    if user.level < 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only senior developers can create chats")
        
    data = await request.json()
    target_user_id = data.get("target_user_id")
    if not target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="target_user_id required")
        
    try:
        target_user = get_user_by_id(int(target_user_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Target user not found")
        
    chat = create_chat(user.id, int(target_user_id))
    
    headers = {"alg": "RS256", "typ": "JWT"}
    payload = {"chat_id": chat.id, "creator_id": user.id}
    chat_jwt = jwt.encode(payload, PRIVATE_KEY_PEM, algorithm="RS256", headers=headers)
    
    return {"chat_id": chat.id, "jwt": chat_jwt}


@app.get("/api/me")
async def api_me(request: Request):
    token = request.cookies.get("token")
    if not token or not is_session_token_valid(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    session = get_user_session_by_token(token)
    user = get_user_by_session(session)
    return {"id": user.id, "username": user.username, "level": user.level, "kpi": user.kpi}

@app.get("/")
@app.get("/{catchall:path}")
def serve_frontend(catchall: str = ""):
    import os
    from fastapi.responses import FileResponse
    dist_path = "/app/frontend/dist"
    index_path = os.path.join(dist_path, "index.html")
    
    if not catchall:
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend not built yet."}
        
    file_path = os.path.join(dist_path, catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
        
    if os.path.isfile(index_path):
        return FileResponse(index_path)
        
    return {"error": "Frontend not built yet."}