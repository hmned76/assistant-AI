"""
Configuration d'AssistantAI.

Remplis tes cles API pour passer du mode simu au mode reel.
Le serveur reste fonctionnel meme sans elles (mode "simu" / "paper-trading").
"""

# --- Mode de marche ---
# "simu" : aucune cle requise, les actions externes sont simulees
# "reel" : les integrations actives sont utilisees (cle presente = active)
#          Si une cle manque, l'action est signalee comme "cle manquante" (pas d'envoi reel).
MODE = "reel"

# --- Serveur ---
HOST = "0.0.0.0"          # accessible depuis l'exterieur (5G) via le tunnel
PORT = 5000
NOM_ASSISTANT = "Hmied حميد"
PREFIXE_UTILISATEUR = "Toi"

# --- Cerveau IA (OpenRouter / Ollama) ---
# OpenRouter : UNE seule cle API pour tous les modeles (Claude, GPT, Gemini, Llama,
# DeepSeek...). Modeles GRATUITS disponibles (suffixe ":free", ex ci-dessous).
# Inscription : https://openrouter.ai  ->  cle "sk-or-..."
# Colle ta cle ici ; laisse vide pour utiliser Ollama local.
OPENROUTER_API_KEY = ""
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- WhatsApp (choisis UN fournisseur cloud, Twilio est bloque en Tunisie) ---
# Alternatives a Twilio (tous fonctionnent depuis la Tunisie) :
#   1. Maytapi     : https://maytapi.com      - gratuit 1000 msg/jour, simple
#   2. 360dialog   : https://www.360dialog.io  - gratuit 1000 msg/mois, pro
#   3. Green-api   : https://green-api.com     - gratuit 5000 msg/jour
#   4. Chat-API    : https://chat-api.com      - payant mais fiable
#   5. Twilio      : bloque "Trials unavailable in Tunisia"
#
# Inscris-toi sur un de ces services, cree un compte WhatsApp Business,
# et colle les cles ici. Change WA_API_PROVIDER en "maytapi" ou "360dialog".
# Ton numero WhatsApp personnel fonctionne (pas besoin de numero pro).

WA_API_PROVIDER = "simu"       # "twilio" | "maytapi" | "360dialog" | "simu"
WA_WEBHOOK_SECRET = "whsec_TonSecretIci"    # secret HMAC pour verifier les webhooks
WA_RECEIVE_PHONE = ""            # ton numero WhatsApp (ex: "+216XXXXXXXX")
WA_SEND_PHONE = ""               # idem (le meme numero envoie)

# --- Maytapi (recommande pour la Tunisie - gratuit 1000 msg/jour) ---
# Inscription : https://maytapi.com
# Apres inscription, cree une instance et recupere :
#   - API Key (dans le dashboard Maytapi)
#   - Instance ID (dans l'URL de ton instance)
WA_MAYTAPI_API_KEY = ""
WA_MAYTAPI_INSTANCE_ID = ""

# --- 360dialog (alternative pro - gratuit 1000 msg/mois) ---
# Inscription : https://www.360dialog.io
WA_360DIALOG_API_KEY = ""
WA_360DIALOG_INSTANCE_ID = ""

# --- Green-api (gratuit 5000 msg/jour) ---
# Inscription : https://green-api.com
# Apres inscription, recupere l'ID d'instance et le token API dans le dashboard.
GREEN_API_INSTANCE_ID = ""
GREEN_API_API_KEY = ""

# --- Twilio (NE FONCTIONNE PAS en Tunisie - trials bloques) ---
# Si tu as un compte Twilio hors Tunisie, remplit ici :
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_FROM_WHATSAPP = ""        # ex: "whatsapp:+1415523886" (numero sandbox Twilio)
TWILIO_TO_WHATSAPP = ""          # ex: "whatsapp:+216XXXXXXXX" (ton numero)

# --- Email (SMTP / SendGrid) ---
EMAIL_ACTIF = False              # passe a True quand tu as rempli le serveur SMTP
SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""
EMAIL_EXPEDITEUR = ""
EMAIL_DESTINATAIRE = ""

# --- Calendrier (Google) ---
GOOGLE_CLIENT_SECRET_FILE = ""

# --- Binance (investissement / trading) ---
# PAPER = True : trading SIMULE avec argent fictif (recommandé pour tester)
# PAPER = False : ordres REELS (risque de perte d'argent !)
# Ne met JAMAIS tes vraies clés si tu ne comprends pas les risques.
BINANCE_PAPER = True
BINANCE_API_KEY = ""
BINANCE_SECRET = ""
BINANCE_COIN_DE_BASE = "BTCUSDT"
BINANCE_CAPITAL_INITIAL = float(100)   # en USDT (fictionnel en mode paper)

# --- Contacts (numeros de telephone pour les appels) ---
# Ajoute tes contacts ici avec leur numero.
CONTACTS = {
    "frere": "+216501234567",
    "mohamed": "+216509876543",
}
