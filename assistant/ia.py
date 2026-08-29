"""
Cerveau IA de Hmied.

Utilise en priorite OpenRouter (une seule cle API -> tous les modeles,
dont des modeles GRATUITS) sinon Ollama local.
"""

import os

import requests

import config

_OLLAMA = "http://127.0.0.1:11434"
_MODELE_OLLAMA = "qwen2.5:7b"

_EN_LIGNE = False
_SOURCE = None  # None | "openrouter" | "ollama"

_SYSTEM = (
    "Tu es Hmied حميد, assistant personnel d'Ahmed qui vit en Tunisie. "
    "TU DOIS TOUJOURS REPONDRE EN DERJA TUNISIEN (arabe tunisien parlé), JAMAIS en arabe littéraire (fusha) ni en français pur. "
    "Exemples de ton: «شنوة» (quoi), «كيفاش» (comment), «برشا» (beaucoup), «ياسر» (très), «نهار» (jour), «باهي» (bien), «يا خوي» (mon frère). "
    "Reste court (2-3 phrases max), sympathique et naturel, avec un peu de tunisien amical. "
    "Tu aides pour : prix crypto/Binance, rendez-vous, rappels, messages WhatsApp, emails, planning, meteo, etc. "
    "Pour ces actions, guide vers une demande precise comme «prends rendez-vous avec mon frere demain a 10h»."
)


def _cle_openrouter() -> str:
    return (config.OPENROUTER_API_KEY or "").strip() or os.environ.get("OPENROUTER_API_KEY", "").strip()


def configurer() -> bool:
    """Detecte la source de cerveau disponible (OpenRouter puis Ollama)."""
    global _EN_LIGNE, _SOURCE
    if _cle_openrouter():
        try:
            r = requests.post(
                config.OPENROUTER_URL,
                headers={
                    "Authorization": "Bearer " + _cle_openrouter(),
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "AssistantAI",
                },
                json={
                    "model": config.OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5,
                },
                timeout=10,
            )
            r.raise_for_status()
            _SOURCE = "openrouter"
            _EN_LIGNE = True
            return True
        except Exception:
            pass
    try:
        r = requests.get(_OLLAMA + "/api/tags", timeout=3)
        noms = [m.get("name", "") for m in r.json().get("models", [])]
        if r.status_code == 200 and any(m.startswith(_MODELE_OLLAMA) for m in noms):
            _SOURCE = "ollama"
            _EN_LIGNE = True
            return True
    except Exception:
        pass
    _SOURCE = None
    _EN_LIGNE = False
    return False


def est_actif() -> bool:
    return _EN_LIGNE


def source() -> str:
    return _SOURCE or "aucune"


def generer(message: str) -> str:
    """Genere une reponse de Hmied pour une question libre."""
    if not _EN_LIGNE:
        return None
    if _SOURCE == "openrouter":
        return _generer_openrouter(message)
    return _generer_ollama(message)


def _generer_openrouter(message: str) -> str:
    try:
        r = requests.post(
            config.OPENROUTER_URL,
            headers={
                "Authorization": "Bearer " + _cle_openrouter(),
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "AssistantAI",
            },
            json={
                "model": config.OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": message},
                ],
                "max_tokens": 300,
            },
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return (data["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        print("OpenRouter erreur:", e)
        return None


def _generer_ollama(message: str) -> str:
    try:
        prompt = _SYSTEM + "\n\nUtilisateur: " + message + "\nHmied:"
        r = requests.post(
            _OLLAMA + "/api/generate",
            json={
                "model": _MODELE_OLLAMA,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_ctx": 2048, "num_predict": 300},
            },
            timeout=240,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        print("Ollama erreur:", e)
        return None