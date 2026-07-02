# Kit de test — automatiser le pipeline avec GitHub Actions

Ce petit projet sert à **tester l'automatisation** d'un pipeline (ingestion -> dbt)
avec **GitHub Actions**, avec de **fausses données** (aucune API externe requise).

À chaque exécution, `run_pipeline.py` :
1. lance `load_data.py` (fonction `ingest_data`) : invente des lignes (+ `row_hash` + `inserted_at`) et les charge dans BigQuery (`ga_test.raw_events`) ;
2. lance `dbt run` : transforme cette table brute (`stg_events`).

L'`inserted_at` permet de **vérifier que le job s'est bien déclenché à telle heure**.

## Structure

```
test_github_actions/
├── load_data.py                # ingestion (fausses données) -> BigQuery raw
├── run_pipeline.py             # lance ingestion PUIS dbt (une commande)
├── requirements.txt            # dépendances
├── .github/workflows/pipeline.yml   # le workflow GitHub Actions (cron + bouton)
└── dbt_ga/                     # mini projet dbt
    ├── dbt_project.yml
    └── models/
        ├── sources.yml
        └── stg_events.sql
```

> Le `profiles.yml` n'est PAS dans le projet : comme pour tout projet dbt, il vit dans `~/.dbt/profiles.yml`. En local vous l'y avez déjà ; sur GitHub Actions, le workflow le recrée dans `~/.dbt/`.

## Mise en place (une fois)

1. **Créez le dataset BigQuery** `ga_test` :
   ```bash
   bq --location=US mk --dataset VOTRE_PROJET:ga_test
   ```
2. **Poussez ce dossier comme un dépôt GitHub.**
3. Dépôt → **Settings → Secrets and variables → Actions → New repository secret**
   - Nom : `GCP_SA_KEY` — Valeur : tout le contenu de votre `cle_bigquery.json`
4. Adaptez `data-quest-tiphaine` (projet) dans `load_data.py`, `dbt_ga/models/sources.yml` et le workflow.

## Tester

- **Tout de suite** : onglet **Actions** → *Pipeline (ingestion + dbt)* → **Run workflow**.
- **Automatique** : le `cron: "0 * * * *"` déclenche le job **chaque heure**.

## Vérifier

```sql
SELECT inserted_at, COUNT(*) AS n
FROM `VOTRE_PROJET.ga_test.raw_events`
GROUP BY inserted_at
ORDER BY inserted_at DESC;
```
Chaque `inserted_at` = une exécution du pipeline.

## Tester en local (sans GitHub)

1. Ajoutez un profil `dbt_ga` à votre `~/.dbt/profiles.yml` (project, dataset, keyfile) — comme pour vos autres projets dbt.
2. Depuis `test_github_actions/`, la clé accessible :
   ```bash
   uv run python run_pipeline.py
   ```
   (le script lance l'ingestion puis `dbt run --project-dir dbt_ga`, qui lit le profil dans `~/.dbt`)
