import os, csv, itertools
from PIL import Image
import imagehash
import pandas as pd

LOGOS_DIR = "logos_downloaded"
META_CSV = os.path.join(LOGOS_DIR, "logos_found.csv")
HASH_CSV = os.path.join(LOGOS_DIR, "logo_hashes.csv")
GROUPS_CSV = os.path.join(LOGOS_DIR, "logo_groups.csv")

def load_logos():
    df = pd.read_csv(META_CSV)
    df = df[df["status"] == "ok"]
    files = df["file"].dropna().tolist()
    domains = df["domain"].dropna().tolist()
    return list(zip(domains, files))

def compute_hashes(pairs):
    results = []
    for domain, path in pairs:
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                h = imagehash.phash(img)
                results.append({"domain": domain, "file": path, "hash": str(h)})
        except Exception as e:
            print(f"[ERR] {domain} -> {e}")
    return results

def group_by_similarity(data, threshold=8):

    groups = []
    used = set()

    for i, row in enumerate(data):
        if i in used:
            continue
        group = [row]
        used.add(i)
        for j, other in enumerate(data[i + 1 :], start=i + 1):
            if j in used:
                continue
            dist = imagehash.hex_to_hash(row["hash"]) - imagehash.hex_to_hash(other["hash"])
            if dist <= threshold:
                group.append(other)
                used.add(j)
        groups.append(group)
    return groups

def main():
    pairs = load_logos()
    print(f"Avem {len(pairs)} imagini pentru analiză.")

    hashes = compute_hashes(pairs)
    pd.DataFrame(hashes).to_csv(HASH_CSV, index=False)
    print(f"Hash-uri salvate în {HASH_CSV}")

    groups = group_by_similarity(hashes, threshold=8)
    print(f"Am format {len(groups)} grupuri de logouri similare.")

    rows = []
    for gid, group in enumerate(groups, start=1):
        for item in group:
            rows.append({"group_id": gid, "domain": item["domain"], "file": item["file"]})
    pd.DataFrame(rows).to_csv(GROUPS_CSV, index=False)
    print(f"Grupurile au fost salvate în {GROUPS_CSV}")

    print("\nExemple de grupuri:")
    for g in groups[:5]:
        print("Group:")
        for item in g:
            print("  ", item["domain"])
        print()

if __name__ == "__main__":
    main()
