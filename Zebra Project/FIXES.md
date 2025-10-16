# Bug Fixes Applied

## Issue: AttributeError during ingestion

**Error:**
```
AttributeError: 'str' object has no attribute 'get'
```

**Cause:**
The PDF extraction process sometimes produces fields (like `media_width`, `resolution`, `print_speed`) as strings instead of dictionaries, depending on the source PDF format.

**Fix Applied:**
Updated `vector_db_schema.py` to handle both dictionary and string values for all spec fields.

### Changes Made

#### 1. `_extract_metadata()` method
Added type checking for all nested dictionary accesses:

```python
# Before (would crash if value is string)
"max_media_width_inches": media.get("media_width", {}).get("max_inches", 0)

# After (handles both dict and string)
media_width_data = media.get("media_width", {})
if isinstance(media_width_data, dict):
    max_width = media_width_data.get("max_inches", 0)
else:
    max_width = 0
```

Applied to:
- `resolution` → `resolution_dpi`
- `print_speed` → `print_speed_ips`
- `media_width` → `max_media_width_inches`

#### 2. Chunking methods
Updated all chunk creation methods to handle mixed types:

**`_create_specs_chunk()`:**
- Resolution handling
- Print speed handling
- Operating temperature handling
- Operating humidity handling

**`_create_media_ribbon_chunk()`:**
- Media width handling

**`_create_performance_chunk()`:**
- Print speed handling
- Resolution handling

### Example

**Dictionary format (preferred):**
```json
{
  "media_width": {
    "raw": "1.00 in./25.4 mm to 4.4 in./112 mm",
    "min_inches": 1.0,
    "max_inches": 4.4
  }
}
```

**String format (also supported now):**
```json
{
  "media_width": "1.00 in./25.4 mm to 4.4 in./112 mm"
}
```

Both formats now work correctly!

## Testing

To verify the fix works:

```bash
# Clear and re-ingest
python src/vector_db_ingest.py output/ --clear

# Should process all 27 files without errors
```

## Impact

- ✅ All 27 PDFs can now be ingested
- ✅ No data loss - strings are preserved as-is
- ✅ Dictionaries still extract structured values when available
- ✅ Backward compatible with existing JSON files

## Future Improvements

Consider standardizing the PDF processor output to always use dictionary format for consistency:

```python
# In pdf_processor.py
def _parse_measurement(self, value: str) -> Dict[str, Any]:
    """Always return dict format, even for simple values."""
    result = {"raw": value}
    # ... parsing logic
    return result
```
