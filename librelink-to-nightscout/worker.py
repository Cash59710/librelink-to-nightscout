import os
import time
import requests

LLA_EMAIL = os.environ.get("LLA_EMAIL")
LLA_PASSWORD = os.environ.get("LLA_PASSWORD")
LLA_REGION = os.environ.get("LLA_REGION", "EU")
NIGHTSCOUT_URL = os.environ.get("NIGHTSCOUT_URL")
NIGHTSCOUT_API_SECRET = os.environ.get("NIGHTSCOUT_API_SECRET")

LOGIN_URL = f"https://{LLA_REGION.lower()}.libreview.io/llu/auth/login"
DATA_URL = f"https://{LLA_REGION.lower()}.libreview.io/llu/connections"

def get_latest_glucose():
    try:
        login_resp = requests.post(
            LOGIN_URL,
            json={"email": LLA_EMAIL, "password": LLA_PASSWORD},
            timeout=10
        )
        login_data = login_resp.json()
        token = login_data["data"]["authTicket"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        data_resp = requests.get(DATA_URL, headers=headers, timeout=10)
        data = data_resp.json()
        return data["data"][0]["glucoseMeasurement"]
    except Exception as e:
        print(f"Erreur récupération LibreLinkUp : {e}")
        return None

def send_to_nightscout(entry):
    try:
        payload = [{
            "type": "sgv",
            "date": int(time.time() * 1000),
            "sgv": entry["ValueInMgPerDl"],
            "direction": entry["TrendArrow"],
            "device": "LibreLinkUp"
        }]
        headers = {"API-SECRET": NIGHTSCOUT_API_SECRET, "Content-Type": "application/json"}
        r = requests.post(f"{NIGHTSCOUT_URL}/api/v1/entries", json=payload, headers=headers)
        if r.status_code in [200, 201]:
            print(f"✓ Valeur {entry['ValueInMgPerDl']} mg/dL envoyée à Nightscout")
        else:
            print(f"Erreur Nightscout ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"Erreur envoi Nightscout : {e}")

while True:
    glucose = get_latest_glucose()
    if glucose:
        send_to_nightscout(glucose)
    time.sleep(60)
