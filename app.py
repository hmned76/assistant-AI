from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

CONVERSATIONS_FILE = os.path.join(app.root_path, "db", "conversations.json")

# Charger les conversations
def load_conversations():
    if not os.path.exists(CONVERSATIONS_FILE):
        return []
    with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Sauvegarder les conversations
def save_conversations(conversations):
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

# Route : afficher la page d'accueil
@app.route("/")
def index():
    convos = load_conversations()
    return render_template("index.html", conversations=convos)

# API : ajouter une nouvelle conversation
@app.route("/api/conversation", methods=["POST"])
def add_conversation():
    data = request.get_json()
    user = data.get("user", "")
    assistant = data.get("assistant", "")
    entry = {
        "id": int(datetime.utcnow().timestamp()),
        "user": user,
        "assistant": assistant,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    conversations = load_conversations()
    conversations.append(entry)
    save_conversations(conversations)
    return jsonify({"status": "ok", "id": entry["id"]}), 201

# API : récupérer toutes les conversations (en JSON)
@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    return jsonify(load_conversations())

if __name__ == "__main__":
    app.run(debug=True, port=5000)