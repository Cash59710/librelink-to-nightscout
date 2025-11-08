import os, requests, json

base = "https://api-eu.libreview.io"
email = os.environ.get("LLA_EMAIL")
pwd = os.environ.get("LLA_PASSWORD")

print("📡 Test de connexion à", base)

try:
    # Test GET racine
    r = requests.get(base, timeout=10)
    print("✅ Base accessible :", r.status_code)
except Exception as e:
    print("❌ Erreur accès base :", e)

if not email or not pwd:
    print("⚠️ Variables LLA_EMAIL / LLA_PASSWORD manquantes.")
else:
    login_url = f"{base}/llu/auth/login"
    print("🔐 Tentative de connexion sur :", login_url)

    try:
        r = requests.post(
            login_url,
            json={"email": email, "password": pwd},
            timeout=15
        )
        print("📥 Status:", r.status_code)
        if "application/json" in r.headers.get("Content-Type", ""):
            data = r.json()
            print("🧩 JSON reçu :")
            print(json.dumps(data, indent=2)[:1000])
        else:
            print("Réponse brute :")
            print(r.text[:500])
    except Exception as e:
        print("❌ Erreur POST login:", e)
