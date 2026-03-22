from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import sections, canvas, generate, validate, projects

app = FastAPI(
    title="TechWriter API",
    description="Technical Writing Canvas Architect - API for managing academic paper sections",
    version="1.0.0",
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
