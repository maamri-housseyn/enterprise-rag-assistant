from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Welcome to Enterprise RAG Assistant!",
        "status": "API is running"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy"
    }