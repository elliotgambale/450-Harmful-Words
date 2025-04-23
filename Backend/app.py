from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from detoxify import Detoxify
import httpx
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

detox = Detoxify("unbiased")

class URLRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze(request: URLRequest):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/112.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(request.url, timeout=10.0, headers=headers)
            resp.raise_for_status()
    except Exception as e:
        logging.error("Fetch error (%s): %s", type(e).__name__, e)
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    # … scraping + detoxify logic remains …


    # extract visible text …
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = " ".join(soup.stripped_strings)[:10000]

    # run detoxify
    raw_results = detox.predict(text)

    # convert numpy scalars to plain Python types
    results: dict[str, float] = {}
    for key, val in raw_results.items():
        try:
            results[key] = val.item()   # numpy scalar → Python float/bool
        except AttributeError:
            results[key] = val         # already a native type

    # pick out the toxicity score (now a Python float)
    toxic_score = results.get('toxicity', results.get('toxic', 0.0))
    threshold = 0.5

    return {
        "is_toxic": toxic_score > threshold,  # Python bool
        "toxic_score": toxic_score,            # Python float
        "threshold": threshold,
        "all_scores": results                   # all native scalars now
    }
