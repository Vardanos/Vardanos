"""Tiny stdlib HTTP helper with retries and polite back-off."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "armenia-science/0.1 (+https://github.com/vardanos/vardanos)"


def get_json(url, params=None, retries=5, backoff=2.0):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            # Budget/rate-limit errors with a long retry window will not clear by waiting.
            if e.code == 429 and "Insufficient budget" in body:
                raise RuntimeError(f"Rate limit/budget exhausted for {url}: {body}") from e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(backoff * 2**attempt)
                continue
            raise RuntimeError(f"HTTP {e.code} for {url}: {body}") from e
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(backoff * 2**attempt)
                continue
            raise
