from flask import Flask
import threading
import time
import requests

# --- CONFIGURATION ---
LLA_EMAIL = "ton_email_librelink"
LLA_PASSWORD = "ton_mdp_librelink"
NIGHTSCOUT_URL = "https://ton-nightscout-url.com"
NIGHTSCOUT_API_SECRET = "ton_api_secret"

# --- FONCTIONS DU WORKER (copié de worker.py) ---
def get_librelink_data():
    """
    Copie ici le code principal de ton worker.py
    Exemple : connexion à LibreLinkUp, récupération des glycémies
    """
    try:
        session = requests.Session()
        login_url = "https://eu.libreview.io/llu/auth/login"
        # Adaptation selon ton worker.py
        resp = session.post(login_url, data={"email": LLA_EMAIL, "password": LLA_PASSWORD})
        resp.raise_for_status()
        
        # Ici tu récupères tes glycémies depuis la réponse
        # Exemple fictif
        glycemia = 100  # remplacer par la valeur réelle
        timestamp = int(time.time() * 1000)
        
        # Envoyer à Nightscout
        data = {"sgv": glycemia, "date": timestamp}
        r = requests.post(f"{NIGHTSCOUT_URL}/api/v1/entries.json?api_secret={NIGHTSCOUT_API_SECRET}", json=data)
        r.raise_for_status()
        
        print("Glycémie envoyée ✔️")
    except Exception as e:
        print("Erreur récupération LibreLinkUp :", e)

def worker_loop():
    while True:
        get_librelink_data()
        time.sleep(60)  # récupérer toutes les 60s (ajuste si besoin)

# --- FLASK APP ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Web Service + Worker actif 🚀"

# --- LANCER LE WORKER EN THREAD ---
threading.Thread(target=worker_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
