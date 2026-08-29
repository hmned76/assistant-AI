"""
Configuration d'AssistantAI.

Remplis ces valeurs quand tu as tes cles API. Le serveur fonctionne
quand meme sans elles : les actions externes (WhatsApp, email, calendrier)
sont alors "estimees" et journalisees dans la base au lieu d'etre envoyees.
"""

# --- Mode de marche ---
# "simu" : aucune cle requise, les actions sont simulees (mode demo)
# "reel" : active les vraies integrations (il faut alors remplir les cles)
MODE = "simu"

# --- Serveur ---
HOST = "0.0.0.0"          # accessible depuis le telephone sur le reseau local
PORT = 5000
NOM_ASSISTANT = "Hmied حميد"
PREFIXE_UTILISATEUR = "Toi"

# --- WhatsApp (Twilio) ---
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_FROM_WHATSAPP = ""        # ex: "whatsapp:+14155238886"
TWILIO_TO_WHATSAPP = ""          # ex: "whatsapp:+216XXXXXXXX"

EMAIL_ACTIF = False

# --- Email (SMTP / SendGrid) ---
SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""
EMAIL_EXPEDITEUR = ""
EMAIL_DESTINATAIRE = ""

# --- Calendrier (Google) ---
GOOGLE_CLIENT_SECRET_FILE = ""