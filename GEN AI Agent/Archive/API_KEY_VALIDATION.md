# API Key Validation

The Excel-RAG system now includes **automatic API key validation** to ensure your configuration is correct before querying.

## What Gets Validated

### Ollama
- **Check:** HTTP request to `/api/tags` endpoint
- **Validates:** Server is running and accessible
- **Status:** `✓ Configured` or `✗ Not configured`

### OpenAI
- **Check:** GET request to `/v1/models` endpoint
- **Validates:** API key is valid and not revoked
- **Status:**
  - `✓ Valid` - Key works
  - `⚠ Set but invalid` - Key present but doesn't work
  - `✗ Not set` - No key configured

### Anthropic
- **Check:** Minimal POST to `/v1/messages` endpoint
- **Validates:** API key is valid and not revoked
- **Status:**
  - `✓ Valid` - Key works
  - `⚠ Set but invalid` - Key present but doesn't work
  - `✗ Not set` - No key configured

### LangSmith
- **Check:** Key presence only (no validation)
- **Status:** `✓ Set` or `✗ Not set`

---

## How It Works

### Automatic Validation

When you run `check_env.py`, the system automatically validates all configured API keys:

```bash
$ python check_env.py

============================================================
API KEY CHECK (with validation)
============================================================
ℹ  Checking API key validity (may take a few seconds)...

Ollama       ✗ Not configured
Openai       ✓ Valid
Anthropic    ✓ Valid
Langsmith    ✓ Set
```

### Programmatic Access

```python
from src.config import (
    get_api_key_status,
    is_ollama_configured,
    is_openai_key_valid,
    is_anthropic_key_valid
)

# Get all statuses
status = get_api_key_status()
print(status)
# {'ollama': '✗ Not configured', 'openai': '✓ Valid', ...}

# Check individual services
if is_ollama_configured():
    print("Ollama is ready!")

if is_openai_key_valid():
    print("OpenAI key is valid!")

if is_anthropic_key_valid():
    print("Anthropic key is valid!")
```

---

## Validation Details

### OpenAI Validation

**Request:**
```python
GET https://api.openai.com/v1/models
Headers:
  Authorization: Bearer sk-your-key
```

**Success:** Status 200
**Failure:** Status 401 (invalid key), timeout, or connection error

**Why this endpoint?**
- Lightweight (doesn't consume tokens)
- Fast response
- Definitively validates key

### Anthropic Validation

**Request:**
```python
POST https://api.anthropic.com/v1/messages
Headers:
  x-api-key: sk-ant-your-key
  anthropic-version: 2023-06-01
Body:
  {
    "model": "claude-3-haiku-20240307",
    "max_tokens": 1,
    "messages": [{"role": "user", "content": "test"}]
  }
```

**Success:** Status 200, 400, or 429 (all indicate valid key)
**Failure:** Status 401 (invalid key), timeout, or connection error

**Why this endpoint?**
- Minimal token usage (1 token)
- Fast response
- Status 400/429 still confirm key is valid (just rate limited)

### Ollama Validation

**Request:**
```python
GET http://localhost:11434/api/tags
```

**Success:** Status 200 with list of available models
**Failure:** Connection refused, timeout, or error

---

## Troubleshooting

### "⚠ Set but invalid" for OpenAI

**Possible causes:**
1. Key is revoked or deleted
2. Typo in the key
3. Wrong key format (should start with `sk-`)
4. Network/firewall blocking access to OpenAI

**Solutions:**
```bash
# 1. Verify key at OpenAI dashboard
open https://platform.openai.com/api-keys

# 2. Check .env file format (no quotes!)
cat .env | grep OPENAI_API_KEY
# Should be: OPENAI_API_KEY=sk-abc123
# NOT: OPENAI_API_KEY="sk-abc123"

# 3. Test manually
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 4. Regenerate key if needed
```

### "⚠ Set but invalid" for Anthropic

**Possible causes:**
1. Key is revoked or deleted
2. Typo in the key
3. Wrong key format (should start with `sk-ant-`)
4. Network/firewall blocking access to Anthropic

**Solutions:**
```bash
# 1. Verify key at Anthropic dashboard
open https://console.anthropic.com/settings/keys

# 2. Check .env file format
cat .env | grep ANTHROPIC_API_KEY

# 3. Test manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"test"}]}'
```

### "✗ Not configured" for Ollama

**Possible causes:**
1. Ollama not installed
2. Ollama server not running
3. Wrong URL in OLLAMA_BASE_URL

**Solutions:**
```bash
# 1. Install Ollama
brew install ollama  # macOS
# Or download from https://ollama.com/

# 2. Start Ollama server
ollama serve

# 3. Verify it's running
curl http://localhost:11434/api/tags

# 4. Pull a model
ollama pull llama3.2

# 5. Check .env
cat .env | grep OLLAMA
# Should have:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2
```

---

## Performance Impact

**Validation timing:**
- Ollama: ~10-50ms (local)
- OpenAI: ~100-300ms (network)
- Anthropic: ~200-500ms (network + minimal API call)

**Total validation time:** ~500ms-1s for all services

**When validation runs:**
- On `check_env.py` execution
- On `get_api_key_status()` call
- NOT on every query (only on config check)

---

## Disabling Validation

If you want to skip validation for faster startup:

```python
from src.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_BASE_URL

# Just check if keys are set (no validation)
has_openai = bool(OPENAI_API_KEY)
has_anthropic = bool(ANTHROPIC_API_KEY)
has_ollama = bool(OLLAMA_BASE_URL)
```

---

## Error Handling

All validation functions are **safe** and won't crash:

```python
def is_openai_key_valid() -> bool:
    try:
        # ... validation logic ...
        return response.status_code == 200
    except:
        return False  # Never crashes
```

**Benefits:**
- Won't break if API is temporarily down
- Won't crash on network errors
- Won't hang (3-second timeout)
- Always returns True/False

---

## Examples

### Check before querying

```python
from src.config import is_openai_key_valid, is_ollama_configured

if is_ollama_configured():
    llm_model = "ollama"
    print("Using Ollama (free, local)")
elif is_openai_key_valid():
    llm_model = "gpt-3.5-turbo"
    print("Using OpenAI GPT")
else:
    llm_model = "mock"
    print("No LLM configured, using mock mode")
```

### Warn user about invalid keys

```python
from src.config import get_api_key_status

status = get_api_key_status()

if status["openai"] == "⚠ Set but invalid":
    print("WARNING: Your OpenAI API key appears invalid!")
    print("Please check your key at: https://platform.openai.com/api-keys")
```

### Pre-flight check

```python
from src.config import get_api_key_status

def preflight_check():
    """Run before starting application"""
    status = get_api_key_status()

    # Ensure at least one LLM backend is available
    valid_backends = [
        status["ollama"] == "✓ Configured",
        status["openai"] == "✓ Valid",
        status["anthropic"] == "✓ Valid"
    ]

    if not any(valid_backends):
        raise RuntimeError(
            "No valid LLM backend configured! "
            "Please configure Ollama, OpenAI, or Anthropic."
        )

    print("✓ Pre-flight check passed")
    return True
```

---

## Security Note

**API key validation makes minimal requests:**
- OpenAI: Lists available models (no token usage)
- Anthropic: Sends 1 token (minimal cost: ~$0.00001)
- Ollama: Local request (no cost)

**Privacy:**
- No sensitive data is sent
- Only test endpoints are called
- Keys are never logged or stored
- Validation is optional

---

## Summary

**What validation gives you:**
- ✓ Immediate feedback on configuration issues
- ✓ Catch typos before querying
- ✓ Verify keys work before starting work
- ✓ Clear error messages for troubleshooting
- ✓ Automatic fallback to available backends

**When to use:**
- Always run `check_env.py` after configuration
- Before deploying to production
- When debugging LLM issues
- After changing API keys

**Quick command:**
```bash
python check_env.py
```
