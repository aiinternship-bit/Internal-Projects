# LLM Testing Guide

Complete guide for testing agents with real LLM API calls.

## Overview

This project has **two types of tests**:

### 1. Mock Tests (`test_agents_with_mocks.py`)
- ✅ **No API keys required**
- ✅ Tests tool functions directly
- ✅ Fast execution
- ✅ No cost
- ❌ Doesn't test LLM reasoning
- ❌ Doesn't test prompt understanding

### 2. LLM Tests (`test_agents_with_llm.py`)
- ✅ Tests real LLM behavior
- ✅ Tests prompt understanding
- ✅ Tests tool selection logic
- ✅ Tests end-to-end scenarios
- ⚠️ Requires Google Cloud credentials
- ⚠️ Uses Vertex AI API (costs money)
- ⚠️ Slower execution

---

## Prerequisites for LLM Testing

### 1. Google Cloud Project Setup

```bash
# Create a new project (or use existing)
gcloud projects create YOUR_PROJECT_ID

# Set as active project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com
```

### 2. Authentication

**Option A: Application Default Credentials (Recommended for development)**
```bash
gcloud auth application-default login
```

**Option B: Service Account (Recommended for production)**
```bash
# Create service account
gcloud iam service-accounts create vertex-ai-agent-tester \
  --display-name="Vertex AI Agent Tester"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:vertex-ai-agent-tester@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/vertex-ai-key.json \
  --iam-account=vertex-ai-agent-tester@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/vertex-ai-key.json
```

### 3. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure Google Cloud AI Platform SDK is installed
pip install google-cloud-aiplatform google-adk
```

### 4. Configure Project ID

Set your Google Cloud project ID in the environment:

```bash
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Running LLM Tests

### Test All Agents

```bash
# Run all agents with LLM
python scripts/test_agents_with_llm.py --agent all
```

### Test Individual Agents

```bash
# Test escalation agent
python scripts/test_agents_with_llm.py --agent escalation

# Test discovery agent
python scripts/test_agents_with_llm.py --agent discovery

# Test domain expert agent
python scripts/test_agents_with_llm.py --agent domain_expert

# Test developer agent (generates real code!)
python scripts/test_agents_with_llm.py --agent developer

# Test code validator agent
python scripts/test_agents_with_llm.py --agent code_validator

# Test architect agent
python scripts/test_agents_with_llm.py --agent architect

# Test QA tester agent
python scripts/test_agents_with_llm.py --agent qa_tester
```

---

## What Gets Tested

### 1. **Escalation Agent**
- Natural language prompt about validation deadlocks
- Tests LLM's ability to understand rejection patterns
- Tests tool selection for analyzing and resolving deadlocks

### 2. **Discovery Agent**
- Natural language prompt to scan legacy codebase
- Tests LLM's ability to understand discovery requests
- Tests tool selection for scanning and analyzing codebases

### 3. **Domain Expert Agent**
- Natural language description of business workflows
- Tests LLM's ability to extract domain concepts
- Tests tool selection for identifying bounded contexts, entities, business rules

### 4. **Developer Agent**
- Natural language requirements for payment processor
- Tests LLM's code generation capabilities
- Tests understanding of business rules and NFRs
- **Generates real Python code!**

### 5. **Code Validator Agent**
- Code with security vulnerabilities
- Tests LLM's ability to identify security issues
- Tests code quality analysis
- Tests feedback generation

### 6. **Architect Agent**
- Natural language architecture requirements
- Tests LLM's architecture design capabilities
- Tests understanding of microservices patterns
- Tests NFR consideration

### 7. **QA Tester Agent**
- Natural language test requirements
- Tests LLM's test case generation
- Tests understanding of functional/negative/edge cases

---

## Expected Output

### Successful Test Output

```
################################################################################
# TESTING ALL AGENTS WITH LLM API CALLS
################################################################################

✓ Google Cloud credentials found
Proceeding with LLM tests...

================================================================================
TESTING: developer_agent (WITH LLM)
================================================================================

[Test 1] Generate Payment Processor Code
--------------------------------------------------------------------------------
Prompt: I need you to implement a PaymentProcessor component in Python...

Invoking agent with LLM...

✓ LLM Response:
Generated 2847 characters of code

Code preview (first 500 chars):
from typing import Dict, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta

class PaymentProcessor:
    """
    PCI-DSS compliant payment processor.
    Handles credit card, debit card, and PayPal payments.
    """

    MIN_AMOUNT = Decimal("1.00")
    MAX_AMOUNT = Decimal("50000.00")
    REFUND_WINDOW_DAYS = 30

    def __init__(self):
        self.logger = logging.getLogger(__name__)
...

✓ Developer Agent - LLM TEST PASSED
```

### Test Results Location

```
tests/agent_tests/results/llm_test_results_20250114_103045.json
```

Results include:
- Timestamp
- Total tests run
- Passed/failed count
- Full LLM responses for each test

---

## Cost Estimation

LLM tests use **Gemini 2.0 Flash** via Vertex AI:

### Pricing (as of 2025)
- Input: ~$0.075 per 1M characters
- Output: ~$0.30 per 1M characters

### Estimated Costs per Test Run
- **Single agent test**: $0.01 - $0.05
- **All 7 agents**: $0.10 - $0.30

**Note:** Actual costs depend on:
- Prompt length
- Response length
- LLM model used
- Current Vertex AI pricing

### Cost Optimization Tips

1. **Test selectively**: Run individual agents instead of all
2. **Use mock tests first**: Validate logic before LLM tests
3. **Set quotas**: Configure budget alerts in Google Cloud
4. **Review responses**: Check if prompts can be more concise

---

## Comparison: Mock Tests vs LLM Tests

| Feature | Mock Tests | LLM Tests |
|---------|-----------|-----------|
| **Cost** | Free | ~$0.10-$0.30 per run |
| **Speed** | < 5 seconds | 30-60 seconds |
| **Setup** | None | GCP credentials |
| **Tests** | Tool functions | End-to-end behavior |
| **Value** | Validate logic | Validate LLM reasoning |
| **When to use** | During development | Before deployment |

### Recommended Testing Flow

```
1. Write code → Run mock tests (fast iteration)
                     ↓
2. Mock tests pass → Run LLM tests (validate behavior)
                     ↓
3. LLM tests pass → Deploy to Vertex AI
                     ↓
4. Monitor in production → Iterate based on real usage
```

---

## Troubleshooting

### Error: "No Google Cloud credentials found"

**Solution:**
```bash
# Use application default credentials
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Error: "Permission denied on resource project"

**Solution:**
```bash
# Grant aiplatform.user role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/aiplatform.user"
```

### Error: "API aiplatform.googleapis.com not enabled"

**Solution:**
```bash
gcloud services enable aiplatform.googleapis.com
```

### Error: "Agent query method not found"

**Cause:** Agents are defined but not yet deployed to Vertex AI.

**Solution:** LLM tests currently work with local agent instances using Google ADK. To test against deployed agents:

```bash
# Deploy agents first
python scripts/deploy_vertex_agents.py \
  --project-id YOUR_PROJECT \
  --location us-central1 \
  --staging-bucket gs://your-bucket

# Then use deployed agent IDs in tests
```

### Error: "Rate limit exceeded"

**Solution:**
- Wait and retry
- Reduce concurrent tests
- Request quota increase in Google Cloud Console

---

## Advanced Configuration

### Custom Model Selection

Edit agent definitions to use different models:

```python
# In agent file (e.g., agents/stage2_development/developer/agent.py)
developer_agent = Agent(
    name="developer_agent",
    model="gemini-2.0-flash-exp",  # Change model here
    # or "gemini-1.5-pro" for higher quality (more expensive)
    ...
)
```

### Custom Prompts

Modify test prompts in `scripts/test_agents_with_llm.py`:

```python
def test_developer_agent_with_llm():
    prompt = """
    Your custom prompt here...
    """
    response = developer_agent.query(prompt)
```

### Add New Test Cases

```python
def test_my_custom_scenario():
    """Test custom scenario."""
    from agents.stage2_development.developer.agent import developer_agent

    print("\n[Test] My Custom Scenario")
    prompt = "Your test prompt..."

    try:
        response = developer_agent.query(prompt)
        print(f"✓ Response: {response}")
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Add to run_all_llm_tests()
tests.append(("My Custom Test", test_my_custom_scenario))
```

---

## Next Steps

1. ✅ **Run mock tests first** to validate tool logic
   ```bash
   python scripts/test_agents_with_mocks.py
   ```

2. ✅ **Set up Google Cloud credentials**
   ```bash
   gcloud auth application-default login
   ```

3. ✅ **Run LLM tests on one agent**
   ```bash
   python scripts/test_agents_with_llm.py --agent developer
   ```

4. ✅ **Review results** in `tests/agent_tests/results/`

5. ✅ **Run all LLM tests**
   ```bash
   python scripts/test_agents_with_llm.py --agent all
   ```

6. ✅ **Deploy to Vertex AI** (see QUICKSTART.md)
   ```bash
   python scripts/deploy_vertex_agents.py --project-id YOUR_PROJECT
   ```

---

## Summary

**Mock Tests** (`test_agents_with_mocks.py`):
- Fast, free, local testing
- Validates tool function logic
- Perfect for development iteration

**LLM Tests** (`test_agents_with_llm.py`):
- Real LLM behavior testing
- Validates prompt understanding
- Tests end-to-end scenarios
- Requires GCP credentials and incurs costs

**Use both** for comprehensive testing before production deployment!
