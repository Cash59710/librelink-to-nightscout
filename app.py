from flask import Flask
import threading
import time
import requests
import os  # <- pour lire les variables d'environnement

# --- CONFIGURATION via ENV ---
LLA_EMAIL = os.environ.get("LLA_EMAIL")
LLA_PASSWORD = os.environ.get("LLA_PASSWORD")
NIGHTSCOUT_URL = os.environ.get("NIGHTSCOUT_URL")
NIGHTSCOUT_API_SECRET = os.environ.get("NIGHTSCOUT_API_SECRET")

# --- FONCTIONS DU WORKER ---
def get_librelink_data():
    try:
        session = requests.Session()
        login_url = "https://eu.libreview.io/llu/auth/login"
        resp = session.post(login_url, data={"email": LLA_EMAIL, "password": LLA_PASSWORD})
        resp.raise_for_status()
        
        # Exemple fictif de glycémie
        glycemia = 100
        timestamp = int(time.time() * 1000)
        
        data = {"sgv": glycemia, "date": timestamp}
        r = requests.post(f"{NIGHTSCOUT_URL}/api/v1/entries.json?api_secret={NIGHTSCOUT_API_SECRET}", json=data)
        r.raise_for_status()
        print("Glycémie envoyée ✔️")
    except Exception as e:
        print("Erreur récupération LibreLinkUp :", e)

def worker_loop():
    while True:
        get_librelink_data()
        time.sleep(60)  # récupérer toutes les 60s

# --- FLASK APP ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Web Service + Worker actif 🚀"

# --- LANCER LE WORKER EN THREAD ---
threading.Thread(target=worker_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
