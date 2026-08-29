"""
AssistantAI - Serveur web local.

Lancez avec :  python app.py
Ouvrez ensuite http://127.0.0.1:5000 (ou l'IP de votre PC depuis le telephone).
"""

import os
import sys

from flask import Flask, render_template, request, jsonify

import config
from assistant import engine, storage
from assistant.integrations import envoyer_whatsapp, envoyer_email
from assistant import trading


def _base_path() -> str:
    """Retourne le bon dossier racine (normal ou exe PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__, template_folder=os.path.join(_base_path(), "templates"))

# On pointe la base de donnees dans le dossier d'execution
storage.DB_PATH = os.path.join(_base_path(), "db", "assistant.db")
storage.initialiser()


def _traiter_demande(message: str):
    resultat = engine.executer(message, config.NOM_ASSISTANT, config.MODE)
    intention = resultat["intention"]
    reponse = resultat["reponse"]
    infos = resultat["infos"]

    # Actions externes selon l'intention (WhatsApp / email / rdv / trading)
    actions = []
    if intention == "whatsapp":
        contact = infos.get("contact") or "le contact"
        corps = infos.get("texte") or reponse
        res = envoyer_whatsapp(config.TWILIO_TO_WHATSAPP or contact, corps)
        actions.append({"type": "whatsapp", "resultat": res})
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


if __name__ == "__main__":
    print("AssistantAI demarre sur http://127.0.0.1:%d" % config.PORT)
    print("Depuis ton telephone (meme Wi-Fi) : http://<IP-DU-PC>:%d" % config.PORT)
    app.run(host=config.HOST, port=config.PORT, debug=False)