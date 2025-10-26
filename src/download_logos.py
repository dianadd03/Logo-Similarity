import os, requests, urllib.parse, hashlib, csv
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

INPUT_PARQUET = "logos.snappy.parquet"
OUTPUT_DIR = "logos_downloaded"
META_PATH = os.path.join(OUTPUT_DIR, "logos_found.csv")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_site_url(domain):
    return f"https://{domain.strip()}"

def absolutize(base, url):
    return urllib.parse.urljoin(base, url)

def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.text, r.url
    except Exception as e:
        print(f"[ERR] {url} -> {e}")
        return None, None

def find_logo_url(domain):
    url = build_site_url(domain)
    html, final_url = fetch_html(url)
    if not html:
        return None, None

    soup = BeautifulSoup(html, "lxml")

    logo = None
    for prop in ["og:logo", "og:image", "twitter:image"]:
        m = soup.find("meta", attrs={"property": prop})
        if m and m.get("content"):
            logo = absolutize(final_url, m["content"])
            break

    if not logo:
        link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        if link and link.get("href"):
            logo = absolutize(final_url, link["href"])

    if not logo:
        img = soup.find("img", attrs={"alt": lambda x: x and "logo" in x.lower()})
        if img and img.get("src"):
            logo = absolutize(final_url, img["src"])

    if not logo:
        logo = absolutize(final_url, "/favicon.ico")

    return logo, final_url

def download_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"[ERR IMG] {url} -> {e}")
        return None

def save_image(content, domain):
    ext = ".png"
    try:
        im = Image.open(BytesIO(content))
        fmt = im.format.lower()
        if fmt in ["jpeg", "jpg", "png", "ico", "svg", "webp"]:
            ext = "." + ("jpg" if fmt == "jpeg" else fmt)
    except:
        pass
    fname = hashlib.sha1(domain.encode()).hexdigest()[:12] + ext
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, "wb") as f:
        f.write(content)
    return path

def main():
    import pandas as pd
    df = pd.read_parquet(INPUT_PARQUET)

    results = []
    for i, row in df.iterrows():
        domain = row["domain"]
        print(f"[{i+1}/{len(df)}] {domain}")
        logo_url, site_url = find_logo_url(domain)
        if not logo_url:
            results.append({"domain": domain, "status": "no_logo"})
            continue
        content = download_image(logo_url)
        if not content:
            results.append({"domain": domain, "status": "download_failed"})
            continue
        path = save_image(content, domain)
        results.append({"domain": domain, "status": "ok", "logo_url": logo_url, "file": path})
        print(f"Saved: {path}")

    with open(META_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "status", "logo_url", "file"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Logos in {OUTPUT_DIR}, metadata in {META_PATH}")

if __name__ == "__main__":
    main()
