# SEC-Edgar
根据CIK ticker与fyear 爬取SEC filing
## What it does

- Pulls `master.idx` by quarter and filters by:
  - CIK (zero-padded to 10 digits)
  - Form types: `DEF 14A`, `DEFA14A`
  - Filing date starting with the given fiscal year (e.g. `2001`)
- Jumps to the filing `index.json` to find the main HTML document
- Downloads the HTML to a local folder with a clear file name

## Quick start

```bash
pip install -r requirements.txt

python src/sec_edgar_download.py \
  --cik 1750 \
  --fyear 2001 \
  --out ~/Documents/pachong_master_index \
  --email your_email@example.com
