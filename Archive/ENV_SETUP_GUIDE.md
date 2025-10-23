# Environment Setup Guide

Complete guide for configuring environment variables, API keys, and LangSmith integration.

## Quick Setup

### 1. Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

### 2. Configure Required Values

At minimum, set these in your `.env` file:

```bash
# For using GPT models
OPENAI_API_KEY=sk-your-key-here

# For using Claude models
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For LangSmith tracing (optional but recommended)
LANGCHAIN_API_KEY=ls-your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=excel-rag-system
```

### 3. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Verify Configuration

```bash
python -c "from src.config import print_config_summary; print_config_summary()"
```

---

## Environment Variables Reference

### LLM API Keys

#### OpenAI (for GPT models)

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Get your key:** https://platform.openai.com/api-keys

**Models supported:**
- `gpt-3.5-turbo` (fast, cheap)
- `gpt-4` (more capable, expensive)
- `gpt-4-turbo` (best balance)

**Usage:**
```bash
python main.py query "your question" --llm gpt-3.5-turbo
```

#### Anthropic (for Claude models)

```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

**Get your key:** https://console.anthropic.com/settings/keys

**Models supported:**
- `claude-3-haiku-20240307` (fast, cheap)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-opus-20240229` (most capable)

**Usage:**
```bash
python main.py query "your question" --llm claude-3-sonnet-20240229
```

---

### LangSmith Configuration

LangSmith provides:
- ✓ Tracing of all queries and LLM calls
- ✓ Performance monitoring
- ✓ Token usage tracking
- ✓ Error logging
- ✓ Debugging and diagnostics

#### Setup LangSmith

1. **Sign up:** https://smith.langchain.com/

2. **Get API key:** Settings → API Keys → Create API Key

3. **Configure in .env:**
```bash
LANGCHAIN_API_KEY=ls-your-langsmith-api-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=excel-rag-system
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

4. **Verify it's working:**
```bash
python main.py query "test query" --llm mock
```

5. **Check traces:** Visit https://smith.langchain.com/ and view your project

#### What Gets Traced

- ✓ Every query execution (with timing)
- ✓ Structure retrieval operations
- ✓ Content retrieval operations
- ✓ LLM API calls (prompts, responses, token usage)
- ✓ Errors and exceptions
- ✓ Cross-sheet queries

#### Example Trace Data

```json
{
  "name": "excel_rag_llm_call",
  "inputs": {"prompt": "...context and query..."},
  "outputs": {"response": "...LLM answer..."},
  "metadata": {
    "model": "gpt-3.5-turbo",
    "token_usage": 1234,
    "execution_time_seconds": 2.5,
    "timestamp": "2024-10-06T14:30:00"
  }
}
```

---

### Database Configuration

```bash
# Path to Milvus database file
DB_PATH=./milvus_edelivery.db

# Path to Excel data file
EXCEL_FILE=eDelivery_AIeDelivery_Database_V1.xlsx
```

**Note:** Paths are relative to project root unless absolute path is provided.

---

### Model Configuration

```bash
# Embedding model (from HuggingFace)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Default LLM model
LLM_MODEL=mock  # Options: mock, gpt-3.5-turbo, gpt-4, claude-3-sonnet-20240229

# LLM parameters
LLM_TEMPERATURE=0.7      # 0.0 = deterministic, 2.0 = very creative
LLM_MAX_TOKENS=2000      # Maximum response length
```

---

### Query Configuration

```bash
# Number of sheets to retrieve
TOP_K_STRUCTURE=3

# Number of content rows to retrieve
TOP_K_CONTENT=5
```

**Tuning tips:**
- Increase for complex queries needing more context
- Decrease for faster queries with less token usage
- Cross-sheet queries may benefit from higher values

---

### Advanced Configuration

```bash
# Batch size for database insertion
BATCH_SIZE=1000

# Vector index type (IVF_FLAT or HNSW)
INDEX_TYPE=IVF_FLAT

# Similarity metric (COSINE, L2, IP)
METRIC_TYPE=COSINE

# IVF index parameters
NLIST=128    # Number of clusters
NPROBE=10    # Clusters to search
```

---

## Usage Examples

### Example 1: Using with OpenAI

```bash
# Set up .env
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_TRACING_V2=true

# Run query
python main.py query "What is the delivery status?" --llm gpt-3.5-turbo
```

### Example 2: Using with Claude

```bash
# Set up .env
ANTHROPIC_API_KEY=sk-ant-...
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_TRACING_V2=true

# Run query
python main.py query "What is the delivery status?" --llm claude-3-sonnet-20240229
```

### Example 3: Mock Mode (No API Keys)

```bash
# No API keys needed
LANGCHAIN_API_KEY=ls-...  # Optional
LANGCHAIN_TRACING_V2=true

# Run with mock LLM
python main.py query "test query" --llm mock
```

### Example 4: Programmatic Usage

```python
from src.config import print_config_summary
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer

# Check configuration
print_config_summary()

# Use query engine
engine = QueryEngine()
llm = LLMLayer(model_name="gpt-3.5-turbo")

results = engine.query("What is the delivery status?")
response = llm.generate_answer(results["context"], results["query"])

print(response["answer"])

# LangSmith will automatically trace this if configured!
```

---

## Checking Configuration Status

### Quick Check

```bash
python -c "from src.config import print_config_summary; print_config_summary()"
```

**Output:**
```
============================================================
EXCEL-RAG CONFIGURATION
============================================================
Database: ./milvus_edelivery.db
Excel file: eDelivery_AIeDelivery_Database_V1.xlsx
Embedding model: all-MiniLM-L6-v2
LLM model: gpt-3.5-turbo

API Keys:
  openai: ✓ Set
  anthropic: ✗ Not set
  langsmith: ✓ Set

LangSmith:
  Tracing enabled: True
  Project: excel-rag-system
============================================================
```

### Programmatic Check

```python
from src.config import get_api_key_status, is_langsmith_enabled

# Check API keys
status = get_api_key_status()
print(f"OpenAI: {status['openai']}")
print(f"Anthropic: {status['anthropic']}")
print(f"LangSmith: {status['langsmith']}")

# Check if tracing is enabled
if is_langsmith_enabled():
    print("✓ LangSmith tracing is active")
else:
    print("✗ LangSmith tracing is not configured")
```

---

## Troubleshooting

### API Key Not Working

**Problem:** "API key not set" error

**Solution:**
1. Check `.env` file exists: `ls -la .env`
2. Verify variable name is correct (no typos)
3. No quotes around values in .env
4. Restart Python session after changing .env

**Correct .env format:**
```bash
OPENAI_API_KEY=sk-abc123
```

**Incorrect:**
```bash
OPENAI_API_KEY="sk-abc123"  # No quotes!
OPENAI_API_KEY = sk-abc123  # No spaces!
```

### LangSmith Not Tracing

**Problem:** No traces appearing in LangSmith dashboard

**Solutions:**
1. Verify `LANGCHAIN_TRACING_V2=true` (not "True" or "1")
2. Check API key is valid
3. Ensure `langsmith` package is installed: `pip install langsmith`
4. Check for error messages in console
5. Verify project name in dashboard matches `.env`

### Environment Variables Not Loading

**Problem:** Using defaults instead of .env values

**Solutions:**
1. Ensure `.env` file is in project root (same directory as `main.py`)
2. Install python-dotenv: `pip install python-dotenv`
3. Check for syntax errors in `.env`
4. Restart Python/terminal session

---

## Security Best Practices

### 1. Never Commit .env

The `.gitignore` file already excludes `.env`:
```
.env  # ← Your secrets are safe
.env.example  # ← This is committed (no secrets)
```

### 2. Use Different Keys Per Environment

```bash
# Development
OPENAI_API_KEY=sk-dev-key-here

# Production
OPENAI_API_KEY=sk-prod-key-here
```

### 3. Rotate Keys Regularly

- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- LangSmith: https://smith.langchain.com/settings

### 4. Use Read-Only Keys When Possible

Some services offer read-only or restricted API keys. Use them for applications that only need to query, not modify.

### 5. Monitor Usage

- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/settings/billing
- LangSmith: https://smith.langchain.com/settings/billing

---

## Cost Optimization

### Token Usage

LangSmith tracks token usage per query:
- View in dashboard under "Traces"
- Identify expensive queries
- Optimize context size

### Reduce Costs

```bash
# Use fewer results
TOP_K_STRUCTURE=2  # Instead of 5
TOP_K_CONTENT=3    # Instead of 10

# Use cheaper models
LLM_MODEL=gpt-3.5-turbo  # Instead of gpt-4

# Use mock for development
LLM_MODEL=mock
```

---

## Complete .env Example

```bash
# ============================================================================
# LLM API Keys
# ============================================================================
OPENAI_API_KEY=sk-proj-abc123xyz789
ANTHROPIC_API_KEY=sk-ant-def456uvw012

# ============================================================================
# LangSmith Configuration
# ============================================================================
LANGCHAIN_API_KEY=ls-ghi789rst345
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=excel-rag-production
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# ============================================================================
# Database Configuration
# ============================================================================
DB_PATH=./milvus_edelivery.db
EXCEL_FILE=eDelivery_AIeDelivery_Database_V1.xlsx

# ============================================================================
# Model Configuration
# ============================================================================
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# ============================================================================
# Query Configuration
# ============================================================================
TOP_K_STRUCTURE=3
TOP_K_CONTENT=5

# ============================================================================
# Advanced Configuration
# ============================================================================
BATCH_SIZE=1000
INDEX_TYPE=IVF_FLAT
METRIC_TYPE=COSINE
NLIST=128
NPROBE=10
LOG_LEVEL=INFO
```

---

## Next Steps

1. **Copy .env.example:** `cp .env.example .env`
2. **Add your API keys** to `.env`
3. **Verify configuration:** `python -c "from src.config import print_config_summary; print_config_summary()"`
4. **Run a test query:** `python main.py query "test" --llm mock`
5. **Check LangSmith dashboard** for traces
6. **Build your database:** `python main.py build --excel your_file.xlsx`
7. **Start querying!** `python main.py interactive`

For more help, see:
- `README.md` - General documentation
- `QUICKSTART.md` - Quick start guide
- `.env.example` - All available variables
