-- Petit modèle de test : lit la table raw remplie par collecte.py
-- et la nettoie un peu. Sert juste à prouver que dbt tourne dans GitHub Actions.

select
    event_id,
    user            as user_name,
    montant,
    row_hash,
    inserted_at
from {{ source('ga', 'raw_events') }}
