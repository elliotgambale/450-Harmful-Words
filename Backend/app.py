# app.py
# test committ
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from detoxify import Detoxify
import httpx
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Toxicity API is up and running!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # adjust in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# load the "broad toxicity" model
detox = Detoxify('unbiased')

class URLRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze(request: URLRequest):
    # fetch page …
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(request.url, timeout=10.0)
            resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

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
