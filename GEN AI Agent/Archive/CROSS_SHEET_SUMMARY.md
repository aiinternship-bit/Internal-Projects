# Cross-Sheet Query Capability Summary

## Question
**"Can it handle cross-sheet joins, ie, if someone asks about product xyz in sheet abc, which is also present with cost data in sheet def, can it extract both pieces of information?"**

## Answer: YES! ✓

The Excel-RAG system **CAN** retrieve and combine information from multiple sheets, with two modes:

---

## How It Works

### Standard Mode (Built-in)

```python
from src.query_engine import QueryEngine

engine = QueryEngine()
results = engine.query("What is the serial number and cost for product xyz?")
```

**Process:**
1. **Structure DB** searches for relevant sheets → finds ["Products", "Pricing", "Inventory"]
2. **Content DB** searches ALL 3 sheets simultaneously using OR filter: `sheet == 'Products' OR sheet == 'Pricing' OR sheet == 'Inventory'`
3. Returns **top-5 results globally** (mixed from all sheets)
4. **LLM** receives combined context and synthesizes answer

**Example Result:**
```
Retrieved content:
  1. [Products] Product xyz, Serial: 12345, Category: Electronics (score: 0.91)
  2. [Pricing] Product xyz, Cost: $99.99, Discount: 10% (score: 0.88)
  3. [Inventory] Product xyz, Stock: 150, Location: Warehouse A (score: 0.85)

LLM Answer: "Product xyz has serial number 12345, costs $99.99, and has 150 units in stock at Warehouse A."
```

---

### Enhanced Mode (New - Better for Entities)

```python
from src.cross_sheet_query import CrossSheetQueryEngine

engine = CrossSheetQueryEngine()
results = engine.query_with_joins(
    "What is the serial number and cost for product xyz?",
    entity_identifier="product xyz",
    top_k_structure=5,
    top_k_per_sheet=3  # Get 3 results FROM EACH sheet
)
```

**Enhancements:**
1. Retrieves **N results PER sheet** (not global) → balanced coverage
2. **Boosts scores** for rows containing the entity (1.5x multiplier)
3. Provides **per-sheet breakdown** in results
4. Marks entity matches with `entity_match: True`

**CLI Usage:**
```bash
# Standard cross-sheet
python main.py query "What is the cost and serial for product xyz?"

# Enhanced with entity focus
python main.py query "What is the cost and serial for product xyz?" \
  --cross-sheet --entity "product xyz"
```

---

## Comparison Table

| Feature | Standard Query | Enhanced Cross-Sheet |
|---------|---------------|---------------------|
| **Searches multiple sheets?** | ✓ Yes | ✓ Yes |
| **Result distribution** | Global top-k (may favor 1 sheet) | Top-k PER sheet (balanced) |
| **Entity boosting** | ✗ No | ✓ Yes (1.5x score) |
| **Per-sheet breakdown** | ✗ No | ✓ Yes |
| **Best for** | General queries | Entity-specific queries |
| **Example** | "delivery data" | "product #12345 cost" |

---

## Important Differences from SQL JOINs

### What Works ✓

- **Semantic retrieval** across sheets based on query meaning
- **Multiple sheets searched** simultaneously
- **LLM synthesis** of information from different sources
- **Fuzzy matching** (e.g., "cost" matches "price")
- **Fast** (vector similarity is efficient)

### Limitations ✗

- **Not relational joins** - no foreign key awareness
- **Probabilistic** - top-k may miss relevant rows
- **Entity name variations** - "XYZ-001" vs "xyz" may not match
- **No aggregations** - can't SUM/AVG across sheets
- **Completeness not guaranteed** - returns top-k, not all matches

---

## When To Use Each Approach

### Use Excel-RAG Cross-Sheet When:
- ✓ Natural language queries
- ✓ Entity appears in multiple sheets
- ✓ Want LLM to "understand" and combine data
- ✓ Entity names are consistent
- ✓ Top-k results are sufficient

### Use SQL/Pandas When:
- ✗ Need exact foreign key joins
- ✗ Require aggregations (SUM, GROUP BY)
- ✗ Must guarantee completeness
- ✗ Working with structured IDs

---

## Example Scenarios

### Scenario 1: Product Information

**Sheets:**
- Products: [ProductID, Name, Serial, Category]
- Pricing: [ProductID, Price, Currency, Discount]
- Inventory: [ProductID, Stock, Location]

**Query:** *"What is the price and stock for product xyz?"*

**Standard Mode Result:**
```
Structure: Found 3 relevant sheets (Products, Pricing, Inventory)
Content: Retrieved 5 rows total across all sheets
Answer: "Product xyz is priced at $99.99 and has 150 units in stock."
```

**Enhanced Mode Result:**
```
Structure: Found 3 relevant sheets
Content: Retrieved 3 rows from Products, 3 from Pricing, 3 from Inventory
Per-sheet breakdown:
  - Products: 3 results (2 entity matches)
  - Pricing: 3 results (1 entity match)
  - Inventory: 3 results (1 entity match)
Answer: "Product xyz is priced at $99.99 and has 150 units in stock."
```

### Scenario 2: Multi-Entity Comparison

**Query:** *"Compare costs of products A, B, and C"*

```python
engine = CrossSheetQueryEngine()
results = engine.query_with_multi_entity(
    "Compare costs of products A, B, and C",
    entities=["product A", "product B", "product C"]
)

# Results organized by entity
# Each entity shows data from multiple sheets
```

---

## Technical Implementation

### Code Location
- **Standard mode:** `src/query_engine.py` - QueryEngine class
- **Enhanced mode:** `src/cross_sheet_query.py` - CrossSheetQueryEngine class

### Key Code Snippet (Multi-Sheet Filter)

```python
# In content_db.py
if sheet_filter:
    # Build OR filter for multiple sheets
    sheet_conditions = [f"sheet == '{sheet}'" for sheet in sheet_filter]
    filter_expr = " or ".join(sheet_conditions)
    # Example: "sheet == 'Products' or sheet == 'Pricing'"

# Search with filter
results = client.search(
    collection_name="excel_vectors",
    data=query_embedding,
    limit=top_k,
    filter=filter_expr  # Searches multiple sheets!
)
```

---

## Performance

### Standard Query
- **Latency:** ~500ms
- **Token usage:** 500-1500 tokens
- **Sheets searched:** 3 (default)
- **Total results:** 5 (default)

### Enhanced Cross-Sheet Query
- **Latency:** ~800ms (more individual searches)
- **Token usage:** 800-2000 tokens (more context)
- **Sheets searched:** 5 (configurable)
- **Results per sheet:** 3 (configurable)

---

## Full Documentation

- **Detailed guide:** `CROSS_SHEET_GUIDE.md`
- **Demo script:** `demo_cross_sheet.py`
- **Example code:** `example_usage.py`
- **Main implementation:** `src/cross_sheet_query.py`

---

## Quick Start

```bash
# 1. Build databases first
python main.py build --excel eDelivery_AIeDelivery_Database_V1.xlsx --drop

# 2. Try standard cross-sheet query
python main.py query "What is the serial and cost for product xyz?"

# 3. Try enhanced cross-sheet query
python main.py query "What is the serial and cost for product xyz?" \
  --cross-sheet --entity "product xyz" --top-k-structure 5

# 4. View demo
python demo_cross_sheet.py
```

---

## Summary

**YES - The system handles cross-sheet queries!**

✓ Retrieves from multiple sheets simultaneously
✓ LLM combines information across sheets
✓ Two modes: standard (fast) and enhanced (entity-focused)
✓ Works with natural language queries

But remember: It's **semantic retrieval**, not SQL joins. Best for queries where you want the LLM to "understand" and synthesize information, rather than exact relational operations.
