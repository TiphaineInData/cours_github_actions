# load_data.py — VERSION DE TEST (fausses donnees) pour tester GitHub Actions.
#
# Dans VOTRE vrai projet, load_data.py appelle une vraie API. Ici, on invente
# des donnees pour verifier que l'automatisation fonctionne, sans dependre du reseau.
# Meme nom de fonction que d'habitude : ingest_data().

import hashlib
import json
import random
from datetime import datetime, timezone

from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

client = bigquery.Client()

# A ADAPTER a votre projet / dataset :
TABLE_ID = "data-quest-tiphaine.ga_test.raw_events"


def generer_donnees(n=5):
    """Invente n lignes bidon (a la place d'un vrai appel API)."""
    prenoms = ["Alice", "Bob", "Chloe", "David", "Emma", "Farid", "Guo", "Hana"]
    return [
        {
            "event_id": random.randint(1, 1_000_000),
            "user": random.choice(prenoms),
            "montant": round(random.uniform(5, 200), 2),
        }
        for _ in range(n)
    ]


def calculer_hash(row):
    """Empreinte SHA-256 stable des donnees (hors inserted_at)."""
    return hashlib.sha256(
        json.dumps(row, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def enrichir(data):
    """Ajoute row_hash (sur les donnees brutes) puis inserted_at."""
    now = datetime.now(timezone.utc).isoformat()
    out = []
    for row in data:
        ligne = dict(row)
        ligne["row_hash"] = calculer_hash(row)
        ligne["inserted_at"] = now
        out.append(ligne)
    return out


def ingest_data():
    data = enrichir(generer_donnees())
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        autodetect=True,
    )
    client.load_table_from_json(data, TABLE_ID, job_config=job_config).result()
    print(f"Succes : {len(data)} lignes inserees dans {TABLE_ID}.")


if __name__ == "__main__":
    ingest_data()
