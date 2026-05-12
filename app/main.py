import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db, init_db
from .metrics import REDIRECTS, MetricsMiddleware
from .models import Link
from .shortcode import generate_code

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("linkly")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("database ready, app starting up")
    yield


app = FastAPI(title="linkly", version="0.1.0", lifespan=lifespan)
app.add_middleware(MetricsMiddleware)


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    target_url: str


class StatsResponse(BaseModel):
    code: str
    target_url: str
    clicks: int
    created_at: datetime


@app.post("/api/shorten", response_model=ShortenResponse, status_code=201)
def shorten(payload: ShortenRequest, db: Session = Depends(get_db)):
    target = str(payload.url)

    code = None
    for _ in range(5):
        candidate = generate_code(settings.code_length)
        if not db.query(Link).filter(Link.code == candidate).first():
            code = candidate
            break
    if code is None:
        raise HTTPException(status_code=500, detail="could not generate a unique code")

    db.add(Link(code=code, target_url=target))
    db.commit()
    logger.info("created short link %s -> %s", code, target)
    return ShortenResponse(
        code=code,
        short_url=f"{settings.base_url}/{code}",
        target_url=target,
    )


@app.get("/api/stats/{code}", response_model=StatsResponse)
def stats(code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.code == code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="code not found")
    return StatsResponse(
        code=link.code,
        target_url=link.target_url,
        clicks=link.clicks,
        created_at=link.created_at,
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database not ready") from None
    return {"status": "ready"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.code == code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="code not found")
    link.clicks += 1
    db.commit()
    REDIRECTS.inc()
    return RedirectResponse(url=link.target_url, status_code=302)
