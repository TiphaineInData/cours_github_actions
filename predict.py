# predict.py
# Calcule les predictions du jour et les ecrit dans BigQuery.
# Meme structure que ton load_data.py : une fonction + un if __name__,
# pour pouvoir l'importer depuis run_pipeline.py (comme ingest_data).
# Ce n'est PAS du dbt : c'est un script Python qui lit les dernieres donnees,
# applique le modele (pipeline.pkl), et ecrit le resultat dans le dataset ml.

import joblib
from datetime import datetime, timezone
from google.cloud import bigquery

PROJECT = "data-quest-tiphaine"   # ton projet GCP
RAW = "raw_data"                  # le dataset raw alimente par load_data.py
ML = "ml"                         # le nouveau dataset dedie au ML
TABLE_SOURCE = "ventes"           # ta table dans raw_data (adapte le nom)


def predire():
    client = bigquery.Client(project=PROJECT)

    # 1) LIRE les dernieres lignes ingerees = les donnees a predire
    df = client.query(f"""
        SELECT jour, promo, nb_articles
        FROM `{PROJECT}.{RAW}.{TABLE_SOURCE}`
        ORDER BY inserted_at DESC
        LIMIT 3
    """).to_dataframe(create_bqstorage_client=False)

    # 2) PREDIRE avec le pipeline entraine (preprocessing + modele dans le .pkl)
    pipeline = joblib.load("pipeline.pkl")
    df["montant_predit"] = pipeline.predict(df[["jour", "promo", "nb_articles"]]).round(1)
    df["date_prediction"] = datetime.now(timezone.utc)   # pour garder l'historique

    # 3) ECRIRE dans le dataset ml, en AJOUTANT a la suite (WRITE_APPEND : on garde l'historique)
    client.load_table_from_dataframe(
        df,
        f"{PROJECT}.{ML}.predictions",
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"),
    ).result()

    print(f"{len(df)} predictions ajoutees dans {ML}.predictions")
    print(df)


if __name__ == "__main__":
    predire()
