# Cross-Sheet Query Guide

## Can the system handle cross-sheet queries?

**Yes!** The Excel-RAG system can retrieve and combine information from multiple sheets, but it works differently than SQL JOINs.

## How It Works

### Standard Query (Semantic Cross-Sheet Retrieval)

```python
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer

engine = QueryEngine()
llm = LLMLayer()

# Query mentions both "serial number" and "cost"
query = "What is the serial number and cost for product xyz?"

# Dual-vector retrieval
results = engine.query(query)

# Structure DB finds: ["Products", "Pricing", "Inventory"]
# Content DB searches ALL 3 sheets with OR filter
# Returns top-5 results (mixed from all sheets)

response = llm.generate_answer(results["context"], query)
print(response["answer"])
```

**Output example:**
```
Retrieved structure:
  • Products (score: 0.85)
  • Pricing (score: 0.82)

Retrieved content:
  1. [Products] Product xyz, Serial: 12345, Category: Electronics (score: 0.91)
  2. [Pricing] Product xyz, Cost: $99.99, Discount: 10% (score: 0.88)

Answer: Product xyz has serial number 12345 and costs $99.99
```

### Enhanced Cross-Sheet Query

For better control over multi-sheet retrieval:

```python
from src.cross_sheet_query import CrossSheetQueryEngine

engine = CrossSheetQueryEngine()

# Query with entity focus
results = engine.query_with_joins(
    "What is the serial number and cost for product xyz?",
    entity_identifier="product xyz",  # Boosts results containing this
    top_k_structure=5,               # Check 5 sheets
    top_k_per_sheet=3                # Get 3 results FROM EACH sheet
)

# Per-sheet breakdown
for sheet, sheet_results in results["per_sheet_results"].items():
    print(f"{sheet}:")
    for r in sheet_results:
        print(f"  - {r['text'][:100]}...")
```

## Comparison: Standard vs Enhanced

| Feature | Standard Query | Enhanced Cross-Sheet |
|---------|---------------|---------------------|
| **Sheets searched** | Multiple (top-k) | Multiple (top-k) |
| **Results distribution** | Global top-k (might be from 1 sheet) | top-k PER sheet (balanced) |
| **Entity boosting** | No | Yes (re-ranks by entity match) |
| **Sheet breakdown** | Combined | Separated by sheet |
| **Use case** | General queries | Entity-specific queries |

## Example Scenarios

### Scenario 1: Product Information Across Sheets

**Data:**
- Sheet "Products": columns [ProductID, Name, Serial, Category]
- Sheet "Pricing": columns [ProductID, Price, Currency, Discount]
- Sheet "Inventory": columns [ProductID, Stock, Location, Supplier]

**Query:** *"What is the price and stock level for product xyz?"*

**What happens:**

1. **Structure retrieval** identifies all 3 sheets (all contain "ProductID")
2. **Content retrieval** searches all 3 sheets for "product xyz"
3. **Results:**
   - From Products: "xyz, Serial: 12345, Category: Electronics"
   - From Pricing: "xyz, Price: $99.99, Currency: USD"
   - From Inventory: "xyz, Stock: 150, Location: Warehouse A"
4. **LLM synthesis:** "Product xyz is priced at $99.99 and has 150 units in stock"

**Limitation:** If ProductID is "XYZ-001" in one sheet and "xyz" in another, semantic similarity might catch it, but it's less reliable than SQL foreign keys.

### Scenario 2: Multi-Entity Comparison

**Query:** *"Compare the costs of products A, B, and C"*

```python
from src.cross_sheet_query import CrossSheetQueryEngine

engine = CrossSheetQueryEngine()

results = engine.query_with_multi_entity(
    "Compare the costs of products A, B, and C",
    entities=["product A", "product B", "product C"],
    top_k_structure=5,
    top_k_per_sheet=5
)

# Results organized by entity
for entity, entity_results in results["entity_results"].items():
    print(f"\n{entity}:")
    for r in entity_results:
        print(f"  [{r['sheet']}] {r['text'][:80]}...")
```

## Limitations vs SQL JOINs

| SQL JOIN | Excel-RAG System |
|----------|------------------|
| Foreign key relationships | Semantic similarity only |
| Exact matching | Fuzzy/semantic matching |
| All related rows | Top-k most similar rows |
| Deterministic | Probabilistic (embedding-based) |
| Fast (indexed) | Fast (vector indexed) |

### What Works Well

✓ **Natural language queries** spanning multiple sheets
✓ **Entity mentions** that appear in multiple sheets
✓ **Semantic relationships** (e.g., "cost" matches "price")
✓ **LLM can synthesize** information from multiple sources

### What Doesn't Work Well

✗ **Exact foreign key joins** (use SQL for this)
✗ **Complex aggregations** across sheets (e.g., "SUM all costs")
✗ **Guaranteed completeness** (top-k may miss relevant rows)
✗ **Entity name variations** (e.g., "XYZ" vs "xyz-001")

## Best Practices

### 1. Use Specific Entity Names

**Good:**
```python
query = "What is the cost for product ABC-12345?"
entity = "ABC-12345"  # Specific identifier
```

**Less effective:**
```python
query = "What is the cost?"  # Too vague
```

### 2. Increase top_k for Complex Queries

```python
# For queries needing multiple sheets
results = engine.query(
    "Show serial number, cost, and inventory for product xyz",
    top_k_structure=7,   # Check more sheets
    top_k_content=15     # Get more rows
)
```

### 3. Use Enhanced Engine for Entity Queries

```python
# Standard engine: good for general queries
engine = QueryEngine()

# Enhanced engine: better for specific entities
cross_engine = CrossSheetQueryEngine()
cross_engine.query_with_joins(query, entity_identifier="product xyz")
```

### 4. Verify Critical Information

For production use cases requiring exact joins:
1. Use RAG system for discovery
2. Validate with SQL queries on specific sheets
3. Or implement hybrid approach (RAG + SQL)

## Performance Implications

### Standard Query
- **Retrieval time:** ~500ms
- **Token usage:** 500-1500 tokens
- **Sheets searched:** 3 (default)
- **Total results:** 5 (default)

### Enhanced Cross-Sheet Query
- **Retrieval time:** ~800ms (more sheet-specific searches)
- **Token usage:** 800-2000 tokens (more context)
- **Sheets searched:** 5 (configurable)
- **Results per sheet:** 3 (balanced coverage)

## Code Examples

### Example 1: Simple Cross-Sheet Query

```python
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer

engine = QueryEngine()
llm = LLMLayer(model_name="gpt-3.5-turbo")

query = "What are the delivery date and cost for order 12345?"
results = engine.query(query, top_k_structure=5, top_k_content=10)
response = llm.generate_answer(results["context"], query)

print(response["answer"])
```

### Example 2: Entity-Focused Query

```python
from src.cross_sheet_query import CrossSheetQueryEngine
from src.llm_layer import LLMLayer

engine = CrossSheetQueryEngine()
llm = LLMLayer(model_name="gpt-3.5-turbo")

query = "What is the serial number, cost, and stock for product xyz?"
results = engine.query_with_joins(
    query,
    entity_identifier="product xyz",
    top_k_structure=5,
    top_k_per_sheet=3
)

response = llm.generate_answer(results["context"], query)

print("\n=== Per-Sheet Results ===")
for sheet, sheet_results in results["per_sheet_results"].items():
    print(f"{sheet}: {len(sheet_results)} results")

print("\n=== Answer ===")
print(response["answer"])
```

### Example 3: Multi-Entity Comparison

```python
from src.cross_sheet_query import CrossSheetQueryEngine
from src.llm_layer import LLMLayer

engine = CrossSheetQueryEngine()
llm = LLMLayer(model_name="gpt-3.5-turbo")

results = engine.query_with_multi_entity(
    "Compare the prices and stock levels of products A, B, and C",
    entities=["product A", "product B", "product C"]
)

response = llm.generate_answer(results["context"], results["query"])

print("\n=== Entity Coverage ===")
for entity, entity_results in results["entity_results"].items():
    print(f"{entity}: Found in {len(set(r['sheet'] for r in entity_results))} sheets")

print("\n=== Comparison ===")
print(response["answer"])
```

## When to Use Each Approach

### Use Standard Query When:
- General exploratory questions
- Don't know which sheets contain data
- Want fastest retrieval
- Token usage is a concern

### Use Enhanced Cross-Sheet When:
- Querying specific entities (products, orders, customers)
- Need balanced coverage across sheets
- Want per-sheet breakdown
- Complex multi-entity queries

### Use SQL/Pandas When:
- Need exact foreign key joins
- Require aggregations (SUM, AVG, GROUP BY)
- Must guarantee completeness
- Working with structured relational data

## Summary

**Yes, the system handles cross-sheet queries!**

✓ Retrieves from multiple sheets simultaneously
✓ LLM combines information across sheets
✓ Semantic matching works across different column names
✓ Enhanced engine provides better entity-focused retrieval

**But remember:** It's semantic retrieval, not SQL joins. Best for natural language queries where you want the LLM to "understand" and combine information, rather than exact relational operations.
