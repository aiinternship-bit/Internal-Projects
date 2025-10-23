# LLM-Enhanced RAG System

The printer recommendation system now includes **Claude-powered natural language responses** for better, more conversational recommendations.

## What's Changed

### Before (Basic RAG)
```
Model: ZD220
Relevance Score: 87.50%
Category: desktop
Key Specifications:
  - Resolution: 203 DPI
  - Speed: 4.0 inches/second
```

### After (LLM-Enhanced RAG)
```
AI RECOMMENDATION
================================================================================

Based on your requirements for a fast desktop printer for retail, I recommend
the ZD220. Here's why it's a great fit:

The ZD220 is specifically designed for retail environments where reliability
and ease of use are crucial. With its 4 inches per second print speed, it
handles your labeling needs efficiently without creating bottlenecks at the
point of sale...

[Full conversational response continues]

================================================================================
DETAILED BREAKDOWN
================================================================================
[Technical specifications follow]
```

## Setup

### 1. Install Updated Dependencies

```bash
pip install -r requirements.txt
```

This now includes `anthropic>=0.40.0` for Claude API access.

### 2. Set API Key

Set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or pass it directly:

```bash
python src/printer_rag.py "your query" --api-key your-api-key-here
```

### 3. Use the Enhanced System

The LLM enhancement is **enabled by default**. Just query normally:

```bash
python src/printer_rag.py "I need a fast desktop printer for retail with USB"
```

## Usage Examples

### Basic Query with LLM Enhancement

```bash
python src/printer_rag.py "I need a printer for healthcare labels"
```

Output includes:
1. **AI Recommendation** - Natural language explanation from Claude
2. **Detailed Breakdown** - Technical specs and matching scores

### Disable LLM (Use Only Vector Search)

```bash
python src/printer_rag.py "your query" --no-llm
```

This falls back to basic vector search output (faster, no API costs).

### Interactive Mode

```bash
python src/printer_rag.py --interactive
```

Each query gets an LLM-enhanced response with context from the vector DB.

### Programmatic Usage

```python
from src.printer_rag import PrinterRAG

# Initialize with LLM enabled (default)
rag = PrinterRAG(use_llm=True)

# Or explicitly disable
rag = PrinterRAG(use_llm=False)

# Get recommendation
result = rag.recommend_printer("fast printer for manufacturing")

# Access LLM response
if 'llm_response' in result:
    print(result['llm_response'])

# Access raw recommendations
for rec in result['recommendations']:
    print(rec['model'], rec['relevance_score'])
```

## How It Works

### 1. Vector Search (Hybrid)
```
User Query → Embeddings → ChromaDB → Top Results
             ↓
      Metadata Filters
```

### 2. Context Building
```
Top 3 Printers → Extract:
  - Model & Category
  - Key Specs
  - Relevance Scores
  - Matching Chunks (content)
```

### 3. LLM Generation
```
Context + User Query → Claude API → Natural Language Response
```

### Prompt Structure

The system sends Claude:

```
User Question: [original query]

Available Printer Information:
--- Printer 1: ZD220 ---
Category: desktop
Relevance Score: 87.50%
Key Specifications:
  resolution_dpi: 203
  print_speed_ips: 4.0
  connectivity: USB

Detailed Information:
Overview:
[chunk content...]

Specifications:
[chunk content...]

Instructions:
1. Provide clear, conversational recommendation
2. Explain WHY each printer matches their needs
3. Highlight relevant specs and features
4. Be concise but informative
5. Use friendly, professional tone
```

## Benefits

### LLM-Enhanced Response
- **Natural language** - Conversational, easy to understand
- **Contextual reasoning** - Explains WHY a printer is recommended
- **Comparison** - Automatically compares multiple options
- **Tailored** - Addresses specific user requirements
- **Professional** - Consistent tone and quality

### Raw Vector Search (--no-llm)
- **Faster** - No API latency (~200ms total)
- **Free** - No API costs
- **Structured** - Consistent format
- **Detailed** - All technical specs

## Configuration Options

### Constructor Parameters

```python
PrinterRAG(
    db_path="./chroma_db",              # Vector DB location
    collection_name="printer_specs",     # Collection name
    use_llm=True,                        # Enable LLM enhancement
    anthropic_api_key=None               # API key (or use env var)
)
```

### Command Line Flags

```bash
--db-path PATH         # ChromaDB directory (default: ./chroma_db)
--collection NAME      # Collection name (default: printer_specs)
--n-results N          # Number of recommendations (default: 3)
--no-llm               # Disable LLM enhancement
--api-key KEY          # Anthropic API key
--interactive          # Interactive mode
--compare MODEL1 MODEL2  # Compare specific models
```

## Cost Considerations

### LLM-Enhanced Mode
- **Model**: Claude Sonnet 4
- **Tokens per query**: ~1,500-2,500 tokens
  - Input: ~1,000-1,500 tokens (context)
  - Output: ~500-1,000 tokens (response)
- **Cost**: ~$0.01-0.02 per query
- **Latency**: +500-1000ms

### Vector-Only Mode (--no-llm)
- **Cost**: $0 (fully local)
- **Latency**: ~200ms

## Example Sessions

### Manufacturing Use Case

**Query:**
```bash
python src/printer_rag.py "I need a printer for manufacturing floor that can handle high volumes"
```

**AI Response:**
```
For high-volume manufacturing floor applications, I recommend the ZD420.
This printer is specifically designed for demanding industrial environments
with features that ensure reliability and performance:

1. Robust Construction: The ZD420 features a dual-wall frame construction
   that can withstand the harsh conditions typical of manufacturing floors.

2. High-Speed Performance: With print speeds up to 6 inches per second,
   it keeps pace with high-volume labeling requirements without creating
   bottlenecks in your production line.

3. Connectivity Options: Multiple connectivity options including USB and
   Ethernet ensure easy integration into your existing manufacturing
   systems...
```

### Healthcare Use Case

**Query:**
```bash
python src/printer_rag.py "hospital wristband printer with reliable operation"
```

**AI Response:**
```
For hospital wristband printing, the ZD220 is an excellent choice. Here's
why it's ideal for healthcare environments:

1. Medical-Grade Reliability: Built with Zebra's quality standards,
   ensuring consistent operation in critical healthcare settings.

2. Wristband Support: Specifically supports wristband media, essential
   for patient identification and tracking.

3. Easy Operation: Single-button operation and LED status indicator
   make it simple for busy healthcare staff to use...
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

Set your API key:
```bash
export ANTHROPIC_API_KEY='your-key'
```

Or pass directly:
```bash
python src/printer_rag.py "query" --api-key your-key
```

### "Falling back to basic responses"

This means the API key wasn't found. The system automatically falls back to
vector-only mode. Set the API key to enable LLM enhancement.

### Slow responses

LLM calls add 500-1000ms latency. Use `--no-llm` for faster responses:
```bash
python src/printer_rag.py "query" --no-llm
```

### High API costs

Each query costs ~$0.01-0.02. For high-volume usage:
- Use `--no-llm` for simple queries
- Cache common queries
- Increase `n_results` to get more recommendations per query

## Architecture

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Vector Search    │ ← ChromaDB + Embeddings
│ (Hybrid)         │   (Local, Free, Fast)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Context Building │ ← Top 3 printers + specs + chunks
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Claude API       │ ← Natural language generation
│ (Optional)       │   (Costs ~$0.01/query)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Final Response   │
│ - LLM Response   │
│ - Raw Data       │
└──────────────────┘
```

## Best Practices

### When to Use LLM Enhancement

✅ **Use LLM when:**
- Customer-facing applications
- Complex requirements
- Need explanations and reasoning
- Quality > speed
- User experience is critical

❌ **Skip LLM when:**
- Internal tools
- High-volume queries
- Cost-sensitive applications
- Speed > quality
- Technical users who prefer raw data

### Optimizing Performance

**Reduce latency:**
```python
# Use fewer results
result = rag.recommend_printer(query, n_results=1)
```

**Reduce costs:**
```python
# Disable LLM for simple queries
if is_simple_query(query):
    rag.use_llm = False
```

**Cache responses:**
```python
import functools

@functools.lru_cache(maxsize=100)
def cached_recommend(query):
    return rag.recommend_printer(query)
```

## Future Enhancements

Potential improvements:

1. **Streaming responses** - Stream Claude's response in real-time
2. **Custom prompts** - Allow users to customize the LLM prompt
3. **Multi-turn conversations** - Support follow-up questions
4. **Response caching** - Cache common queries
5. **Fallback models** - Use cheaper models for simple queries
6. **A/B testing** - Compare LLM vs non-LLM responses

## Comparison: LLM vs Non-LLM

| Feature | With LLM | Without LLM |
|---------|----------|-------------|
| Response quality | Natural, conversational | Technical, structured |
| Latency | ~700-1200ms | ~200ms |
| Cost per query | ~$0.01-0.02 | $0 |
| Explanations | Detailed reasoning | None |
| Comparison | Automatic | Manual |
| User experience | Excellent | Good |
| API dependency | Yes | No |
| Offline support | No | Yes |

## Summary

The LLM-enhanced RAG system combines:
- **Fast vector search** (local, free)
- **Precise filtering** (metadata)
- **Natural language generation** (Claude)

Result: **Best of both worlds** - technical accuracy + conversational quality.
