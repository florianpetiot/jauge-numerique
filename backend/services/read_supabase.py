from supabase import create_client, Client

SUPABASE_URL = "https://ogmxssczekgpwowgprjd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nbXhzc2N6ZWtncHdvd2dwcmpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNTA4NzcsImV4cCI6MjA4NjkyNjg3N30.-60sb4dzO9coZFbEmbC823WWvW_nitWftyasB3trUFA"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

mesured_diam_mm = 13.2
tolerance_diam = 0.1
mesured_pas = 1.24
tolerance_pas = 0.1

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