"""
Persistence des donnees (SQLite) pour AssistantAI.

Tables : conversations, contacts, events (rendez-vous), rappels.
Converties depuis le schema Postgres vers SQLite pour tourner en local.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db", "assistant.db")


def _connexion():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialiser():
    conn = _connexion()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            contenu TEXT NOT NULL,
            intention TEXT DEFAULT '',
            cree_le TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT,
            relation TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            debut TEXT NOT NULL,
            fin TEXT,
            prive INTEGER DEFAULT 0,
            contact_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES contacts(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rappels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenu TEXT,
            quand TEXT,
            fait INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def ajouter_conversation(role: str, contenu: str, intention: str = "") -> int:
    conn = _connexion()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (role, contenu, intention) VALUES (?, ?, ?)",
        (role, contenu, intention),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def lister_conversations(limite: int = 200) -> list:
    conn = _connexion()
    rows = conn.execute(
        "SELECT * FROM conversations ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def ajouter_contact(nom: str, telephone: str = "", relation: str = "") -> int:
    conn = _connexion()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO contacts (nom, telephone, relation) VALUES (?, ?, ?)",
        (nom, telephone, relation),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def lister_contacts() -> list:
    conn = _connexion()
    rows = conn.execute("SELECT * FROM contacts ORDER BY nom").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_evenement(titre: str, debut: str, fin: str = "", prive: int = 0) -> int:
    conn = _connexion()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (titre, debut, fin, prive) VALUES (?, ?, ?, ?)",
        (titre, debut, fin, prive),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def lister_evenements() -> list:
    conn = _connexion()
    rows = conn.execute("SELECT * FROM events ORDER BY debut").fetchall()
    conn.close()
    return [dict(r) for r in rows]