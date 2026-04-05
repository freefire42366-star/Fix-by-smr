import requests
import hashlib
from fastapi import FastAPI, Request

app = FastAPI()

# --- URL DATABASE (A to Z) ---
URL_BIND_INFO = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
URL_SEND_OTP  = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
URL_VERIFY_OTP = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
URL_BIND_REQ  = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
URL_VERIFY_ID = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
URL_REBIND_REQ = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
URL_UNBIND_REQ = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
URL_CANCEL_REQ = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
URL_PLATFORM  = "https://100067.connect.garena.com/bind/app/platform/info/get"
URL_LOGOUT    = "https://100067.connect.garena.com/oauth/logout"
URL_RANK      = "https://clientbp.ggwhitehawk.com/GetPlayerCSRankingInfoByAccountID"
URL_F_LIST    = "https://clientbp.ggwhitehawk.com/GetFriendRequestList"
URL_F_ADD     = "https://clientbp.ggwhitehawk.com/RequestAddingFriend"
URL_F_REM     = "https://clientbp.ggwhitehawk.com/RemoveFriend"
URL_F_ACC     = "https://clientbp.ggwhitehawk.com/ConfirmFriendRequest"
URL_F_DEC     = "https://clientbp.ggwhitehawk.com/DeclineFriendRequest"
URL_TOPUP     = "https://100067.msdk.garena.com/api/msdk/v2/info/pricing"
URL_BIND_DEL  = "https://clientbp.ggwhitehawk.com/BindDelete"

AID = "100067"
REF = "1380dcb63ab3a077dc05bdf0b25ba4497c403a5b4eae96d7203010eafa6c83a8"

def get_h(r: Request):
    ua = r.headers.get("user-agent", "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)")
    return {"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip"}

def hs(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

@app.get("/")
async def root():
    return {"status": "SUCCESS", "msg": "SAMEER-SUPREME-V11-PRO-LIVE"}

@app.get("/api/request")
async def request_otp(token: str, email: str, request: Request):
    p = {"app_id": AID, "access_token": token, "email": email, "locale": "en_PK", "region": "PK"}
    return requests.post(URL_SEND_OTP, data=p, headers=get_h(request)).json()

@app.get("/api/confirm-new")
async def bind_new_account(token: str, email: str, otp: str, sc: str = "123456", request: Request):
    h = get_h(request)
    v = requests.post(URL_VERIFY_OTP, data={"app_id": AID, "access_token": token, "email": email, "otp": otp}, headers=h).json()
    vt = v.get("verifier_token")
    if not vt: return {"status": "ERROR", "garena": v}
    p = {"app_id": AID, "access_token": token, "verifier_token": vt, "email": email, "secondary_password": hs(sc)}
    return requests.post(URL_BIND_REQ, data=p, headers=h).json()

@app.get("/api/rebind")
async def change_email(token: str, email: str, otp: str, sc: str, request: Request):
    h = get_h(request)
    v = requests.post(URL_VERIFY_OTP, data={"app_id": AID, "access_token": token, "email": email, "otp": otp}, headers=h).json()
    i = requests.post(URL_VERIFY_ID, data={"app_id": AID, "access_token": token, "secondary_password": hs(sc)}, headers=h).json()
    vt, it = v.get("verifier_token"), i.get("identity_token")
    if not vt or not it: return {"status": "FAILED", "v_res": v, "i_res": i}
    p = {"app_id": AID, "access_token": token, "identity_token": it, "verifier_token": vt, "email": email}
    return requests.post(URL_REBIND_REQ, data=p, headers=h).json()

@app.get("/api/unbind")
async def remove_email(token: str, sc: str, request: Request):
    h = get_h(request)
    i = requests.post(URL_VERIFY_ID, data={"app_id": AID, "access_token": token, "secondary_password": hs(sc)}, headers=h).json()
    it = i.get("identity_token")
    if not it: return i
    return requests.post(URL_UNBIND_REQ, data={"app_id": AID, "access_token": token, "identity_token": it}, headers=h).json()

@app.get("/api/info")
async def get_account_info(token: str, request: Request):
    h = get_h(request)
    bind_data = requests.get(URL_BIND_INFO, params={"app_id": AID, "access_token": token}, headers=h).json()
    uid = bind_data.get("uid") or "0"
    rank_data = requests.get(URL_RANK, params={"access_token": token, "target_account_id": uid}, headers=h).json()
    return {"bind": bind_data, "rank": rank_data}

@app.get("/api/friends")
async def friends_manager(token: str, mode: str, target: str = None, request: Request):
    h = get_h(request)
    urls = {"list": URL_F_LIST, "add": URL_F_ADD, "remove": URL_F_REM, "accept": URL_F_ACC, "decline": URL_F_DEC}
    url = urls.get(mode)
    p = {"access_token": token}
    if target: p["target_account_id"] = target
    return requests.get(url, params=p, headers=h).json()

@app.get("/api/utils")
async def account_utils(token: str, type: str, request: Request):
    h = get_h(request)
    if type == "plat": return requests.get(URL_PLATFORM, params={"access_token": token}, headers=h).json()
    if type == "topup": return requests.get(URL_TOPUP, params={"access_token": token}, headers=h).json()
    if type == "cancel": return requests.post(URL_CANCEL_REQ, data={"app_id": AID, "access_token": token}, headers=h).json()
    if type == "del_bind": return requests.post(URL_BIND_DEL, data={"access_token": token}, headers=h).json()
    return {"err": "Invalid Type"}

@app.get("/api/revoke")
async def revoke_access(token: str, request: Request):
    r = requests.get(URL_LOGOUT, params={"access_token": token, "refresh_token": REF}, headers=get_h(request))
    return {"status": "Logged Out", "response": r.text}

@app.get("/api/convert")
async def eat_to_access(eat: str):
    return {"link": f"https://api-otrss.garena.com/support/callback/?access_token={eat}"}
