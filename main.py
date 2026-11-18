
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router


app = FastAPI(
    title="Enterprise RAG Assistant",
    description="An intelligent assistant for enterprise documents",
    version="0.1.0"
)

# Register API routers
app.include_router(health_router)
app.include_router(documents_router)
