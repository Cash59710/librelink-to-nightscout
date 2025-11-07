import os
import time
import requests
from flask import Flask

app = Flask(__name__)

# Variables d'environnement
LLA_EMAIL = os.environ.get("LLA_EMAIL")
LLA_PASSWORD = os.environ.get("LLA_PASSWORD")
LLA_REGION = os.environ.get("LLA_REGION", "EU")
NIGHTSCOUT_URL = os.environ.get("NIGHTSCOUT_URL")
NIGHTSCOUT_API_SECRET = os.environ.get("NIGHTSCOUT_API_SECRET")

LOGIN_URL = f"https://{LLA_REGION.lower()}.libreview.io/llu/auth/login"
DATA_URL = f"https://{LLA_REGION.lower()}.libreview.io/llu/connections"

# Authentification et récupération de données LibreLinkUp
def get_latest_glucose():
    try:
        login_resp = requests.post(
            LOGIN_URL,
            json={"email": LLA_EMAIL, "password": LLA_PASSWORD},
            timeout=10,
        )
        login_data = login_resp.json()
        token = login_data["data"]["authTicket"]["token"]

        headers = {"Authorization": f"Bearer {token}"}
        data_resp = requests.get(DATA_URL, headers=headers, timeout=10)
        data = data_resp.json()

        glucose = data["data"][0]["glucoseMeasurement"]
        return glucose
    except Exception as e:
        print(f"Erreur récupération LibreLinkUp : {e}")
        return None

# Envoi vers Nightscout
def send_to_nightscout(entry):
    try:
        payload = [{
            "type": "sgv",
            "date": int(time.time() * 1000),
            "sgv": entry["ValueInMgPerDl"],
            "direction": entry["TrendArrow"],
            "device": "LibreLinkUp"
        }]

        headers = {
            "API-SECRET": NIGHTSCOUT_API_SECRET,
            "Content-Type": "application/json"
        }

        r = requests.post(f"{NIGHTSCOUT_URL}/api/v1/entries", json=payload, headers=headers)
        if r.status_code == 200 or r.status_code == 201:
            print(f"✓ Valeur {entry['ValueInMgPerDl']} mg/dL envoyée à Nightscout")
        else:
            print(f"Erreur Nightscout ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"Erreur envoi Nightscout : {e}")

@app.route("/")
def home():
    return "LibreLinkUp → Nightscout bridge actif 🚀"

# Boucle de mise à jour (une fois par minute)
def loop():
    while True:
        glucose = get_latest_glucose()
        if glucose:
            send_to_nightscout(glucose)
        time.sleep(60)

if __name__ == "__main__":
    import threading
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
