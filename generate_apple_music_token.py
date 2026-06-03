import time
import jwt

TEAM_ID = "LZH7U3MUHK"
KEY_ID = "97FY2RHSNQ"
PRIVATE_KEY_PATH = "./AuthKey_97FY2RHSNQ.p8"

with open(PRIVATE_KEY_PATH, "r") as f:
    private_key = f.read()

headers = {
    "alg": "ES256",
    "kid": KEY_ID,
}

payload = {
    "iss": TEAM_ID,
    "iat": int(time.time()),
    "exp": int(time.time()) + 60 * 60 * 24 * 30,
}

token = jwt.encode(
    payload,
    private_key,
    algorithm="ES256",
    headers=headers,
)

print(token)