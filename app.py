"""
AssistantAI - Serveur web local.

Lancez avec :  python app.py
Ouvrez ensuite http://127.0.0.1:5000 (ou l'IP de votre PC depuis le telephone).
"""

import os
import sys

os.environ.setdefault("HF_HOME", r"D:\assistantAI\.cache\huggingface")
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", r"D:\assistantAI\.cache\huggingface")
os.environ.setdefault("OLLAMA_MODELS", r"D:\assistantAI\.ollama")

from flask import Flask, render_template, request, jsonify, Response

import config
from assistant import engine, storage, ia
from assistant.integrations import envoyer_email
from assistant.whatsapp_connector import envoyer_whatsapp as wa_envoyer, demarrer_whatsapp_monitor, arreter_whatsapp_monitor, traiter_message_whatsapp, verifier_signature_webhook
from assistant import trading


def _base_path() -> str:
    """Retourne le bon dossier racine (normal ou exe PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__, template_folder=os.path.join(_base_path(), "templates"))
app.config.update(TEMPLATES_AUTO_RELOAD=True, SEND_FILE_MAX_AGE_DEFAULT=0)


@app.after_request
def _no_cache(resp):
    """Forcer le rechargement de l'interface (WebView du téléphone)."""
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

# On pointe la base de donnees dans le dossier d'execution
storage.DB_PATH = os.path.join(_base_path(), "db", "assistant.db")
storage.initialiser()
ia.configurer()
print("Cerveau IA:", ia.source())

# Demarrer le monitor WhatsApp en arriere-plan
demarrer_whatsapp_monitor()
print("WhatsApp monitor lance")


def _traiter_demande(message: str):
    resultat = engine.executer(message, config.NOM_ASSISTANT, config.MODE)
    intention = resultat["intention"]
    reponse = resultat["reponse"]
    infos = resultat["infos"]

    # Cerveau local (Ollama) pour les questions libres
    if intention == "question" and ia.est_actif():
        try:
            llm = ia.generer(message)
            if llm:
                reponse = llm
        except Exception as e:
            print("Ollama erreur:", e)

    # Actions externes selon l'intention (WhatsApp / email / rdv / trading)
    actions = []
    if intention == "whatsapp":
        contact = infos.get("contact") or "le contact"
        corps = infos.get("texte") or reponse
        # Resoudre le nom du contact vers un numero de telephone (config.CONTACTS)
        cle_contact = contact.lower().split()[-1]
        numero = config.CONTACTS.get(cle_contact, config.CONTACTS.get(contact.lower(), ""))
        destinataire = numero or contact
        res = wa_envoyer(destinataire, corps)
        actions.append({"type": "whatsapp", "resultat": res})
        if res.get("statut") == "simu":
            reponse = (f"(Simulation) Message WhatsApp prêt pour {contact} : « {corps} ». "
                       "Configure un fournisseur dans config.py (Maytapi/360dialog) pour un vrai envoi.")
        elif res.get("statut") == "erreur":
            reponse = f"⚠️ WhatsApp réel a échoué : {res.get('details', 'erreur inconnue')}"
    elif intention == "email":
        res = envoyer_email("Message d'AssistantAI", infos.get("texte") or reponse)
        actions.append({"type": "email", "resultat": res})
    elif intention == "rdv":
        titre = f"RDV avec {infos.get('contact') or 'contact'}"
        debut = f"{infos.get('jour')}T{infos.get('heure') or '10:00'}:00"
        rid = storage.ajouter_evenement(titre, debut)
        actions.append({"type": "rdv", "resultat": {"id": rid, "debut": debut}})
    elif intention == "trading":
        try:
            res = trading.executer_investissement(message)
            reponse = res["reponse"]
            actions.append({"type": "trading", "resultat": res})
        except Exception as e:
            reponse = f"L'analyse Binance a échoué : {e} (vérifie ta connexion internet)."
    elif intention == "call":
        c = infos.get("contact") or "le contact"
        numero = config.CONTACTS.get(c.lower().split()[-1], config.CONTACTS.get(c.lower(), ""))
        actions.append({"type": "call", "resultat": {"numero": numero, "contact": c}})
        reponse = f"Je vais appeler {c} des maintenant."

    # Persistance des deux cotes de la conversation
    storage.ajouter_conversation("user", message, intention)
    storage.ajouter_conversation("assistant", reponse, intention)

    return {"reponse": reponse, "intention": intention, "actions": actions}


@app.route("/")
def index():
    conversations = storage.lister_conversations()
    return render_template(
        "index.html",
        conversations=conversations,
        nom_assistant=config.NOM_ASSISTANT,
        mode=config.MODE,
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"erreur": "message vide"}), 400
    resultat = _traiter_demande(message)
    return jsonify(resultat)


@app.route("/api/stt", methods=["POST"])
def api_stt():
    """Reconnait la parole (francais ou arabe tunisien) a partir du fichier audio envoye par l'APK."""
    audio = request.get_data(cache=False)
    if not audio or len(audio) < 500:
        return jsonify({"texte": ""}), 400
    try:
        from assistant import stt
        texte = stt.transcrire(audio)
        return jsonify({"texte": texte})
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


@app.route("/api/tts", methods=["POST"])
def api_tts():
    """Synthetise la reponse en MP3 avec une voix Microsoft naturelle (homme fr/ar)."""
    data = request.get_json(silent=True) or {}
    texte = (data.get("texte") or "").strip()
    if not texte:
        return jsonify({"erreur": "texte vide"}), 400
    import re
    if re.search(r"[\u0600-\u06FF]", texte):
        voix = "ar-SA-HamedNeural"
    else:
        voix = "fr-FR-HenriNeural"
    try:
        import asyncio
        import edge_tts

        async def _synthetiser():
            buffer = bytearray()
            async for c in edge_tts.Communicate(texte, voix).stream():
                if c["type"] == "audio":
                    buffer.extend(c["data"])
            return bytes(buffer)

        chunks = asyncio.run(_synthetiser())
        return Response(chunks, mimetype="audio/mpeg",
                        headers={"Cache-Control": "no-store"})
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


@app.route("/api/conversations")
def api_conversations():
    return jsonify(storage.lister_conversations())


@app.route("/api/events")
def api_events():
    return jsonify(storage.lister_evenements())


@app.route("/api/contacts")
def api_contacts():
    return jsonify(storage.lister_contacts())


@app.route("/api/prix")
def api_prix():
    symbole = request.args.get("symbol", config.BINANCE_COIN_DE_BASE)
    try:
        return jsonify({"symbole": symbole, "prix": trading.obtenir_prix(symbole)})
    except Exception as e:
        return jsonify({"erreur": str(e)}), 502


@app.route("/api/analyse")
def api_analyse():
    symbole = request.args.get("symbol", config.BINANCE_COIN_DE_BASE)
    try:
        return jsonify(trading.analyser_marche(symbole))
    except Exception as e:
        return jsonify({"erreur": str(e)}), 502


@app.route("/api/portfolio")
def api_portfolio():
    return jsonify(trading.valeur_portefeuille())


@app.route("/api/trade", methods=["POST"])
def api_trade():
    data = request.get_json(silent=True) or {}
    symbole = data.get("symbol") or config.BINANCE_COIN_DE_BASE
    cote = (data.get("side") or "ACHAT").upper()
    montant = float(data.get("amount") or (config.BINANCE_CAPITAL_INITIAL / 5))

    if config.BINANCE_PAPER:
        return jsonify(trading.trader_paper(symbole, cote, montant))
    return jsonify(trading.ordre_reel(symbole, cote, montant))


@app.route("/api/whatsapp/webhook", methods=["GET"])
def wa_webhook_verify():
    """Verification du webhook (GET pour l'inscription chez le fournisseur)."""
    mode = request.args.get("mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    secret = config.WA_WEBHOOK_SECRET
    if mode == "subscribe" and token == secret:
        return challenge, 200
    return "Forbidden", 403


@app.route("/api/whatsapp/webhook", methods=["POST"])
def wa_webhook_incoming():
    """Reception d'un message WhatsApp entrant via webhook."""
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"erreur": "donnees vides"}), 400

    # Verification de la signature si configure
    signature = request.headers.get("X-Signature", "")
    if signature and config.WA_WEBHOOK_SECRET:
        payload = request.get_data()
        if not verifier_signature_webhook(payload, signature):
            return jsonify({"erreur": "signature invalide"}), 403

    try:
        resultat = traiter_message_whatsapp(data)
        return jsonify(resultat)
    except Exception as e:
        print("WA webhook erreur:", e)
        return jsonify({"erreur": str(e)}), 500


@app.route("/api/whatsapp/monitor/start", methods=["POST"])
def wa_monitor_start():
    """Demarre le polling des messages WhatsApp en arriere-plan."""
    demarrer_whatsapp_monitor()
    return jsonify({"statut": "ok", "message": "WhatsApp monitor demarre"})


@app.route("/api/whatsapp/monitor/stop", methods=["POST"])
def wa_monitor_stop():
    """Arrete le polling des messages WhatsApp."""
    arreter_whatsapp_monitor()
    return jsonify({"statut": "ok", "message": "WhatsApp monitor arrette"})


@app.route("/api/whatsapp/monitor/statut", methods=["GET"])
def wa_monitor_statut():
    """Statut du monitor WhatsApp."""
    from assistant.whatsapp_connector import _wa_monitor
    return jsonify({"actif": _wa_monitor.actif})


@app.route("/api/whatsapp/envoyer", methods=["POST"])
def wa_envoyer_manual():
    """Envoi manuel d'un message WhatsApp."""
    data = request.get_json(silent=True) or {}
    dest = data.get("destinataire", "")
    message = data.get("message", "")
    if not dest or not message:
        return jsonify({"erreur": "destinataire et message requis"}), 400
    res = wa_envoyer(dest, message)
    return jsonify(res)


if __name__ == "__main__":
    print("AssistantAI demarre sur http://127.0.0.1:%d" % config.PORT)
    print("Depuis ton telephone (meme Wi-Fi) : http://<IP-DU-PC>:%d" % config.PORT)
    app.run(host=config.HOST, port=config.PORT, debug=False)