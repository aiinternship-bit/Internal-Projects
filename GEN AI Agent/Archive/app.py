"""
eDelivery RAG API
FastAPI application that automatically downloads Milvus DB from GCS on startup
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional, List
import logging

# Import our modules
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer
from src.milvus_gcs_utils import ensure_milvus_available
from src import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="eDelivery RAG API",
    description="Retrieval-Augmented Generation API for eDelivery Database",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for database and LLM
query_engine: Optional[QueryEngine] = None
llm_layer: Optional[LLMLayer] = None

# Configuration from environment variables
DB_PATH = os.getenv("DB_PATH", "/app/milvus_edelivery.db")
GCS_BUCKET = os.getenv("GCS_BUCKET", "edeliverydata")
GCS_DB_PATH = os.getenv("GCS_DB_PATH", "milvus_edelivery.db")


class QueryRequest(BaseModel):
    """Request model for queries"""
    question: str
    top_k_structure: Optional[int] = 5
    top_k_content: Optional[int] = 10


class QueryResponse(BaseModel):
    """Response model for queries"""
    question: str
    answer: str
    model: str
    backend: str
    token_usage: str
    retrieved_sheets: List[str]
    num_content_results: int


@app.on_event("startup")
async def startup_event():
    """
    Download Milvus database from GCS on application startup
    This runs once when the Cloud Run container starts
    """
    global query_engine, llm_layer

    logger.info("="*80)
    logger.info("EDELIVERY RAG API STARTUP")
    logger.info("="*80)

    # Step 1: Ensure Milvus database is available
    logger.info("Step 1: Downloading Milvus database from GCS (if needed)...")
    logger.info(f"  GCS Location: gs://{GCS_BUCKET}/{GCS_DB_PATH}")
    logger.info(f"  Local Path: {DB_PATH}")

    try:
        success = ensure_milvus_available(
            local_db_path=DB_PATH,
            bucket_name=GCS_BUCKET,
            gcs_file_path=GCS_DB_PATH,
            force_download=False  # Use cached version if available
        )

        if not success:
            logger.error("Failed to download Milvus database from GCS")
            raise RuntimeError("Failed to initialize Milvus database")

        logger.info("✓ Milvus database is ready")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise

    # Step 2: Initialize query engine
    logger.info("Step 2: Initializing query engine...")
    try:
        query_engine = QueryEngine(DB_PATH)
        logger.info("✓ Query engine initialized")
    except Exception as e:
        logger.error(f"Error initializing query engine: {e}")
        raise

    # Step 3: Initialize LLM layer
    logger.info("Step 3: Initializing LLM layer...")
    try:
        llm_layer = LLMLayer()
        logger.info(f"✓ LLM initialized (backend: {llm_layer.backend}, model: {llm_layer.model_name})")
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise

    logger.info("="*80)
    logger.info("✅ EDELIVERY RAG API READY")
    logger.info("="*80)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "eDelivery RAG API",
        "version": "1.0.0",
        "database": "ready" if query_engine is not None else "not initialized"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "query_engine": "ready" if query_engine is not None else "not initialized",
        "llm": "ready" if llm_layer is not None else "not initialized",
        "db_path": DB_PATH,
        "gcs_bucket": GCS_BUCKET
    }


@app.post("/query", response_model=QueryResponse)
async def query_edelivery(request: QueryRequest):
    """
    Query the eDelivery database using RAG

    Args:
        request: QueryRequest with question and optional parameters

    Returns:
        QueryResponse with answer and metadata
    """
    if query_engine is None or llm_layer is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Database or LLM not initialized."
        )

    try:
        logger.info(f"Processing query: {request.question}")

        # Step 1: Retrieve relevant documents
        results = query_engine.query(
            query=request.question,
            top_k_structure=request.top_k_structure,
            top_k_content=request.top_k_content
        )

        logger.info(f"Retrieved {len(results['structure_results'])} sheets, {len(results['content_results'])} content items")

        # Step 2: Generate answer with LLM
        response = llm_layer.generate_answer(
            context=results["context"],
            query=request.question
        )

        # Step 3: Prepare response
        retrieved_sheets = [s["sheet"] for s in results["structure_results"]]

        return QueryResponse(
            question=request.question,
            answer=response["answer"],
            model=response["model"],
            backend=response["backend"],
            token_usage=response["token_usage"],
            retrieved_sheets=retrieved_sheets,
            num_content_results=len(results["content_results"])
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_only(request: QueryRequest):
    """
    Search the database without LLM generation
    Returns raw search results
    """
    if query_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Database not initialized."
        )

    try:
        results = query_engine.query(
            query=request.question,
            top_k_structure=request.top_k_structure,
            top_k_content=request.top_k_content
        )

        return {
            "question": request.question,
            "structure_results": results["structure_results"],
            "content_results": results["content_results"][:10],  # Limit to top 10
            "total_content_results": len(results["content_results"])
        }

    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_level="info"
    )
