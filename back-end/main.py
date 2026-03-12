import os
import uuid
import time
import requests
import uvicorn

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from firebase_admin import auth, credentials, initialize_app, _apps
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# =========================
# Firebase init
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "serviceAccountKey.json")
PROJECT_ID = "texty-ee5ff"

if not _apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    initialize_app(cred)

app = FastAPI()

# זיכרון זמני לפרוטוטייפ בלבד
verification_store = {}

SCOPES = [
    "https://www.googleapis.com/auth/identitytoolkit",
    "https://www.googleapis.com/auth/cloud-platform",
]

# =========================
# Models
# =========================
class SendCodeBody(BaseModel):
    phone: str
    recaptcha_token: str | None = None
    captcha_response: str | None = None
    client_type: str | None = None
    recaptcha_version: str | None = None


class VerifyCodeBody(BaseModel):
    phone: str
    code: str
    verification_id: str


# =========================
# Helpers
# =========================
def get_access_token() -> str:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    creds.refresh(Request())
    return creds.token


def normalize_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        raise ValueError("Phone must be in E.164 format, e.g. +972501234567")
    return phone


def build_send_code_payload(body: SendCodeBody, phone: str) -> dict:
    payload = {
        "phoneNumber": phone
    }

    # מצב רגיל: recaptchaToken
    if body.recaptcha_token:
        payload["recaptchaToken"] = body.recaptcha_token

    # מצב של reCAPTCHA Enterprise
    if body.captcha_response:
        payload["captchaResponse"] = body.captcha_response
        payload["clientType"] = body.client_type or "CLIENT_TYPE_WEB"
        payload["recaptchaVersion"] = body.recaptcha_version or "RECAPTCHA_ENTERPRISE"

    return payload


# =========================
# Routes
# =========================
@app.get("/")
def root():
    return {"ok": True, "message": "API is running"}


@app.post("/auth/send-code")
def send_code(body: SendCodeBody):
    try:
        phone = normalize_phone(body.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not body.recaptcha_token and not body.captcha_response:
        raise HTTPException(
            status_code=400,
            detail="Missing app verification token: send recaptcha_token or captcha_response"
        )

    access_token = get_access_token()
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendVerificationCode"

    payload = build_send_code_payload(body, phone)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=20)

    if resp.status_code != 200:
        try:
            error_json = resp.json()
        except Exception:
            error_json = {"raw_error": resp.text}
        raise HTTPException(status_code=resp.status_code, detail=error_json)

    data = resp.json()
    session_info = data.get("sessionInfo")

    if not session_info:
        raise HTTPException(status_code=500, detail="Missing sessionInfo in Firebase response")

    verification_id = str(uuid.uuid4())

    verification_store[verification_id] = {
        "phone": phone,
        "session_info": session_info,
        "created_at": time.time(),
    }

    return {
        "ok": True,
        "verification_id": verification_id
    }


@app.post("/auth/verify-code")
def verify_code(body: VerifyCodeBody):
    record = verification_store.get(body.verification_id)

    if not record:
        raise HTTPException(status_code=400, detail="Invalid verification_id")

    try:
        phone = normalize_phone(body.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if record["phone"] != phone:
        raise HTTPException(status_code=400, detail="Phone mismatch")

    access_token = get_access_token()
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPhoneNumber"

    payload = {
        "sessionInfo": record["session_info"],
        "code": body.code
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=20)

    if resp.status_code != 200:
        try:
            error_json = resp.json()
        except Exception:
            error_json = {"raw_error": resp.text}

        return {
            "success": False,
            "exists": False,
            "firebase_error": error_json
        }

    exists = False
    try:
        auth.get_user_by_phone_number(phone)
        exists = True
    except Exception:
        exists = False

    verification_store.pop(body.verification_id, None)

    return {
        "success": True,
        "exists": exists
    }


# =========================
# Run server
# In order to see what IP Addres the Server
# uses, please type ipconfig into the comand line
# then in the IPV4 section will be the current IP.
# =========================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
                port=8000, reload=True)