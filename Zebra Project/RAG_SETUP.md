# RAG-Based Printer Recommendation System

A complete RAG (Retrieval Augmented Generation) system for recommending Zebra printers based on natural language requirements.

## System Architecture

```
┌─────────────┐
│ JSON Files  │
│ (27 specs)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Vector DB       │ ← Chunking strategy (8 chunks per printer)
│ Schema          │   - overview, specs, features, use_cases
│                 │   - media_ribbon, performance, etc.
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Ingestion       │ ← sentence-transformers (all-MiniLM-L6-v2)
│ (ChromaDB)      │   - 384-dimensional embeddings
│                 │   - Local, no API costs
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ RAG Query       │ ← Hybrid search:
│ System          │   - Semantic similarity
│                 │   - Metadata filtering
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Recommendations │
└─────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pdfplumber` - PDF extraction
- `chromadb` - Vector database
- `sentence-transformers` - Local embeddings (no API costs!)

### 2. Process PDFs to JSON (if not done already)

```bash
python src/pdf_processor.py pdfs/
```

This creates JSON files in `output/` directory.

### 3. Ingest into Vector Database

```bash
python src/vector_db_ingest.py output/
```

This will:
- Create a ChromaDB database in `./chroma_db`
- Process each JSON file into 6-8 semantic chunks
- Generate embeddings for each chunk
- Store with metadata for filtering

Expected output:
```
Found 27 JSON files to ingest

Processing: output/zd220-spec-sheet-en-us.json
  Inserted 6 chunks for model: ZD220

Processing: output/zc300-spec-sheet-en-us.json
  Inserted 6 chunks for model: ZC300

...

================================================================================
Ingestion Complete
================================================================================
Files processed: 27/27
Total chunks inserted: 162
Total documents in DB: 162
================================================================================
```

### 4. Test the System

```bash
python src/vector_db_ingest.py output/ --test-query "fast desktop printer for retail"
```

## Usage

### Command-Line Query

```bash
python src/printer_rag.py "I need a desktop printer for retail with USB connectivity"
```

Output:
```
================================================================================
RECOMMENDATIONS
================================================================================

1. Model: ZD220
Relevance Score: 87.50%
Category: desktop

Key Specifications:
  - Resolution: 203 DPI
  - Speed: 4.0 inches/second
  - Connectivity: USB

Matching Sections (3):
  - Overview (score: 92%)
  - Features (score: 85%)
  - Use Cases (score: 84%)

--------------------------------------------------------------------------------
```

### Interactive Mode

```bash
python src/printer_rag.py --interactive
```

Example session:
```
Interactive Printer Recommendation System
================================================================================
Enter your requirements (or 'quit' to exit)
Example: 'I need a desktop printer for healthcare that supports USB'
================================================================================

Your requirements: I need a fast printer for manufacturing labels

Analyzing requirements: 'I need a fast printer for manufacturing labels'
Detected filters: {'category': 'desktop'}

================================================================================
RECOMMENDATIONS
================================================================================

1. Model: ZD220
...

Your requirements: I need a mobile printer with Bluetooth

Analyzing requirements: 'I need a mobile printer with Bluetooth'
Detected filters: {'category': 'mobile', 'has_bluetooth': True}

================================================================================
RECOMMENDATIONS
================================================================================

1. Model: [Mobile printer models with Bluetooth]
...
```

### Compare Specific Models

```bash
python src/printer_rag.py --compare ZD220 ZC300 ZT411
```

## How It Works

### 1. Chunking Strategy

Each printer is split into semantic chunks:

**Chunk Types:**
- `overview` - Product description, tagline, key selling points
- `specifications` - Technical specs (resolution, speed, memory)
- `features` - Standard and optional features
- `use_cases` - Industries and applications
- `media_ribbon` - Media and ribbon specifications
- `performance` - Speed and quality metrics

**Why chunking?**
- Better semantic relevance (e.g., "fast printing" matches "performance" chunk)
- More granular retrieval
- Avoids context dilution

### 2. Metadata Filtering

Filters are extracted automatically from natural language:

| Query Phrase | Detected Filter |
|--------------|----------------|
| "desktop printer" | `category: desktop` |
| "USB connectivity" | `has_usb: True` |
| "energy efficient" | `energy_star: True` |
| "WiFi" | `has_wifi: True` |
| "industrial" | `category: industrial` |

### 3. Hybrid Search

1. **Semantic Search**: Embed query and find similar chunks
2. **Metadata Filtering**: Apply structured filters
3. **Deduplication**: Group chunks by printer model
4. **Ranking**: Sort by relevance score

### 4. Result Aggregation

For each printer:
- Combine all matching chunks
- Extract key specs from metadata
- Calculate aggregate relevance score
- Generate explanation

## Advanced Usage

### Custom Filters

```python
from src.printer_rag import PrinterRAG

rag = PrinterRAG()

# Query with explicit filters
result = rag.recommend_printer(
    requirements="I need a printer for labels",
    filters={
        "has_usb": True,
        "energy_star": True,
        "category": "desktop"
    },
    n_results=5
)
```

### Programmatic Access

```python
from src.printer_rag import PrinterRAG

rag = PrinterRAG()

# Get recommendations
result = rag.recommend_printer("fast printer for retail", n_results=3)

for rec in result['recommendations']:
    print(f"Model: {rec['model']}")
    print(f"Score: {rec['relevance_score']:.2%}")
    print(f"Specs: {rec['key_specs']}")
    print()
```

## Vector Database Details

### ChromaDB Collection

- **Name**: `printer_specs`
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Distance Metric**: Cosine similarity
- **Storage**: Local persistent storage in `./chroma_db`

### Metadata Schema

Each document includes:

```python
{
    "model": "ZD220",
    "category": "desktop",
    "chunk_type": "overview",
    "resolution_dpi": 203,
    "print_speed_ips": 4.0,
    "has_usb": True,
    "has_ethernet": False,
    "has_wifi": False,
    "has_bluetooth": False,
    "energy_star": True,
    "source_file": "zd220-spec-sheet-en-us.json",
    "extraction_date": "2025-10-16T13:30:15.017322"
}
```

### Reingest Data

To clear and reingest:

```bash
python src/vector_db_ingest.py output/ --clear
```

### View Stats

```bash
python src/vector_db_ingest.py output/ --stats
```

## Example Queries

### Simple Queries

```bash
# By category
python src/printer_rag.py "desktop printer"

# By use case
python src/printer_rag.py "printer for healthcare labels"

# By feature
python src/printer_rag.py "fast printing with high resolution"

# By connectivity
python src/printer_rag.py "wireless printer with bluetooth"
```

### Complex Queries

```bash
# Multiple requirements
python src/printer_rag.py "I need a desktop printer for manufacturing that prints fast, supports USB and Ethernet, and is energy efficient"

# Specific applications
python src/printer_rag.py "What printer should I use for printing wristbands in a hospital?"

# Performance focused
python src/printer_rag.py "Which printer has the highest print speed for labels?"
```

## Performance

- **Embedding time**: ~50ms per query (local, no API)
- **Search time**: ~100ms for 200 documents
- **Total query time**: <200ms end-to-end
- **Cost**: $0 (fully local)

## Troubleshooting

### "Collection not found"

Run ingestion first:
```bash
python src/vector_db_ingest.py output/
```

### "No matching printers found"

- Try broader requirements
- Check if filters are too restrictive
- Verify data was ingested correctly:
  ```bash
  python src/vector_db_ingest.py output/ --stats
  ```

### Low relevance scores

- Chunks might not contain relevant information
- Try rephrasing query
- Use interactive mode to experiment

## Future Enhancements

Potential improvements:

1. **LLM Integration**: Add OpenAI/Anthropic for natural language responses
2. **Advanced Filtering**: Price ranges, dimensions, weight
3. **Comparison Mode**: Side-by-side feature comparison
4. **Query Expansion**: Automatic synonym expansion
5. **Feedback Loop**: Learn from user preferences
6. **Multi-language**: Support non-English queries

## Architecture Decisions

### Why ChromaDB?

- Easy to use
- Built-in embedding support
- Persistent local storage
- No cloud dependencies
- Active development

### Why sentence-transformers?

- Local inference (no API costs)
- Fast (< 100ms per query)
- Good semantic understanding
- Small model size (~80MB)

### Why Chunking?

- Better semantic matching
- Reduces noise
- Enables chunk-type filtering
- Improves ranking accuracy

## Files Structure

```
src/
├── vector_db_schema.py      # Schema and chunking logic
├── vector_db_ingest.py      # Ingestion script
├── printer_rag.py           # RAG query system
├── pdf_processor.py         # PDF extraction
└── validator.py             # JSON validation

chroma_db/                   # Vector database storage
output/                      # Processed JSON files
pdfs/                        # Source PDF files
```
