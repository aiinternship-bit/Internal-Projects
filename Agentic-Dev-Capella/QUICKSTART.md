# Quick Start Guide - Vertex AI Agent Engine

Get your legacy modernization pipeline running in **under 30 minutes**.

## Prerequisites Checklist

- [ ] GCP Project with billing enabled
- [ ] Owner or Editor role on the project
- [ ] `gcloud` CLI installed
- [ ] Python 3.10+ installed

## Step-by-Step Setup

### 1. Setup GCP (5 minutes)

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export BUCKET_NAME="${PROJECT_ID}-staging"

# Configure gcloud
gcloud config set project $PROJECT_ID
gcloud auth login
gcloud auth application-default login

# Enable required APIs
gcloud services enable aiplatform.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com

# Create staging bucket
gsutil mb -l $REGION gs://$BUCKET_NAME
```

### 2. Clone and Install (5 minutes)

```bash
# Clone repository
git clone https://github.com/your-org/legacy-modernization.git
cd legacy-modernization-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment (2 minutes)

```bash
# Create .env file
cat > .env << EOF
PROJECT_ID=$PROJECT_ID
LOCATION=$REGION
STAGING_BUCKET=gs://$BUCKET_NAME
EOF

# Verify configuration
cat config/agents_config.yaml
# Update project_id if needed
```

### 4. Deploy Agents (10 minutes)

```bash
# Deploy all agents to Vertex AI
python scripts/deploy_vertex_agents.py \
  --project-id $PROJECT_ID \
  --location $REGION \
  --staging-bucket gs://$BUCKET_NAME \
  --config config/agents_config.yaml

# This creates:
# - Vertex AI Vector Search index and endpoint
# - 26 Reasoning Engine agents
# - Pub/Sub topics and subscriptions
# - Agent registry JSON file

# Expected time: 8-10 minutes
```

### 5. Load Sample Legacy Code (5 minutes)

```bash
# For testing, use the included sample COBOL code
python scripts/load_legacy_knowledge.py \
  --project-id $PROJECT_ID \
  --legacy-repo examples/sample_cobol_system \
  --agent-registry config/agent_registry.json

# Or use your own legacy codebase
python scripts/load_legacy_knowledge.py \
  --project-id $PROJECT_ID \
  --legacy-repo /path/to/your/legacy/code \
  --agent-registry config/agent_registry.json
```

### 6. Run Pipeline (5 minutes)

```bash
# Run the modernization pipeline
python scripts/run_vertex_pipeline.py \
  --project-id $PROJECT_ID \
  --location $REGION \
  --legacy-repo examples/sample_cobol_system \
  --output ./output \
  --agent-registry config/agent_registry.json

# Watch the agents communicate via A2A protocol
# Output will be in ./output directory
```

## Verify Deployment

### Check Agents in Vertex AI Console

```bash
# Open in browser
echo "https://console.cloud.google.com/vertex-ai/reasoning-engines?project=$PROJECT_ID"
```

You should see 26 deployed agents:
- orchestrator_agent
- discovery_agent
- developer_agent
- code_validator_agent
- qa_agent
- etc.

### Check Vector Search

```bash
# List indexes
gcloud ai indexes list --region=$REGION

# List index endpoints
gcloud ai index-endpoints list --region=$REGION
```

### Check Pub/Sub Topics

```bash
# List topics
gcloud pubsub topics list

# Should see: legacy-modernization-messages

# List subscriptions
gcloud pubsub subscriptions list
```

### Test A2A Communication

```python
# test_a2a.py
from shared.utils.vertex_a2a_protocol import VertexA2AMessageBus, A2AProtocolHelper
import json

# Load agent registry
with open('config/agent_registry.json', 'r') as f:
    registry = json.load(f)

# Initialize message bus
message_bus = VertexA2AMessageBus(
    project_id="your-project-id",
    topic_name="legacy-modernization-messages"
)

# Send test message
test_msg = A2AProtocolHelper.create_task_assignment(
    sender_id=registry['orchestrator_agent']['resource_name'],
    sender_name="orchestrator_agent",
    recipient_id=registry['developer_agent']['resource_name'],
    recipient_name="developer_agent",
    task_data={"task_id": "test_001", "task_type": "test"}
)

message_id = message_bus.publish_message(test_msg)
print(f"Message sent: {message_id}")
```

```bash
python test_a2a.py
```

## Troubleshooting

### Issue: API not enabled

```bash
# Error: API [aiplatform.googleapis.com] not enabled
gcloud services enable aiplatform.googleapis.com
```

### Issue: Permission denied

```bash
# Grant yourself required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/pubsub.admin"
```

### Issue: Quota exceeded

```bash
# Check quotas
gcloud ai quotas describe \
  --project=$PROJECT_ID \
  --location=$REGION \
  --service=aiplatform.googleapis.com

# Request increase if needed
```

### Issue: Agent deployment fails

```bash
# Check logs
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit 50 \
  --format json

# Retry deployment with increased timeout
# Edit scripts/deploy_vertex_agents.py and increase timeouts
```

## Next Steps

### 1. Customize Configuration

Edit `config/agents_config.yaml` to customize:
- Agent models (Gemini 2.0 vs 1.5)
- Validation thresholds
- Deployment strategies
- Vector search parameters

### 2. Add Your Legacy Code

```bash
# Prepare your legacy codebase
# Ensure it's in a directory structure:
# /legacy-code/
#   ├── src/
#   ├── config/
#   ├── schemas/
#   └── docs/

# Load it into Vector Search
python scripts/load_legacy_knowledge.py \
  --project-id $PROJECT_ID \
  --legacy-repo /path/to/your/code \
  --agent-registry config/agent_registry.json
```

### 3. Monitor Progress

```bash
# View agent logs in real-time
gcloud logging tail "resource.type=aiplatform.googleapis.com/ReasoningEngine"

# View Pub/Sub message metrics
gcloud pubsub topics describe legacy-modernization-messages --format="table(name,metrics)"
```

### 4. Review Output

```bash
# Check modernized code
ls -la ./output/

# Review architecture documents
cat ./output/architecture/*.md

# Check generated tests
cat ./output/tests/*.py
```

## Clean Up (when done)

```bash
# Delete all deployed agents
for agent in $(gcloud ai reasoning-engines list --region=$REGION --format="value(name)"); do
  gcloud ai reasoning-engines delete $agent --region=$REGION --quiet
done

# Delete Vector Search resources
gcloud ai index-endpoints delete INDEX_ENDPOINT_ID --region=$REGION --quiet
gcloud ai indexes delete INDEX_ID --region=$REGION --quiet

# Delete Pub/Sub resources
gcloud pubsub topics delete legacy-modernization-messages --quiet

# Delete staging bucket
gsutil -m rm -r gs://$BUCKET_NAME
```

## Cost Estimate

For a typical 50K LOC legacy codebase:

| Resource | Cost | Duration |
|----------|------|----------|
| Vector Search Index | $20-40 | Per month |
| Agent Invocations | $100-200 | Full pipeline |
| Pub/Sub Messages | $5-10 | Full pipeline |
| Storage (GCS) | $1-5 | Per month |
| **Total** | **$126-255** | **One-time + monthly** |

## Support

- **Documentation**: See full [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/repo/issues)
- **GCP Support**: [Google Cloud Console](https://console.cloud.google.com/support)

---

**Completed the Quick Start?**
