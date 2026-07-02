import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.model_loader import load_model
from backend.fertilizer import load_fertilizer_data
from backend.database import init_db
from backend.routes import router

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML model once on startup
    load_model()
    # Load fertilizer data on startup
    load_fertilizer_data()
    # Init DB
    init_db()
    yield
    # Shutdown logic (if any)
    pass

app = FastAPI(
    title="AgriVision AI Backend",
    description="Backend API for Crop and Fertilizer Recommendation",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS so Streamlit (or other frontends) can make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
