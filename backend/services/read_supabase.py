from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL et/ou SUPABASE_KEY ne sont pas définis dans les variables d'environnement.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# mesured_diam_mm = 13.2
# tolerance_diam = 0.1
# mesured_pas = 1.24
# tolerance_pas = 0.1


def find_match_supabase(mesured_diam_mm: float, tolerance_diam: float, mesured_pas: float, tolerance_pas: float) -> Any:
    diam_min = mesured_diam_mm - tolerance_diam
    diam_max = mesured_diam_mm + tolerance_diam

    pas_min_metric = mesured_pas - tolerance_pas
    pas_max_metric = mesured_pas + tolerance_pas

    pas_min_imperial = 25.4 / (mesured_pas + tolerance_pas)
    pas_max_imperial = 25.4 / (mesured_pas - tolerance_pas)

    response = supabase.table("normes") \
        .select("*") \
        .gte("diam_mm", diam_min) \
        .lte("diam_mm", diam_max) \
        .or_(
            f"and(unite.eq.M,pas.gte.{pas_min_metric},pas.lte.{pas_max_metric}),"
            f"and(unite.eq.I,pas.gte.{pas_min_imperial},pas.lte.{pas_max_imperial})"
        ) \
        .execute()

    print(response.data)
    return response.data