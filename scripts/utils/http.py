import time

import requests

DEFAULT_HEADERS = {"User-Agent": "NUVIEW-Intel-Bot/1.0 (contact@nuview.space)", "Accept": "application/json, text/html"}

def safe_get(url, params=None, headers=None, timeout=20, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            resp = requests.get(url, params=params, headers={**DEFAULT_HEADERS, **(headers or {})}, timeout=timeout)
            if resp.status_code == 429:
                time.sleep(int(resp.headers.get("Retry-After", 5)))
                attempt += 1
                continue
            resp.raise_for_status()
            return resp
        except Exception:
            attempt += 1
            time.sleep(2 ** attempt)
    return None
