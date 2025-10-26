import os, csv

LOGOS_DIR = "logos_downloaded"
CSV_PATH = os.path.join(LOGOS_DIR, "logos_found.csv")

# extrage toate imaginile din logos_downloaded
files = [f for f in os.listdir(LOGOS_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".ico", ".svg", ".webp"))]

rows = []
for f in files:
    domain_guess = f.split("__")[0]  # dacă fișierele au fost salvate cu pattern domain__hash.ext
    rows.append({
        "domain": domain_guess,
        "status": "ok",
        "logo_url": "",
        "file": os.path.join(LOGOS_DIR, f)
    })

# scrie CSV
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["domain", "status", "logo_url", "file"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Am creat {CSV_PATH} cu {len(rows)} înregistrări.")
