# run_pipeline.py — lance TOUT le pipeline en une seule commande :
# 1) l'ingestion (load_data.py -> BigQuery raw), 2) dbt.
# C'est CE script que GitHub Actions executera.

import subprocess

from load_data import ingest_data   # reutilise load_data.py (grace a if __name__ == "__main__")
from predict import predire         # <-- NOUVEAU : la prediction ML

# 1. Ingestion : donnees -> raw
print("=== 1. Ingestion (load_data -> raw) ===")
ingest_data()

# 2. Transformation dbt
print("\n=== 2. dbt run (raw -> stg_events) ===")
subprocess.run(
    ["dbt", "run", "--project-dir", "dbt_ga"],   # profil lu dans ~/.dbt (comme d'habitude)
    check=True,   # stoppe si dbt echoue
)

# 3. Prediction : lit raw_data.ventes, applique pipeline.pkl, ecrit ml.predictions
print("\n=== 3. Predictions (ml.predictions) ===")   # <-- NOUVEAU
predire()

print("\nPipeline termine avec succes.")
