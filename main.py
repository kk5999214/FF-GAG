from fastapi import FastAPI, HTTPException
import hmac
import hashlib
import requests
import string
import random
import codecs
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="BITTU__DEV Account Forge API")

# ==========================================
# BITTU__DEV : CORE ENCRYPTION
# ==========================================
hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
aes_key = bytes.fromhex(hex_key)

def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F ; N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))           
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))           
    return packet

def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    K = AES.new(key , AES.MODE_CBC , iv)
    R = K.encrypt(pad(Z , AES.block_size))
    return bytes.fromhex(R.hex())

def encode_string(original):
    keystream = [0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
                 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30]
    encoded = ""
    for i in range(len(original)):
        orig_byte = ord(original[i])
        key_byte = keystream[i % len(keystream)]
        encoded += chr(orig_byte ^ key_byte)
    return {"field_14": encoded}

def to_unicode_escaped(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

# ==========================================
# BITTU__DEV : FORGE ENGINE
# ==========================================
def execute_forge(region: str, name_pref: str):
    # 1. Exact 12-Character Name Generator
    if len(name_pref) >= 12:
        name = name_pref[:12]
    else:
        needed_digits = 12 - len(name_pref)
        random_digits = ''.join(random.choice('0123456789') for _ in range(needed_digits))
        name = name_pref + random_digits
    
    # 2. Setup Device & Password
    random_part = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9)).upper()
    password = f"BITTU_{random_part}"
    
    ph = hashlib.sha256(password.encode()).hexdigest().upper()
    data = f"password={password}&client_type=2&source=2&app_id=100067"
    signature = hmac.new(aes_key, data.encode('utf-8'), hashlib.sha256).hexdigest()

    # 3. Register Guest
    reg_url = "https://100067.connect.garena.com/oauth/guest/register"
    reg_headers = {
        "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
        "Authorization": "Signature " + signature,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }

    try:
        r1 = requests.post(reg_url, headers=reg_headers, data=data, verify=False, timeout=10)
        if r1.status_code != 200:
            return {"error": f"Register Failed: {r1.text}"}
        uid = r1.json().get('uid')
        if not uid:
            return {"error": "UID not returned in register payload."}
    except Exception as e:
        return {"error": f"Request Failed: {str(e)}"}

    # 4. Token Grant
    token_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    token_body = {
        "uid": uid,
        "password": ph,
        "response_type": "token",
        "client_type": "2",
        "client_secret": aes_key,
        "client_id": "100067"
    }
    
    try:
        r2 = requests.post(token_url, headers=reg_headers, data=token_body, verify=False, timeout=10)
        if r2.status_code != 200:
            return {"error": f"Token Grant Failed: {r2.text}"}
            
        open_id = r2.json().get('open_id')
        access_token = r2.json().get("access_token")
    except Exception as e:
        return {"error": f"Token Grant Error: {str(e)}"}

    # 5. Major Register (Region Locking)
    encoded_dict = encode_string(open_id)
    field = codecs.decode(to_unicode_escaped(encoded_dict['field_14']), 'unicode_escape').encode('latin1')
    
    payload = {
        1: name,
        2: access_token,
        3: open_id,
        5: 102000007,
        6: 4,
        7: 1,
        13: 1,
        14: field,
        15: region.lower() if region.lower() in ["ar", "en", "hi", "id", "vi", "th", "bn", "ur", "zh", "ru", "es", "pt"] else "en",
        16: 1,
        17: 1
    }

    payload_hex = CrEaTe_ProTo(payload).hex()
    encrypted_payload = bytes.fromhex(E_AEs(payload_hex).hex())

    major_headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",   
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4."
    }

    try:
        r3 = requests.post("https://loginbp.ggblueshark.com/MajorRegister", headers=major_headers, data=encrypted_payload, verify=False, timeout=10)
        if r3.status_code != 200:
            return {"error": f"Major Register Failed: {r3.status_code} - {r3.text}"}
    except Exception as e:
        return {"error": f"Major Register Error: {str(e)}"}

    # ==========================================
    # BITTU__DEV : FINAL PAYLOAD RETURN
    # ==========================================
    return {
        "success": True,
        "owner": "BITTU__DEV",
        "region": region.upper(),
        "uid": str(uid),
        "password": password,
        "game_name": name,
        "tokens": {
            "access_token": access_token,
            "open_id": open_id
        }
    }

# ==========================================
# FASTAPI ENDPOINTS
# ==========================================
@app.get("/api/gen")
def api_generate_account(reg: str = "IND", name_pref: str = "BITTU"):
    """Forge a new Free Fire Guest Account instantly."""
    
    result = execute_forge(reg.upper(), name_pref)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

@app.get("/")
def root():
    return {
        "status": "BITTU__DEV Forge API Live 💀",
        "endpoint": "/api/gen?reg=IND&name_pref=BITTU.DEV"
    }
