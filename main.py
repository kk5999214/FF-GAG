from fastapi import FastAPI, HTTPException
import random
import hashlib
import hmac
from urllib.parse import urlencode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests

app = FastAPI(title="FF Guest Account Forge")

def forge_guest(region: str):
    """Core logic to forge a new Free Fire Guest Account."""
    s = b'2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3'
    cid = "100067"
    ua = "GarenaMSDK/4.0.19P9(SM-S908E; Android 11; en; IN)"
    session = requests.Session()
    
    def e(x):
        k = [0,0,0,2,0,1,7,0,0,0,0,0,2,0,1,7,0,0,0,0,0,2,0,1,7,0,0,0,0,0,2,0]
        return bytes(b ^ k[i % len(k)] ^ 48 for i, b in enumerate(x.encode()))
    
    def aes(h):
        c = AES.new(b"Yg&tc%DEuh6%Zc^8", AES.MODE_CBC, b"6oyZDr22E3ychjM%")
        return c.encrypt(pad(bytes.fromhex(h), 16)).hex()
    
    def ev(n):
        r = bytearray()
        while n:
            b = n & 0x7F
            n >>= 7
            r.append(b | (0x80 if n else 0))
        return bytes(r)
    
    def ef(f,v):
        if type(v) == int: return ev((f<<3)|0)+ev(v)
        b = v.encode() if type(v)==str else v
        return ev((f<<3)|2)+ev(len(b))+b
    
    def ep(d):
        p = bytearray()
        for k in sorted(d): p.extend(ef(k,d[k]))
        return p
    
    # 1. Generate Fake Device & Password
    pwd = str(random.randint(1000000000,9999999999))
    ph = hashlib.sha256(pwd.encode()).hexdigest().upper()
    
    bd = urlencode({'password':ph,'client_type':'2','source':'2','app_id':cid})
    hd = {'User-Agent':ua,'Authorization':f"Signature {hmac.new(s,bd.encode(),hashlib.sha256).hexdigest()}",'Content-Type':'application/x-www-form-urlencoded'}
    
    # 2. Register Guest
    r1 = session.post('https://ffmconnect.live.gop.garenanow.com/oauth/guest/register', data=bd, headers=hd, timeout=10)
    if r1.status_code != 200: 
        return None, None, f"Register failed: {r1.text}"
    
    uid = r1.json().get("uid")
    if not uid: 
        return None, None, "No UID in register response"
    
    # 3. Grant Token
    td = {'uid':str(uid),'password':ph,'response_type':"token",'client_type':"2",'client_secret':s.decode(),'client_id':cid}
    r2 = session.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=td, headers={'User-Agent':ua}, timeout=10)
    if r2.status_code != 200: 
        return None, None, f"Token grant failed: {r2.text}"
    
    j = r2.json()
    at = j.get("access_token")
    oid = j.get("open_id") or j.get("openId") or j.get("openid")
    if not at or not oid: 
        return None, None, "Missing access_token or open_id"
    
    # 4. Major Register (The Regional Lock-in)
    pf = {1:f"0xMe{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in str(random.randint(1,9999)))}",2:at,3:oid,5:102000007,6:4,7:1,13:1,14:e(oid),15:region,16:1}
    ed = bytes.fromhex(aes(ep(pf).hex()))
    
    hs = {
        "Authorization": f"Bearer {at}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53", # Keep this matched to current live patch
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(ed)),
        "User-Agent": ua,
        "Host": "loginbp.ggblueshark.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    
    r3 = session.post('https://loginbp.ggblueshark.com/MajorRegister', data=ed, headers=hs, timeout=10)
    session.close()
    
    if r3.status_code == 200:
        return str(uid), ph, "Success"
    return None, None, f"Major Register failed: {r3.status_code} - {r3.text}"


@app.get("/generate")
def api_generate_account(region: str = "BR"):
    """
    Hit this endpoint to forge a new account for a specific region.
    Example: /generate?region=SG
    """
    region = region.upper()
    uid, password, msg = forge_guest(region)
    
    if not uid:
        raise HTTPException(status_code=500, detail=f"Forge Failed: {msg}")
        
    return {
        "success": True,
        "region": region,
        "uid": uid,
        "password": password,
        "message": "Identity forged successfully."
    }

@app.get("/")
def root():
    return {"status": "Forge API Online. Use /generate?region=BR"}
  
