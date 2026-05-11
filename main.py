from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import string
import random
import codecs
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(
    title="BITTU__DEV Ghost Factory",
    description="High-Speed Asynchronous Auto-Activating Account Generator 💀",
    version="3.0"
)

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
# 11-REGION ROUTING ARCHITECTURE
# ==========================================
REGION_MAP = {
    "IND": {"login": "https://loginbp.ggpolarbear.com", "lang": "hi"},
    "BD":  {"login": "https://loginbp.ggpolarbear.com", "lang": "bn"},
    "ME":  {"login": "https://loginbp.ggpolarbear.com", "lang": "ar"},
    "PK":  {"login": "https://loginbp.ggpolarbear.com", "lang": "ur"},
    "BR":  {"login": "https://loginbp.ggpolarbear.com", "lang": "pt"},
    "NA":  {"login": "https://loginbp.ggpolarbear.com", "lang": "en"},
    "VN":  {"login": "https://loginbp.ggpolarbear.com", "lang": "vi"},
    "SG":  {"login": "https://loginbp.ggpolarbear.com", "lang": "en"},
    "ID":  {"login": "https://loginbp.ggpolarbear.com", "lang": "id"},
    "RU":  {"login": "https://loginbp.ggpolarbear.com", "lang": "ru"},
    "TH":  {"login": "https://loginbp.ggpolarbear.com", "lang": "th"},
    "GHOST": {"login": "https://loginbp.ggblueshark.com", "lang": "en"}
}

# ==========================================
# BITTU__DEV : ASYNC FORGE ENGINE
# ==========================================
async def execute_forge(region: str, name_pref: str):
    region_key = region.upper()
    if region_key not in REGION_MAP:
        region_key = "GHOST"
    
    login_url = REGION_MAP[region_key]["login"]
    lang = REGION_MAP[region_key]["lang"]

    super_digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
    if len(name_pref) >= 12:
        name = name_pref[:12]
    else:
        needed_digits = 12 - len(name_pref)
        name = name_pref + ''.join(random.choice(super_digits) for _ in range(needed_digits))
    
    random_part = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9)).upper()
    password = f"BITTU__DEV-{random_part}"

    # Asynchronous HTTP Client Context
    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
        
        # 1. Register Guest (WAF Bypass)
        reg_url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
        reg_payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
        reg_headers = {
            "User-Agent": "garenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
            "Accept": "application/json", 
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            r1 = await client.post(reg_url, headers=reg_headers, json=reg_payload)
            if r1.status_code != 200: return {"error": f"Register Failed: {r1.text}"}
            uid = r1.json().get("data", {}).get("uid")
            if not uid: return {"error": "UID missing."}
        except Exception as e: return {"error": f"Request Failed: {str(e)}"}

        # 2. Token Grant
        token_headers = {
            "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)"
        }
        token_body = {
            "uid": uid, "password": password, "response_type": "token",
            "client_type": "2", "client_secret": aes_key.decode('latin1'), "client_id": "100067"
        }
        
        try:
            r2 = await client.post("https://100067.connect.garena.com/oauth/guest/token/grant", headers=token_headers, data=token_body)
            open_id = r2.json().get('open_id')
            access_token = r2.json().get("access_token")
        except Exception as e: return {"error": f"Token Grant Error: {str(e)}"}

        # 3. Major Register
        encoded_dict = encode_string(open_id)
        field = codecs.decode(to_unicode_escaped(encoded_dict['field_14']), 'unicode_escape').encode('latin1')
        
        payload = {
            1: name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 13: 1, 14: field,
            15: lang, 16: 1, 17: 1
        }
        encrypted_payload = bytes.fromhex(E_AEs(CrEaTe_ProTo(payload).hex()).hex())

        major_headers = {
            "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded", "Expect": "100-continue",
            "Host": login_url.replace("https://", ""), "ReleaseVersion": "OB53",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1", "X-Unity-Version": "2018.4."
        }

        try:
            await client.post(f"{login_url}/MajorRegister", headers=major_headers, content=encrypted_payload)
        except: pass

        # 4. Major Login (Auto-Activation)
        login_payload_raw = b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02' + lang.encode("ascii") + b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        login_payload_raw = login_payload_raw.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        login_payload_raw = login_payload_raw.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
        
        final_login_payload = bytes.fromhex(E_AEs(login_payload_raw.hex()).hex())
        
        jwt_token = "NOT_FOUND_OR_FAILED"
        try:
            r4 = await client.post(f"{login_url}/MajorLogin", headers=major_headers, content=final_login_payload)
            res_text = r4.text
            idx = res_text.find("eyJhbGciOiJIUzI1NiIs")
            if idx != -1:
                raw_token = res_text[idx:]
                first_dot = raw_token.find(".")
                if first_dot != -1:
                    second_dot = raw_token.find(".", first_dot + 1)
                    if second_dot != -1:
                        jwt_token = raw_token[:second_dot + 44]
        except Exception as e:
            jwt_token = f"ERROR: {str(e)}"

    # ==========================================
    # EXACT ORDERED JSON RESPONSE
    # ==========================================
    # Dictionary insertion order is preserved in Python. FastAPI's JSONResponse respects it.
    return {
        "developer": "BITTU__DEV",
        "player_name": name,
        "player_uid": str(uid),
        "password": password,
        "reg": region_key,
        "success": "true",
        "tokens": {
            "access_token": access_token,
            "activated_jwt": jwt_token,
            "open_id": open_id
        }
    }

# ==========================================
# FASTAPI ROUTES
# ==========================================
@app.get("/api/gen")
async def api_generate_account(reg: str = "IND", name_pref: str = "BITTU"):
    result = await execute_forge(reg, name_pref)
    
    if "error" in result:
        # Return error preserving structure or fallback
        return JSONResponse(content=result, status_code=500)
        
    return JSONResponse(content=result, status_code=200)

@app.get("/")
async def root():
    return JSONResponse(content={
        "status": "BITTU__DEV Forge API Live (FastAPI Async Engine) 💀",
        "docs": "/docs",
        "endpoint": "/api/gen?reg=IND&name_pref=BITTU"
    })
