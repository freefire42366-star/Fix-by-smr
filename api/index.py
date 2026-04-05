from fastapi import FastAPI, Request
import requests
import hashlib

# Vercel entry point
app = FastAPI()

U1 = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
U2 = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
U3 = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
U4 = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
U5 = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
U6 = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
U7 = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
U8 = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
U9 = "https://100067.connect.garena.com/bind/app/platform/info/get"
U10 = "https://100067.connect.garena.com/oauth/logout"
U11 = "https://clientbp.ggwhitehawk.com/GetPlayerCSRankingInfoByAccountID"
U12 = "https://clientbp.ggwhitehawk.com/GetFriendRequestList"
U13 = "https://clientbp.ggwhitehawk.com/RequestAddingFriend"
U14 = "https://clientbp.ggwhitehawk.com/RemoveFriend"
U15 = "https://clientbp.ggwhitehawk.com/ConfirmFriendRequest"
U16 = "https://clientbp.ggwhitehawk.com/DeclineFriendRequest"
U17 = "https://100067.msdk.garena.com/api/msdk/v2/info/pricing"

def gh(r: Request):
    ua = r.headers.get("user-agent", "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)")
    return {"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip"}

def hs(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

@app.get("/")
async def root():
    return {"status": "SUCCESS"}

@app.get("/api/request")
async def req(token: str, email: str, request: Request):
    d = {"app_id": "100067", "access_token": token, "email": email, "locale": "en_PK", "region": "PK"}
    return requests.post(U2, data=d, headers=gh(request)).json()

@app.get("/api/confirm-new")
async def b_new(token: str, email: str, otp: str, sc: str = "123456", request: Request):
    h = gh(request)
    v = requests.post(U3, data={"app_id": "100067", "access_token": token, "email": email, "otp": otp}, headers=h).json()
    vt = v.get("verifier_token")
    if not vt: return {"status": "FAIL", "res": v}
    d = {"app_id": "100067", "access_token": token, "verifier_token": vt, "email": email, "secondary_password": hs(sc)}
    return requests.post(U4, data=d, headers=h).json()

@app.get("/api/rebind")
async def b_re(token: str, email: str, otp: str, sc: str, request: Request):
    h = gh(request)
    v = requests.post(U3, data={"app_id": "100067", "access_token": token, "email": email, "otp": otp}, headers=h).json()
    i = requests.post(U5, data={"app_id": "100067", "access_token": token, "secondary_password": hs(sc)}, headers=h).json()
    vt, it = v.get("verifier_token"), i.get("identity_token")
    if not vt or not it: return {"status": "FAIL", "v": v, "i": i}
    d = {"app_id": "100067", "access_token": token, "identity_token": it, "verifier_token": vt, "email": email}
    return requests.post(U6, data=d, headers=h).json()

@app.get("/api/unbind")
async def ub(token: str, sc: str, request: Request):
    h = gh(request)
    i = requests.post(U5, data={"app_id": "100067", "access_token": token, "secondary_password": hs(sc)}, headers=h).json()
    it = i.get("identity_token")
    if not it: return i
    return requests.post(U7, data={"app_id": "100067", "access_token": token, "identity_token": it}, headers=h).json()

@app.get("/api/info")
async def info(token: str, request: Request):
    h = gh(request)
    b = requests.get(U1, params={"app_id": "100067", "access_token": token}, headers=h).json()
    uid = b.get("uid") or "0"
    r = requests.get(U11, params={"access_token": token, "target_account_id": uid}, headers=h).json()
    return {"bind": b, "rank": r}

@app.get("/api/friends")
async def fr(token: str, mode: str, target: str = None, request: Request):
    h = gh(request)
    u_m = {"list": U12, "add": U13, "remove": U14, "accept": U15, "decline": U16}
    u = u_m.get(mode)
    p = {"access_token": token}
    if target: p["target_account_id"] = target
    return requests.get(u, params=p, headers=h).json()

@app.get("/api/utils")
async def ut(token: str, type: str, request: Request):
    h = gh(request)
    if type == "plat": return requests.get(U9, params={"access_token": token}, headers=h).json()
    if type == "topup": return requests.get(U17, params={"access_token": token}, headers=h).json()
    if type == "cancel": return requests.post(U8, data={"app_id": "100067", "access_token": token}, headers=h).json()
    return {"err": "err"}

@app.get("/api/revoke")
async def rv(token: str, request: Request):
    return requests.get(U10, params={"access_token": token, "refresh_token": "1380dcb63ab3a077dc05bdf0b25ba4497c403a5b4eae96d7203010eafa6c83a8"}, headers=gh(request)).text
