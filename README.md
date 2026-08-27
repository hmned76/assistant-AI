# Assistant IA – Structure de dépôt `hmned76`

Ce dépôt contient les fichiers nécessaires à la création d'un assistant IA capable de comprendre le Tunisien (mélange français‑arabe) et d'exécuter des actions (prise de rendez‑vous, envoi WhatsApp, etc.).

## Arborescence

```
hmned76/
├─ prompts/                     # Prompts système et modèles de tâches
│   ├─ tunisian_system.md       # Règles d'écoute et d'interprétation en Tunisian
│   └─ general_tasks.md         # Modèles (RDV, WhatsApp, rappel, planning)
├─ transform/                   # Petits scripts de parsing / transformation
│   └─ whatsapp_prompt.py       # Extraction de nom, message, date depuis une phrase Tunisian
├─ db/                          # Schémas et migrations de la base de données
│   └─ migrations/              # Fichiers de migration SQL (ex: 20260827_initial.sql)
├─ .github/                     # Workflows CI/CD (optionnel)
└─ README.md                    # Ce fichier
```

## 1. Prompts

- **`prompts/tunisian_system.md`** : À préfixer à chaque demande utilisateur. Il dit à l'IA d'écouter le Tunisian tel quel, de reconnaître l'intention sans traduction mot‑à‑mot, et de répondre en français (avec le droit d'utiliser des mots tunisiens).
- **`prompts/general_tasks.md`** : Contient des modèles décrivant les actions courantes (prendre RDV, envoyer WhatsApp, programmer un rappel, afficher le planning). Ces modèles peuvent être utilisés par le backend pour construire les requêtes vers la base de données ou les APIs tierces.

## 2. Script de transformation

- **`transform/whatsapp_prompt.py`** : Fonction `extract_intent(text)` qui, à partir d'une phrase en Tunisian, retourne un dictionnaire simplifié :
  - `contact_name` : dernier mot considéré comme le nom de la personne.
  - `action` : "whatsapp" si des mots déclencheurs sont détectés, sinon "none".
  - `message` : texte après le mot "à" (ex. "demain à 10h").
  - `date_heur` : motif de date/heure optionnel.

  *Note* : C'est un parser très naïf ; en production, on utiliserait un modèle NLP ou des expressions régulières plus robustes.

## 3. Base de données

- **`db/migrations/`** : Contiendra les fichiers de migration SQL (ou dossiers Prisma/TypeORM) pour créer les tables suivantes (voir schema.prisma ci‑dessous).
- **Tables suggérées** :
  - `users` – identifiant, mot de passe (hash), préférences linguistiques.
  - `contacts` – `id`, `user_id`, `name`, `phone`, `relation` (frère, sœur, médecin, etc.), `is_private`.
  - `events` (rendez‑vous) – `id`, `user_id`, `title`, `start_datetime`, `end_datetime`, `is_private`, `contact_id` (lien vers `contacts`).
  - `notifications` – `id`, `user_id`, `event_id`, `scheduled_at`, `sent`.

Un exemple de **schema Prisma** peut être généré ou ajouté dans `db/schema.prisma` si vous utilisez Prisma.

## 4. Utilisation typique

1. Utilisateur envoie un message en Tunisian (ex: `"prends rendez‑vous avec mon frère Mohamed demain à 10h"`).
2. Le backend reçoit le message et l'envoie au modèle LLM **après avoir préfixé** le prompt `tunisian_system.md`.
3. Le LLM produit une réponse structurée (ou le backend appelle `extract_intent` via le script Python).
4. Le backend recherche le contact dans la table `contacts` (via le nom extrait).
5. Selon l'action :
   - **RDV** : créer un événement dans la table `events`, puis envoyer un WhatsApp via Twilio.
   - **Message** : envoyer directement un WhatsApp avec le texte extrait.
   - **Rappel** : planifier une notification (Cron, FCM, etc.).
6. L'IA répond à l'utilisateur en confirmant l'action (en français, avec le droit d'insérer des mots tunisiens si l'utilisateur les a employés).

## 5. Développement local

```bash
# Cloner ou copier le dossier hmned76 dans votre projet
git clone <votre-repo> hmned76
cd hmned76

# Installer les dépendances (exemple Python)
pip install pytwilio  # ou les libs que vous utilisez

# Lancer le script de test
python transform/whatsapp_prompt.py
```

## 6. prochain steps (au choix)

- Ajouter un fichier `db/schema.prisma` ou les migrations SQL manquantes.
- Intégrer le script `extract_intent` dans votre backend (Node/Express, FastAPI, etc.).
- Configurer les clés API Twilio / SendGrid / Google Calendar.
- Tester le flow complet avec quelques phrases Tunisian réelles.

---

*Ce dépôt est un point de départ. Vous pouvez le personnaliser selon vos besoins (base de données, choix de LLM, déploiement).*