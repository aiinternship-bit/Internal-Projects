"""
Configuration settings for Excel-RAG system
Loads from environment variables with fallback defaults
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Database settings
# ============================================================================
DB_PATH = os.getenv("DB_PATH", "./milvus_edelivery.db")
STRUCTURE_COLLECTION = "excel_structure_vectors"
CONTENT_COLLECTION = "excel_vectors"

# ============================================================================
# Embedding settings
# ============================================================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 produces 384-dim vectors

# ============================================================================
# Milvus settings
# ============================================================================
INDEX_TYPE = os.getenv("INDEX_TYPE", "HNSW")
METRIC_TYPE = os.getenv("METRIC_TYPE", "COSINE")

# IVF_FLAT parameters (kept for reference, not used with HNSW)
NLIST = int(os.getenv("NLIST", "4096"))  # Number of clusters for IVF
NPROBE = int(os.getenv("NPROBE", "400"))  # Number of clusters to search

# HNSW parameters
M = int(os.getenv("M", "16"))  # Number of connections per layer (higher = better recall, more memory)
EF_CONSTRUCTION = int(os.getenv("EF_CONSTRUCTION", "200"))  # Size of dynamic candidate list for construction
EF = int(os.getenv("EF", "128"))  # Size of dynamic candidate list for search (increased from 64 for better recall)

# ============================================================================
# Batch processing
# ============================================================================
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))

# ============================================================================
# Excel settings
# ============================================================================
EXCEL_FILE = os.getenv("EXCEL_FILE", "eDelivery_AIeDelivery_Database_V1.xlsx")

# ============================================================================
# Query settings
# ============================================================================
TOP_K_STRUCTURE = int(os.getenv("TOP_K_STRUCTURE", "5"))  # Top-k sheets/columns (increased from 3)
TOP_K_CONTENT = int(os.getenv("TOP_K_CONTENT", "10"))     # Top-k rows (increased from 5)

# ============================================================================
# API Keys (loaded from environment)
# ============================================================================
# Ollama (local LLM server - highest priority)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# Cloud LLM providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ============================================================================
# LangSmith Configuration
# ============================================================================
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "excel-rag-system")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "")

# ============================================================================
# Helper functions
# ============================================================================

def is_langsmith_enabled() -> bool:
    """Check if LangSmith tracing is enabled and configured"""
    return LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY is not None

def is_ollama_configured() -> bool:
    """Check if Ollama is configured and accessible"""
    if not OLLAMA_BASE_URL:
        return False
    try:
        import requests
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def is_openai_key_valid() -> bool:
    """Check if OpenAI API key is valid"""
    if not OPENAI_API_KEY:
        return False
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        # Use the models endpoint - minimal request
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=3
        )
        return response.status_code == 200
    except:
        return False

def is_anthropic_key_valid() -> bool:
    """Check if Anthropic API key is valid"""
    if not ANTHROPIC_API_KEY:
        return False
    try:
        import requests
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        # Make a minimal request to validate the key
        # Using messages endpoint with minimal payload
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "test"}]
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=3
        )
        # 200 = success, 400 might be rate limit but key is valid
        return response.status_code in [200, 400, 429]
    except:
        return False

def get_default_llm_model() -> str:
    """Auto-detect best available LLM model"""
    if is_ollama_configured():
        return OLLAMA_MODEL or "ollama"
    elif is_anthropic_key_valid():
        return "claude-3-haiku-20240307"
    elif is_openai_key_valid():
        return "gpt-3.5-turbo"
    else:
        return "mock"

def get_api_key_status() -> dict:
    """Get status of API keys for diagnostics"""
    ollama_status = "✓ Configured" if is_ollama_configured() else "✗ Not configured"

    # Check OpenAI key validity
    if not OPENAI_API_KEY:
        openai_status = "✗ Not set"
    elif is_openai_key_valid():
        openai_status = "✓ Valid"
    else:
        openai_status = "⚠ Set but invalid"

    # Check Anthropic key validity
    if not ANTHROPIC_API_KEY:
        anthropic_status = "✗ Not set"
    elif is_anthropic_key_valid():
        anthropic_status = "✓ Valid"
    else:
        anthropic_status = "⚠ Set but invalid"

    return {
        "ollama": ollama_status,
        "openai": openai_status,
        "anthropic": anthropic_status,
        "langsmith": "✓ Set" if LANGCHAIN_API_KEY else "✗ Not set",
    }

# ============================================================================
# LLM settings (defined after API key helpers)
# ============================================================================
LLM_MODEL = os.getenv("LLM_MODEL", get_default_llm_model())
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

def print_config_summary():
    """Print configuration summary for debugging"""
    print("\n" + "=" * 60)
    print("EXCEL-RAG CONFIGURATION")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Excel file: {EXCEL_FILE}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"LLM model: {LLM_MODEL}")
    print(f"\nAPI Keys:")
    for service, status in get_api_key_status().items():
        print(f"  {service}: {status}")
    print(f"\nLangSmith:")
    print(f"  Tracing enabled: {LANGCHAIN_TRACING_V2}")
    print(f"  Project: {LANGCHAIN_PROJECT}")
    print("=" * 60 + "\n")
