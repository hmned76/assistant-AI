# AssistantAI 🇹🇳🤖

**Assistant personnel intelligent** qui comprend le **Tunisien** (mélange français‑arabe), prend des
rendez‑vous, envoie des messages WhatsApp, programme des rappels, et garde l'historique de
toutes les conversations.

## Fonctionnalités (état actuel)

- ✅ **Compréhension du Tunisien** : pars le message tel quel, détecte l'intention
  (salutation, RDV, WhatsApp, rappel, planning, email, remerciements, au revoir).
- ✅ **Serveur web local** (Flask) sur `http://127.0.0.1:5000`, accessible depuis le
  **téléphone** sur le même Wi‑Fi (`http://<IP‑du‑PC>:5000`).
- ✅ **Interface de chat mobile‑first** (bulles, entrée Tunisien, badges d'intention).
- ✅ **Persistance SQLite** : conversations, contacts, rendez‑vous, rappels.
- ✅ **Mode `simu` par défaut** : aucune clé API requise ; les WhatsApp/emails sont
  journalisés au lieu d'être envoyés.
- 🔜 **Mode `reel`** : remplis `config.py` (Twilio, SMTP, Google Calendar) pour de vrais envois.

## Démarrage rapide

```powershell
# 1. Installer les dépendances
python -m pip install -r requirements.txt

# 2. Lancer le serveur
python app.py
# ou double‑clic sur start.bat

# 3. Ouvrir le navigateur
http://127.0.0.1:5000
```

Depuis ton téléphone (même Wi‑Fi) : `http://192.168.100.29:5000` (IP du PC, affichée au démarrage).

## Compiler en .exe

```powershell
# double‑clic sur build_exe.bat  (ou lancer ci‑dessous)
python -m PyInstaller --onefile --windowed --name AssistantAI --add-data "templates;templates" app.py
```

Résultat : `dist\AssistantAI.exe`

## Structure

```
assistant-AI/
├─ app.py                    # Serveur Flask (chat + API + page)
├─ config.py                 # Clés API (Twilio, SMTP, Google) — MODE simu/reel
├─ requirements.txt          # Dépendances Python
├─ start.bat                 # Lance le serveur (Windows)
├─ build_exe.bat             # Compile l'executable (Windows)
├─ templates/
│   └─ index.html            # Interface de chat (mobile-first)
├─ assistant/
│   ├─ engine.py             # Moteur IA : analyse Tunisien + reponses
│   ├─ storage.py            # Persistance SQLite
│   ├─ integrations.py       # WhatsApp (Twilio) + Email (SMTP), simu/reel
│   └─ __init__.py
├─ prompts/
│   ├─ tunisian_system.md    # Regles d'ecoute du Tunisian (pour un futur LLM)
│   └─ general_tasks.md      # Modeles de tâches
├─ transform/
│   └─ whatsapp_prompt.py    # Extraction d'intention (legacy / reference)
├─ db/
│   ├─ assistant.db          # Base locale (creee au premier lancement)
│   └─ migrations/           # Schema SQL de reference (Postgres)
└─ README.md
```

## API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page de chat |
| `/api/chat` | POST | `{"message": "..."}` → réponse + intention + actions |
| `/api/conversations` | GET | Historique des conversations |
| `/api/events` | GET | Rendez‑vous enregistrés |
| `/api/contacts` | GET | Contacts |

## Exemples Tunisien

| Tu dis | AssistantAI fait |
|--------|------------------|
| « prends rendez‑vous avec mon frère Mohamed demain à 10h » | Note le RDV (event) + invite (si mode réel) |
| « whatsapp mon frère dis‑lui qu'on se voit demain » | Envoie le message WhatsApp (si mode réel) |
| « rappelle‑moi le médecin à 16h » | Programme le rappel |
| « montre mon planning » | Affiche le résumé du jour/mois |

## Étapes suivantes possibles

1. Remplir `config.py` avec tes clés **Twilio** (WhatsApp), **SMTP/SendGrid** (email),
   **Google Calendar** → passer `MODE = "reel"`.
2. Brancher un vrai **LLM** (OpenAI / Claude) dans `assistant/engine.py` pour un dialogue libre.
3. Générer l'**APK Android** (le dossier `android/` est prévu pour les autorisations).
4. Ajouter la **vérification par PIN / chiffrement** pour la vue privée du planning.