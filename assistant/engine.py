"""
Moteur IA d'AssistantAI.

Comprend des messages en Tunisien (melange francais-arabe), detecte
l'intention (rdv, message whatsapp, rappel, planning, bonjour, etc.),
construit une reponse et renvoie les actions a executer.
Un vrai LLM (OpenAI/Claude) pourra remplacer la partie regles plus tard.
"""

import re
from datetime import datetime, timedelta

# LEXIQUE : mots tunisiens de base -> comprehension
LEXIQUE_TN = {
    "ya3ni": "c'est-a-dire", "chwiya": "un peu", "saha": "bonjour/sante",
    "bladi": "mon pays", "3ayech": "comment vas-tu", "labes": "ça va",
    "bnina": "bon", "chedda": "la fête/le dejeuner", "balech": "rien/ne t'embete pas",
    "wali": "tu vois", "ima": "maman", "baba": "papa", "khouya": "mon frere",
    "okhti": "ma sœur", "belek": "attention", "tawahit": "tu as peur",
    "squie": "detends-toi", "zahma": "probleme", "fhemka": "je t'ai compris",
    "ma fhemtesh": "tu n'as pas compris", "a3mal": "fais", "ash": "quoi",
    "kifesh": "comment", "yezzi": "assez", "barsha": "beaucoup",
    "wahda": "un", "zoz": "deux", "tlatha": "trois", "rb3a": "quatre",
    "khamsa": "cinq", "souda": "six", "sb3a": "sept", "thmaniya": "huit",
    "ts3ud": "neuf", "3achra": "dix", "hadi": "ceci/c'est", "hina": "ici",
    "houna": "la-bas", "l3eb": "le travail", "dkra": "souviens-toi",
    "trad": "va-t-en", "zid": "ajoute", "khli": "laisse",
    "selem": "paix/salut", "mrhba": "bienvenu", "tekhtar": "choisis",
    "tsawer": "ecris", "qra": "lit", "sme3": "ecoute",
    "nhar": "jour", "leyl": "nuit", "bhar": "matin", "3shiya": "soir",
    "yaoum": "jour", "njom": "nuit", "tempiya": "temperature",
    "csma": "soleil", "ghada": "pluie", "borj": "tour", "sayara": "voiture",
    "darb": "route", "makan": "lieu", "waqt": "temps/heure",
    "daba": "maintenant", "ghadya": "demain", "elahor": "maintenant",
    "fi3l": "faire", "mshy": "marche", "t9mel": "termine",
    "t9adem": "continue", "a9wal": "d'abord", "bel3eb": "au travail",
    "fi rjal": "dans la maison", "m3a": "avec", "b9ida": "loin",
    "qrib": "presse", "7ajr": "pierre", "hbib": "ami", "s7eb": "compagnon",
    "ra7eb": "voisin", "gherma": "cousin", "khta": "cousine",
    "m3amera": "oncle", "3amha": "tante", "bent": "fille", "weld": "garcon",
    "bint": "fille", "yezid": "ajouter", "nazel": "venir", "mshi": "marcher",
    "ktab": "livre", "daira": "cercle/arrondissement", "wilaya": "region",
    "baladiyya": "mairie", "souk": "marche", "masraf": "banque",
    "hospital": "hopital", "mdrasa": "ecole", "jom3a": "mosquee",
    "cafe": "cafe", "reshto": "restaurant", "hayat": "vie", "rahma": "miseration",
    "hiber": "sleepless", "rahlet": "fatigue", "3tisa": "as-tu",
    "3andek": "tu as", "3andia": "j'ai", "m3ak": "avec toi", "m3aya": "avec moi",
    "ghir": "juste", "kolchi": "tout", "wa7ad": "un", "lwan": "couleur",
    "kber": "grand", "sghir": "petit", "zain": "beau", "khayeb": "mauvais",
    "yyen": "il/elle", "nahki": "je", "entek": "tu", "howa": "il", "hiya": "elle",
    "ahna": "nous", "huma": "ils", "nifsek": "toi", "rask": "ton", "mrak": "ta",
    "rak": "tu as", "mra": "femme", "rajel": "homme", "timssa7": "demander",
    "t9eddem": "apprendre", "t9arraf": "connaitre", "t9allam": "enseigner",
    "n7eb": "j'aime", "ma n7ebch": "je n'aime pas", "bghit": "je veux",
    "nbghit": "je veux", "n9adhem": "je peux", "lah": "non", "eh": "oui",
    "na3m": "d'accord", "mish": "ne pas", "mach": "ne pas",
    "w3ad": "un peu", "bar9": "beaucoup", "tfat7": "ouvrir", "tferm": "fermer",
    "tqra": "lire", "tkhudh": "prendre", "tbalagh": "envoyer",
    "t7addeth": "appeler", "twaskil": "utiliser", "t9addam": "rester",
    "tjaw": "aller", "jawab": "reponse", "khemma": "les deux", "zad": "ajoute",
    "yanss": "il connait", "ya3ref": "il sait", "ya3refk": "il sait (te)",
    "ya3refni": "il sait (me)", "ya3refkom": "il sait (vous)",
    "fhem": "comprendre", "fhemek": "comprendre (te)", "fhemni": "comprendre (me)",
    "fhemkom": "comprendre (vous)", "t3arf": "sais-tu", "ta3ref": "est-ce que tu sais",
    "fin": "où", "ach": "quoi", "kifak": "comment tu", "kifakom": "comment vous",
    "ashkan": "comment", "9bal": "avant", "ba3d": "après", "feqd": "pendant",
    "ma9bl": "avant", "ba3dha": "après", "awwel": "premier", "tani": "deuxième",
    "tsael": "troisième", "rb3i": "quatrième", "khamsi": "cinquième",
    "soudi": "sixième", "sb3i": "septième", "thmani": "huitième",
    "ts3udi": "neuvième", "3achri": "dixième", "nishan": "signe",
    "karaha": "tâche", "t3amira": "tâche", "w2ed": "j'ai promis", "mel": "miel",
    "ghorba": "étranger", "djebali": "montagne", "saheli": "côte", "ardh": "terre",
    "bahr": "mer", "neb9": "ciel", "nujom": "étoiles", "qamar": "lune",
    "shams": "soleil", "twas9a": "heure", "dakika": "minute", "thnia": "demi",
    "rab3a": "quart", "tkhmsa": "cinq", "ts9od": "neuf", "3achra": "dix",
    "9achratin": "vingt", "tkhmissin": "cinquante", "miya": "cent", "alf": "mille",
    "mjoz": "moitié", "qwi": "fort", "dh3af": "faible", "safi": "suffisant",
    "taman": "assez", "r7y": "rêve", "hbss": "souvenir", "fkr": "pense",
    "tfa99al": "essaye", "t9awwaj": "répète", "tksb": "écrit",
    "t9ul": "dit", "t9awl": "commence", "tkammel": "termine",
    "t9addem": "continue", "tjarreb": "rappelle", "t3allem": "enseigne",
    "t9awan": "travaille",     "t9aleb": "fait", "t9alebh": "fais-le",
    "t9albih": "fais-le", "t9alebha": "fais-la", "t9alebhom": "fais-les",
    "t9alebki": "fais (tu)", "t9albi": "fais (je)", "t9albu": "fais (nous)",
    "t9albhum": "fais (ils)", "hwaya": "lui", "homuma": "eux",
    "tji": "viens", "t9adhab": "pars", "t9allal": "donne",
    "t9awd": "rends", "t9achor": "cherche",
}

def _nettoyer_texte(t: str) -> str:
    """Normalise un peu le texte : minuscules, espaces, accents legers."""
    return t.strip().lower()

def _contient(text: str, mots: list) -> bool:
    return any(m in text for m in mots)

def _extraire_contact(text: str) -> str:
    """Recupere le nom de la personne a contacter (ex: 'mon frere Mohamed')."""
    t = text.lower()
    # On coupe avant les marqueurs de message pour ne pas les prendre pour un nom
    for mq in ["dis-lui", "dis lui", "dislui", "qouli", "lou", "colha"]:
        if mq in t:
            t = t.split(mq)[0]
            break
    m = re.search(r"(?:avec\s+)?(?:mon|ma|le|la|ton|ta)\s+(?P<qui>[a-z\u00e0-\u017f]+)(?:\s+(?P<nom>[a-z\u00e0-\u017f]+))?", t)
    if m:
        mots_stop = {"a", "le", "la", "de", "du", "pour", "demain", "apres",
                     "soir", "matin", "aujourd", "tout", "mon", "ma"}
        qui = m.group("qui")
        nom = m.group("nom")
        if nom and nom not in mots_stop:
            return f"{qui.capitalize()} {nom.capitalize()}".strip()
        if qui not in mots_stop:
            return qui.capitalize()
    return "Contact"

def _extraire_heure(text: str) -> str:
    """Recupere une heure type '10h' voire une heure complete 'a 16h'."""
    m = re.search(r"\b(\d{1,2})h(?:\s?(\d{2}))?\b", text)
    if m:
        h = int(m.group(1))
        mi = m.group(2) or "00"
        return f"{h:02d}:{mi}"
    return None

def _extraire_jour(text: str) -> str:
    t = text.lower()
    if "demain" in t or "غدوة" in t or "غدا" in t:
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if "apres-demain" in t or "بعد غد" in t:
        return (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    if "aujourd" in t or "lyoum" in t or "اليوم" in t:
        return datetime.now().strftime("%Y-%m-%d")
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", text)
    if m:
        j, mois, an = m.group(1), m.group(2), m.group(3) or str(datetime.now().year)
        return f"{int(an):04d}-{int(mois):02d}-{int(j):02d}"
    return datetime.now().strftime("%Y-%m-%d")

def _extraire_texte_message(text: str) -> str:
    """Pour un envoi de message : recupere le contenu apres 'dis-lui'."""
    m = re.search(r"(?:dis-lui|di-lui|dislui|qouli|lou)\s+(.+)$", text)
    if m:
        return m.group(1).strip().capitalize()
    return ""

def analyser(message: str) -> dict:
    """Analyse un message Tunisien et renvoie l'intention + infos.

    Ordre de priorite : les intentions d'ACTION (whatsapp, appel, rdv, email,
    trading, rappel) sont verifiees AVANT les politesses (salutation/merci/
    au-revoir) pour eviter qu'un message du type «whatsapp ... bonjour» ne soit
    classe a tort comme une simple salutation.
    """
    t = _nettoyer_texte(message)
    jour = _extraire_jour(t)
    heure = _extraire_heure(t)
    contact = _extraire_contact(t)

    if _contient(t, ["whatsapp", "msg", "wa", "انبوب", "واتساب", "واتس", "ابعت"]):
        corps = _extraire_texte_message(t)
        return {"intention": "whatsapp", "contact": contact, "jour": jour, "heure": heure, "texte": corps or message}
    if _contient(t, ["appelle", "appell", "telephone", "tel", "يطلب", "اتصل", "صل", "appeler"]):
        return {"intention": "call", "contact": contact, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["rdv", "rendez", "موعد", "لقاء", "حجز", "prends"]):
        return {"intention": "rdv", "contact": contact, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["email", "mail", "ecris a", "اكتب", "ايميل"]):
        return {"intention": "email", "contact": contact, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["binance", "invest", "investir", "gagne", "profit", "bitcoin", "b tc",
                     "btc", "crypto", "achete du", "vends ", "شراء", "اشتري", "اشتر", "بيع", "استثمار",
                     "بيتكوين", "سعر", "السعر", "ثمن", "تحليل", "صرف", "كريبتو", "عملة",
                     "cryptomonnaie"]):
        return {"intention": "trading", "contact": None, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["rappelle-moi", "rappel", "najm troufassni", "ذكرني", "فكرني", "ذكر", "rappelle le"]):
        return {"intention": "rappel", "contact": contact, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["planning", "programme", "agenda", "mon planning", "الجدول", "جدول", "برنامج", "plan du"]):
        return {"intention": "planning", "contact": None, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["saha", "bonjour", "salut", "sbah el khir", "hello", "بونجور",
                     "صحه", "صباح الخير", "السلام", "اهلا", "مرحبا"]):
        return {"intention": "salutation", "contact": None, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["merci", "chokran", "شكرا"]):
        return {"intention": "merci", "contact": None, "jour": jour, "heure": heure, "texte": message}
    if _contient(t, ["au revoir", "by", "bye", "مع السلامة", "بسلامة", "besslema"]):
        return {"intention": "au_revoir", "contact": None, "jour": jour, "heure": heure, "texte": message}
    return {"intention": "question", "contact": contact, "jour": jour, "heure": heure, "texte": message}


def repondre(intention: dict, nom_assistant: str = "Hmied حميد", mode: str = "simu") -> str:
    """Construit la reponse de l'assistant selon l'intention."""
    it = intention["intention"]
    contact = intention["contact"]
    jour = intention["jour"]
    heure = intention["heure"]
    texte = intention["texte"]

    if it == "salutation":
        return f"Saha ! Ana {nom_assistant}, relation. Qouli a3malt chkoun khair aujourd'hui ?"
    if it == "planning":
        return (f"Voici ton planning du {jour} : pour l'instant rien de prevu. "
                "Tu veux que je note un rendez-vous ?")
    if it == "rappel":
        h = heure or "16:00"
        c = contact if contact and contact != "Contact" else "le contact"
        if mode == "simu":
            return f"Bien recu. Je te rappellerai le {jour} a {h} ({c}). (Mode simu : aucun SMS envoyé.)"
        return f"Rappel programme le {jour} a {h} pour {c}."
    if it == "whatsapp":
        c = contact if contact and contact != "Contact" else "le contact"
        corps = texte if texte and len(texte) > 3 else "Message sans texte."
        if mode == "simu":
            return (f"OK ! Message WhatsApp envoye (simu) a {c} : « {corps} » "
                    "(configure un fournisseur dans config.py : Maytapi ou 360dialog, "
                    "Twilio etant bloque en Tunisie).")
        return f"Message WhatsApp envoye a {c} : « {corps} »."
    if it == "rdv":
        c = contact if contact and contact != "Contact" else "le contact"
        h = heure or "10:00"
        if mode == "simu":
            return (f"Rendez-vous note pour {c} le {jour} a {h}. "
                    "(Mode simu : je n'ai pas encore envoye d'invitation. "
                    "Accorde-moi la cle calendrier/Twilio pour le faire vraiment.)")
        return f"Rendez-vous cree avec {c} le {jour} a {h}. Invitation envoyee."
    if it == "email":
        if mode == "simu":
            return "Email prepare (simu). Configure SMTP dans config.py pour l'envoi."
        return "Email envoye."
    if it == "trading":
        return "J'ouvre mon analyse du marche des cryptos. Un instant..."
    if it == "merci":
        return "De rien ! N'hesite pas si tu as besoin d'autre chose."
    if it == "au_revoir":
        return "Besslema ! A bientot."
    if it == "call":
        c = contact if contact and contact != "Contact" else "le contact"
        return f"Je vais appeler {c} des maintenant. 📞"
    return (f"J'ai compris ta demande. Aide-moi un peu : est-ce que tu veux un rendez-vous, "
            "un message WhatsApp, un rappel, ou un email ? (tu peux dire par exemple "
            "« prends rendez-vous avec mon frere demain a 10h »)")


def executer(message: str, nom_assistant: str, mode: str) -> dict:
    """Pipeline complet : analyse -> reponse."""
    intention = analyser(message)
    reponse = repondre(intention, nom_assistant, mode)
    return {
        "intention": intention["intention"],
        "reponse": reponse,
        "infos": {k: v for k, v in intention.items() if k != "intention"},
    }


if __name__ == "__main__":
    tests = [
        "saha",
        "prends rendez-vous avec mon frere Mohamed demain a 10h",
        "rappelle-moi le medecin a 16h",
        "whatsapp mon frere dis-lui qu'on se voit demain ?",
        "merci",
    ]
    for msg in tests:
        print("->", msg)
        print("   ", executer(msg, "Hmied حميد", "simu"))
        print()