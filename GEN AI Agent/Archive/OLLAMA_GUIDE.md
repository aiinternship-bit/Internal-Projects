# Ollama Integration Guide

Complete guide for using Ollama (local LLMs) with Excel-RAG system.

## What is Ollama?

Ollama is a **local LLM server** that runs models on your machine:
- ✓ **Free** - No API costs
- ✓ **Private** - Data never leaves your machine
- ✓ **Fast** - No network latency
- ✓ **Offline** - Works without internet
- ✗ **Resource intensive** - Requires good CPU/GPU

**Official site:** https://ollama.com/

---

## Quick Setup

### 1. Install Ollama

**macOS:**
```bash
# Download from https://ollama.com/
# Or use Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### 2. Start Ollama Server

```bash
ollama serve
```

**Note:** Keep this terminal open while using Excel-RAG

### 3. Pull a Model

```bash
# Recommended: Llama 3.2 (fast, good quality)
ollama pull llama3.2

# Other options:
ollama pull mistral      # Fast, efficient
ollama pull qwen2.5      # Good for code
ollama pull llama3.1     # Larger, more capable
ollama pull codellama    # Optimized for code
```

### 4. Configure .env

```bash
# Add to .env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_MODEL=ollama  # Use Ollama by default
```

### 5. Verify Setup

```bash
python check_env.py
```

**Expected output:**
```
API Keys:
  ollama: ✓ Configured
  openai: ✗ Not set
  anthropic: ✗ Not set
```

### 6. Test Query

```bash
python main.py query "test query" --llm ollama
```

---

## Available Models

### Recommended for Excel-RAG

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **llama3.2** | 2GB | Fast | Good | General purpose, best balance |
| **mistral** | 4GB | Fast | Good | Efficient, good for simple queries |
| **qwen2.5** | 4GB | Medium | Excellent | Best quality for data analysis |
| **llama3.1** | 8GB | Medium | Excellent | More capable, slower |

### How to Choose

**For fast development:**
```bash
ollama pull llama3.2
LLM_MODEL=ollama
```

**For best quality:**
```bash
ollama pull qwen2.5
OLLAMA_MODEL=qwen2.5
```

**For coding/technical queries:**
```bash
ollama pull codellama
OLLAMA_MODEL=codellama
```

---

## Usage

### CLI Usage

```bash
# Use Ollama (default if configured)
python main.py query "What is the delivery status?"

# Explicitly specify Ollama
python main.py query "What is the delivery status?" --llm ollama

# Override to use OpenAI instead
python main.py query "What is the delivery status?" --llm gpt-3.5-turbo
```

### Python API

```python
from src.llm_layer import LLMLayer

# Use Ollama
llm = LLMLayer(model_name="ollama")
response = llm.generate_answer(context, query)

# Specify Ollama model
import os
os.environ["OLLAMA_MODEL"] = "llama3.1"
llm = LLMLayer(model_name="ollama")
```

### Interactive Mode

```bash
python main.py interactive --llm ollama
```

---

## Priority System

Excel-RAG uses Ollama **first** if configured:

1. **Ollama** (if `OLLAMA_BASE_URL` is set and server is running)
2. **OpenAI** (if `OPENAI_API_KEY` is set)
3. **Anthropic** (if `ANTHROPIC_API_KEY` is set)
4. **Mock** (fallback for testing)

### Example Configurations

**Ollama only:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_MODEL=ollama
```

**Ollama with cloud fallback:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OPENAI_API_KEY=sk-your-key
LLM_MODEL=ollama  # Uses Ollama first, falls back to OpenAI if Ollama fails
```

**Cloud only (disable Ollama):**
```bash
# Don't set OLLAMA_BASE_URL or comment it out
# OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-3.5-turbo
```

---

## Performance Tuning

### Temperature Settings

```bash
# More focused, deterministic answers
LLM_TEMPERATURE=0.1

# Balanced (default)
LLM_TEMPERATURE=0.7

# More creative, varied answers
LLM_TEMPERATURE=1.5
```

### Response Length

```bash
# Shorter responses (faster)
LLM_MAX_TOKENS=500

# Standard
LLM_MAX_TOKENS=2000

# Longer responses
LLM_MAX_TOKENS=4000
```

### Model-Specific Settings

For `.env`:
```bash
# Fast, short answers
OLLAMA_MODEL=llama3.2
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000

# Quality, detailed answers
OLLAMA_MODEL=qwen2.5
LLM_TEMPERATURE=0.5
LLM_MAX_TOKENS=3000
```

---

## Troubleshooting

### "Cannot connect to Ollama"

**Problem:** Connection refused error

**Solutions:**
1. Start Ollama server: `ollama serve`
2. Check if running: `curl http://localhost:11434/api/tags`
3. Verify URL in .env: `OLLAMA_BASE_URL=http://localhost:11434`

### "Model not found"

**Problem:** Model hasn't been pulled

**Solution:**
```bash
# List available models
ollama list

# Pull the model you need
ollama pull llama3.2

# Verify it's downloaded
ollama list
```

### "Ollama request timed out"

**Problem:** Query too large or model too slow

**Solutions:**
1. Use a smaller model: `llama3.2` instead of `llama3.1`
2. Reduce context size: Lower `TOP_K_CONTENT` in .env
3. Use fewer sheets: Lower `TOP_K_STRUCTURE` in .env
4. Increase timeout in code (advanced)

### Poor quality answers

**Solutions:**
1. Try a better model: `qwen2.5` or `llama3.1`
2. Adjust temperature: Lower for more focused (0.3)
3. Provide more context: Increase `TOP_K_CONTENT`
4. Use cross-sheet mode: `--cross-sheet --entity "specific item"`

### Memory issues

**Problem:** System runs out of RAM

**Solutions:**
1. Use smaller model: `llama3.2` (2GB) instead of `llama3.1` (8GB)
2. Close other applications
3. Limit context: Reduce `TOP_K_CONTENT` and `TOP_K_STRUCTURE`
4. Use quantized models (if available)

---

## Comparing Ollama vs Cloud LLMs

| Feature | Ollama (Local) | OpenAI/Anthropic (Cloud) |
|---------|----------------|--------------------------|
| **Cost** | Free | Pay per token |
| **Privacy** | 100% local | Data sent to API |
| **Speed** | Depends on hardware | Consistent, fast |
| **Offline** | ✓ Works offline | ✗ Requires internet |
| **Quality** | Good (model-dependent) | Excellent |
| **Setup** | More complex | Simple (API key) |
| **Resources** | Uses local CPU/GPU | No local resources |

### When to Use Ollama

✓ Privacy-sensitive data
✓ No API budget
✓ Offline environment
✓ High volume queries
✓ Development/testing

### When to Use Cloud LLMs

✓ Best quality needed
✓ Limited local resources
✓ Production deployment
✓ Consistent performance
✓ Latest model features

---

## Advanced Configuration

### Custom Ollama Server

```bash
# Remote Ollama server
OLLAMA_BASE_URL=http://192.168.1.100:11434
OLLAMA_MODEL=llama3.2
```

### Multiple Models

```python
# Switch models dynamically
import os

# Use Llama for simple queries
os.environ["OLLAMA_MODEL"] = "llama3.2"
llm_fast = LLMLayer(model_name="ollama")

# Use Qwen for complex queries
os.environ["OLLAMA_MODEL"] = "qwen2.5"
llm_quality = LLMLayer(model_name="ollama")
```

### GPU Acceleration

Ollama automatically uses GPU if available. Verify:

```bash
# Check GPU usage
nvidia-smi  # For NVIDIA GPUs
ollama ps   # See running models
```

---

## Cost Comparison

### Example: 1000 queries with ~1500 tokens each

**Ollama (Free):**
- Cost: $0
- One-time setup: ~1 hour
- Ongoing: Electricity cost (minimal)

**OpenAI GPT-3.5:**
- Input tokens: 1000 * 1000 = 1M tokens = $0.50
- Output tokens: 1000 * 500 = 500K tokens = $0.75
- **Total: $1.25 per 1000 queries**

**Anthropic Claude:**
- Input tokens: $3.00
- Output tokens: $15.00
- **Total: $18.00 per 1000 queries**

**For 10K queries/month:**
- Ollama: $0
- GPT-3.5: $12.50/month
- Claude: $180/month

---

## LangSmith Integration

Ollama queries are **automatically traced** to LangSmith:

```bash
# Enable tracing
LANGCHAIN_API_KEY=ls-your-key
LANGCHAIN_TRACING_V2=true

# Run query (auto-traced!)
python main.py query "test" --llm ollama
```

**Traces include:**
- Model used (ollama/llama3.2)
- Execution time
- Estimated token usage
- Full prompt and response

View at: https://smith.langchain.com/

---

## Best Practices

### 1. Model Selection

```bash
# Development: Fast iteration
OLLAMA_MODEL=llama3.2

# Production: Best quality
OLLAMA_MODEL=qwen2.5
```

### 2. Keep Server Running

```bash
# Run in background
ollama serve &

# Or use system service (Linux)
sudo systemctl start ollama
```

### 3. Update Models Regularly

```bash
# Check for updates
ollama list

# Update a model
ollama pull llama3.2
```

### 4. Monitor Resource Usage

```bash
# Check running models
ollama ps

# View model info
ollama show llama3.2
```

---

## Migration Guide

### From Mock to Ollama

**Before:**
```bash
LLM_MODEL=mock
```

**After:**
```bash
# Install and start Ollama
ollama serve
ollama pull llama3.2

# Update .env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_MODEL=ollama
```

### From OpenAI to Ollama

**Before:**
```bash
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-3.5-turbo
```

**After (keeping OpenAI as fallback):**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OPENAI_API_KEY=sk-your-key  # Keep for fallback
LLM_MODEL=ollama
```

---

## Summary

**Setup:**
```bash
# 1. Install Ollama
brew install ollama  # macOS

# 2. Start server
ollama serve

# 3. Pull model
ollama pull llama3.2

# 4. Configure
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
echo "OLLAMA_MODEL=llama3.2" >> .env
echo "LLM_MODEL=ollama" >> .env

# 5. Test
python check_env.py
python main.py query "test" --llm ollama
```

**Verify it's working:**
- check_env.py shows "✓ Configured" for Ollama
- Queries complete without errors
- LangSmith shows "ollama/llama3.2" model

For more help:
- **Ollama docs:** https://github.com/ollama/ollama
- **Model library:** https://ollama.com/library
- **Excel-RAG env guide:** `ENV_SETUP_GUIDE.md`
