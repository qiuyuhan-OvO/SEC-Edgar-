# SEC-Edgar
根据CIK ticker与fyear 爬取SEC filing
## What it does

- Pulls `master.idx` by quarter and filters by:
  - CIK (zero-padded to 10 digits)
  - Form types: `10-K`,`DEF 14A`, `DEFA14A`
  - Filing date starting with the given fiscal year (e.g. `2001`)
- Or an excel with CIK and fyear
- Jumps to the filing `index.json` to find the main HTML document
- Downloads the HTML to a local folder with a clear file name
