# Excel-RAG System

Vector-based retrieval and LLM Q&A over Excel data using dual-vector search architecture.

## Overview

This system enables natural language queries over large Excel datasets by:
1. **Dual-Vector Indexing**: Separate indexes for structure (sheets/columns) and content (rows)
2. **Two-Stage Retrieval**: Structure search → Content search (filtered by relevant sheets)
3. **Cross-Sheet Queries**: Retrieve and combine data from multiple sheets simultaneously
4. **LLM Integration**: Retrieved context → LLM → Natural language answers

### Key Features

✓ **Cross-Sheet Retrieval** - Query data spanning multiple sheets (e.g., "product xyz serial and cost")
✓ **Dual-Vector Architecture** - Efficient structure + content indexing
✓ **Multi-LLM Support** - Ollama (local), OpenAI, Anthropic, or mock mode
✓ **API Key Validation** - Automatic verification of all API keys
✓ **LangSmith Integration** - Complete tracing and diagnostics
✓ **Production Ready** - Handles 2M+ rows, comprehensive testing

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (copy and edit .env file)
cp .env.example .env
nano .env  # Add your API keys

# Verify configuration
python check_env.py
```

### 2. Build Vector Databases

```bash
# Build from Excel file (takes ~2-3 hours for large files)
python main.py build --excel eDelivery_AIeDelivery_Database_V1.xlsx --drop
```

### 3. Run Tests

```bash
# Verify everything works
python main.py test
```

### 4. Query the Data

```bash
# Single query
python main.py query "What is the digital delivery system?"

# Interactive mode
python main.py interactive
```

## Usage

### Build Databases

```bash
python main.py build [OPTIONS]

Options:
  --excel PATH    Path to Excel file (default: eDelivery_AIeDelivery_Database_V1.xlsx)
  --db PATH       Path to Milvus database (default: ./milvus_edelivery.db)
  --drop          Drop existing collections before building
```

### Query Data

```bash
python main.py query "YOUR QUESTION" [OPTIONS]

Options:
  --llm MODEL            LLM model (default: mock, options: gpt-3.5-turbo, gpt-4, claude-3-sonnet)
  --top-k-structure N    Number of sheets to retrieve (default: 3)
  --top-k-content N      Number of rows to retrieve (default: 5)
  --entity TEXT          Entity identifier for cross-sheet queries (e.g., 'product xyz')
  --cross-sheet          Use enhanced cross-sheet query engine (per-sheet results)
  --db PATH             Database path

Examples:
  # Standard query
  python main.py query "What is the delivery status?"

  # Cross-sheet query with entity focus
  python main.py query "What is the serial and cost for product xyz?" \
    --cross-sheet --entity "product xyz"
```

### Interactive Mode

```bash
python main.py interactive [OPTIONS]

Options:
  --llm MODEL    LLM model to use
  --db PATH      Database path
```

### Run Tests

```bash
python main.py test [OPTIONS]

Options:
  --db PATH      Database path
  --query TEXT   Sample query for testing
```

## Architecture

### Components

1. **Structure Vector DB** (`src/structure_db.py`)
   - Encodes Excel schema (sheets, columns)
   - Fast lookup for relevant sheets
   - Small index size

2. **Content Vector DB** (`src/content_db.py`)
   - Encodes row-level content
   - Large index with full data
   - Supports sheet-based filtering

3. **Query Engine** (`src/query_engine.py`)
   - Orchestrates dual-vector retrieval
   - Combines structure + content results
   - Builds optimized context for LLM

4. **LLM Layer** (`src/llm_layer.py`)
   - Supports multiple backends (OpenAI, Anthropic, local)
   - Mock mode for testing without API
   - Tracks token usage

5. **Testing Module** (`src/testing.py`)
   - 5-stage validation suite
   - End-to-end pipeline testing
   - Performance metrics

### Data Flow

```
User Query
    ↓
[Query Engine]
    ├─> [Structure DB] → Identify relevant sheets
    └─> [Content DB filtered by sheets] → Retrieve rows
    ↓
[Build Context]
    ↓
[LLM Layer]
    ↓
Natural Language Answer
```

## Configuration

Edit `src/config.py` to customize:

```python
# Database paths
DB_PATH = "./milvus_edelivery.db"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions

# Retrieval parameters
TOP_K_STRUCTURE = 3  # Sheets to retrieve
TOP_K_CONTENT = 5    # Rows to retrieve

# LLM settings
LLM_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2000
```

## Using Real LLMs

### OpenAI

```bash
# Install
pip install openai

# Set API key
export OPENAI_API_KEY="your-key"

# Query with GPT
python main.py query "Your question" --llm gpt-3.5-turbo
```

### Anthropic Claude

```bash
# Install
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Query with Claude
python main.py query "Your question" --llm claude-3-sonnet-20240229
```

## Project Structure

```
eDelivery/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── structure_db.py     # Structure vector database
│   ├── content_db.py       # Content vector database
│   ├── query_engine.py     # Dual-vector retrieval
│   ├── llm_layer.py        # LLM integration
│   └── testing.py          # Test suite
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
├── CLAUDE.md              # Development guide
├── Implementation_plan.md  # Detailed design
└── milvus_edelivery.db    # Vector database (created on build)
```

## Performance

- **Database size**: ~4GB for 2M rows (384-dim vectors)
- **Build time**: ~2-3 hours for full dataset
- **Query latency**: <1 second for retrieval
- **Token usage**: ~500-1500 tokens per query (vs 10K+ without RAG)

## Testing

The test suite validates 5 stages:

1. **Connectivity**: DB collections exist
2. **Embedding**: Vector dimensions correct
3. **Retrieval**: Structure + content search working
4. **LLM**: Answer generation functional
5. **End-to-End**: Complete pipeline successful

```bash
python main.py test
```

## Cross-Sheet Queries

The system supports queries spanning multiple sheets! See `CROSS_SHEET_GUIDE.md` for details.

**Example:** "What is the serial number and cost for product xyz?"
- Searches "Products" sheet for serial number
- Searches "Pricing" sheet for cost
- LLM combines both into a single answer

```bash
# Standard cross-sheet (fast)
python main.py query "What is the serial and cost for product xyz?"

# Enhanced cross-sheet (better entity coverage)
python main.py query "What is the serial and cost for product xyz?" \
  --cross-sheet --entity "product xyz"
```

See also: `CROSS_SHEET_SUMMARY.md` and `demo_cross_sheet.py`
