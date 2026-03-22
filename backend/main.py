import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import sections, canvas, generate, validate, projects
from backend.services import llm_service

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify that LM Studio is reachable when the server starts."""
    status = await llm_service.check_lm_studio_status()
    if status["lm_studio"] == "online":
        logger.info("LM Studio is reachable at %s", llm_service.LM_STUDIO_BASE_URL)
    else:
        logger.warning(
            "LM Studio not reachable at startup (%s). "
            "The server will still start but AI generation will use template fallback "
            "until LM Studio is running.",
            status.get("error", "unknown"),
        )
    yield


app = FastAPI(
    title="TechWriter API",
    description="Technical Writing Canvas Architect - API for managing academic paper sections",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(sections.router)
app.include_router(canvas.router)
app.include_router(generate.router)
app.include_router(validate.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/status")
async def status():
    """Check whether LM Studio is currently reachable."""
    return await llm_service.check_lm_studio_status()
