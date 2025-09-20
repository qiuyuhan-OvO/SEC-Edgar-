##For example,to download DEF 14A （proxy statement） from Edgar 
import os
import time
import argparse
import requests

def fetch_master_idx(year: int, quarter: int, headers: dict) -> str:
    url = f"https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{quarter}/master.idx"
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text

def parse_master_idx(text: str, cik_target: str, fyear: int, form_types=None):
    if form_types is None:
        form_types = {"DEF 14A", "DEFA14A"}
    out = []
    cik_target = str(cik_target).zfill(10)
    for line in text.splitlines():
        # master.idx lines look like: CIK|Company|Form|Date|Path
        if line.count("|") < 4:
            continue
        cik, name, form, date, filename = [p.strip() for p in line.split("|", 4)]
        if cik.zfill(10) == cik_target and form in form_types and date.startswith(str(fyear)):
            out.append({"cik": cik.zfill(10), "form": form, "date": date, "filename": filename})
    return out

def pick_main_html_from_index_json(cik: str, accession: str, headers: dict, form_type: str):
    no_dash = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{no_dash}/index.json"
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    items = data.get("directory", {}).get("item", [])
    # try: match by form keyword
    key = form_type.replace(" ", "").lower()
    for it in items:
        name = it.get("name", "")
        if name.endswith(".htm") and key in name.lower():
            return name
    # fallback: first .htm
    for it in items:
        name = it.get("name", "")
        if name.endswith(".htm"):
            return name
    return None

def download_def14a_html(cik: str, fyear: int, out_dir: str, email: str, forms: list):
    os.makedirs(out_dir, exist_ok=True)
    headers = {"User-Agent": f"{email} (research; SEC-Edgar downloader)"}
    cik10 = str(cik).zfill(10)

    for q in range(1, 5):
        try:
            idx_text = fetch_master_idx(fyear, q, headers)
            recs = parse_master_idx(idx_text, cik10, fyear, set(forms))
            if not recs:
                continue

            for rec in recs:
                accession = rec["filename"].rsplit("/", 1)[-1].replace(".txt", "")
                html_name = pick_main_html_from_index_json(rec["cik"], accession, headers, rec["form"])
                if not html_name:
                    continue
                base = f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{accession.replace('-', '')}"
                url = f"{base}/{html_name}"
                save_name = f"{rec['cik']}_{rec['date']}_{rec['form'].replace(' ', '')}.html"
                save_path = os.path.join(out_dir, save_name)

                print(f"Downloading: {url}")
                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(r.text)
                    print(f"Saved: {save_path}")
                    return True
        except Exception as e:
            # keep going across quarters/records
            print(f"Warning (Q{q}): {e}")
        time.sleep(0.4)

    print(f"No DEF14A/DEFA14A found for {cik10} in {fyear}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Download DEF14A/DEFA14A HTML by CIK + fiscal year.")
    parser.add_argument("--cik", required=True, help="Company CIK (int or str).")
    parser.add_argument("--fyear", required=True, type=int, help="Fiscal year to match filing date prefix.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--email", required=True, help="Contact email for SEC User-Agent.")
    parser.add_argument("--forms", default="DEF 14A,DEFA14A", help="Comma-separated form types.")
    args = parser.parse_args()

    forms = [s.strip() for s in args.forms.split(",") if s.strip()]
    download_def14a_html(args.cik, args.fyear, args.out, args.email, forms)

if __name__ == "__main__":
    main()
