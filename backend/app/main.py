from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.api import api_router
from strawberry.fastapi import GraphQLRouter
from app.api.v1.graphql.monitoring import schema
from app.api.v1.graphql.context import get_context
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=True
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development environment
        "https://monitories.com",  # Production environment
        "https://monitories.com"  # Production environment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Add GraphQL endpoint
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)
app.include_router(graphql_app, prefix="/graphql")

# Add REST API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Monitories API"}
