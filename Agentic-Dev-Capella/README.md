# Dynamic Multi-Agent Development System - Vertex AI Agent Engine

An intelligent, multi-agent system for software development with **dynamic agent detection**, **multimodal inputs**, and **parallel execution** using **Vertex AI Agent Engine** with **Agent-to-Agent (A2A) communication protocol**.

**New Features:**
- **Dynamic Agent Detection** - Automatically selects required agents based on task analysis
- **Multimodal Inputs** - Supports images, PDFs, design files, videos for comprehensive requirements
- **Expanded Agent Teams** - Frontend, backend, mobile, infrastructure, and legacy modernization engineers
- **Intelligent Orchestration** - AI-powered task decomposition and parallel execution

## Overview

This system leverages Google Cloud's Vertex AI Agent Engine to deploy specialized agents that communicate asynchronously via Pub/Sub, orchestrated by an **intelligent dynamic coordinator**. The architecture uses:

- **Vertex AI Agent Engine** (Reasoning Engine) for agent deployment
- **Vertex AI Vector Search** (Matching Engine) for knowledge storage
- **Google Cloud Pub/Sub** for A2A communication
- **Gemini 2.0 Flash (multimodal)** for code generation, analysis, and vision tasks
- **Dynamic Orchestration** with AI-powered agent selection

## System Capabilities

### 1. Dynamic Task Understanding

The system intelligently analyzes tasks from multiple input types:

- **Text Requirements** - Natural language descriptions, user stories
- **Visual Designs** - UI mockups (PNG/JPG), wireframes, Figma/Sketch files
- **Documents** - PDFs with requirements, architecture diagrams, specifications
- **Video** - App demos, user flow recordings
- **Audio** - Stakeholder interviews, requirements discussions
- **Code** - Existing implementations, examples

### 2. Intelligent Agent Selection

Instead of predefined workflows, the orchestrator:

1. **Analyzes task requirements** using LLM reasoning
2. **Matches capabilities** against available agent pool
3. **Assembles optimal team** based on task needs
4. **Creates execution plan** with parallel workflows

### 3. Comprehensive Agent Teams

**Frontend Engineering (7 agents)**
- UI/UX Designer - Design systems, wireframes, component specs
- React Developer - React/Next.js applications
- Vue Developer - Vue/Nuxt applications
- Angular Developer - Angular applications
- Mobile Developer - React Native, Flutter apps
- CSS/Styling Agent - Tailwind, styled-components
- Accessibility Agent - WCAG compliance, a11y testing

**Backend Engineering (5 agents)**
- API Developer - REST/GraphQL/gRPC APIs
- Database Engineer - Schema design, migrations, optimization
- Microservices Architect - Service decomposition, patterns
- Data Engineer - ETL pipelines, data warehousing
- Message Queue Agent - Kafka, RabbitMQ, Pub/Sub setup

**Infrastructure & DevOps (3 agents)**
- Cloud Infrastructure - Terraform, CloudFormation, GCP DM
- Kubernetes Agent - Manifests, Helm charts, service mesh
- Observability Agent - Prometheus, Grafana, tracing

**Quality & Security (3 agents)**
- Performance Testing - Load testing, profiling
- Security Auditor - Penetration testing, vulnerability scanning
- Compliance Agent - GDPR, HIPAA, SOC2 validation

**Legacy Modernization (26 agents)**
- All existing COBOL/legacy modernization agents
- Organized in discovery, ETL, development, CI/CD stages

**Total: 44+ Specialized Agents**

### 4. Example Use Cases

**Use Case 1: Build Dashboard from Design Mockup**
- Input: PNG mockup + requirements PDF
- Agents activated: UI Designer → React Developer → API Developer → Database Engineer
- Output: Full-stack dashboard with real-time data

**Use Case 2: Microservices from Architecture Diagram**
- Input: PDF with architecture diagram + text description
- Agents activated: Microservices Architect → API Developers × N → Database Engineer → Kubernetes Agent
- Output: Complete microservices deployment

**Use Case 3: Mobile App from Competitor Demo**
- Input: Video of competitor app
- Agents activated: Video Analyzer → UI Designer → Mobile Developer → API Developer
- Output: React Native app with similar features

### Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                    Dynamic Multi-Agent System                          │
│                    (Vertex AI Agent Engine)                            │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │              Multimodal Input Processing Layer                  │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  Images → Vision Model  │  PDFs → Doc Parser  │  Video → Frames │  │
│  │  Audio → Speech-to-Text │  Design Files → API │  Code → AST    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │           Dynamic Orchestrator (AI-Powered)                     │  │
│  │  • Task Analysis  • Agent Selection  • Execution Planning      │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                ↓                                        │
│          ┌─────────────────Pub/Sub A2A Messages───────────────┐        │
│          │                                                     │        │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐   │        │
│  │  Frontend     │  │   Backend     │  │ Infrastructure │   │        │
│  │  Team (7)     │  │   Team (5)    │  │   Team (3)     │   │        │
│  └───────────────┘  └───────────────┘  └────────────────┘   │        │
│          │                   │                   │            │        │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐   │        │
│  │ Legacy Mod    │  │   Quality &   │  │   Validation   │   │        │
│  │  Team (26)    │  │  Security (3) │  │   Agents       │   │        │
│  └───────────────┘  └───────────────┘  └────────────────┘   │        │
│                                ↓                              │        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │          Vertex AI Vector Search (Knowledge Base)               │  │
│  │  • Legacy Code  • Design Patterns  • Best Practices            │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Dynamic Orchestration (NEW)

**Intelligent Task Analysis:**
- LLM-powered understanding of task requirements from any input type
- Automatic capability extraction and complexity estimation
- Dependency graph generation

**AI-Powered Agent Selection:**
- Capability-based matching instead of hardcoded routing
- Performance-aware selection (historical success rates)
- Cost optimization (use cheaper models for simpler tasks)
- Load balancing across available agents

**Parallel Execution:**
- Automatic parallelization of independent tasks
- Up to 20 agents executing concurrently
- Dependency-aware scheduling

### 2. Multimodal Input Processing (NEW)

**Vision Understanding:**
- UI mockups → Component specifications
- Architecture diagrams → Service designs
- Wireframes → HTML/CSS layouts
- Powered by Gemini 2.0 Flash (multimodal)

**Document Parsing:**
- PDFs → Structured requirements extraction
- Embedded diagrams → Visual analysis
- Tables → Data model specifications

**Design File Integration:**
- Figma API → Component extraction
- Design tokens → CSS variables
- Auto-layout → Flexbox/Grid specs

**Video Analysis:**
- Frame extraction for UI screens
- Audio transcription for requirements
- User flow identification

**Audio Processing:**
- Stakeholder interviews → Requirements docs
- Meeting notes → User stories

### 3. Vertex AI Integration

- **Reasoning Engine**: All agents deployed as Vertex AI Reasoning Engines
- **Vector Search**: Knowledge stored in Vertex AI Matching Engine
- **A2A Protocol**: Native agent-to-agent communication via Pub/Sub
- **Gemini 2.0 Flash**: Multimodal model for code, vision, and reasoning tasks

### 4. Agent Communication

Agents communicate asynchronously using Google Cloud Pub/Sub:
- Each agent has a dedicated subscription filtered by agent ID
- Messages follow standardized A2A protocol
- Supports request-response and publish-subscribe patterns
- Automatic retry and dead-letter handling

## Prerequisites

### Google Cloud Setup

1. **GCP Project** with billing enabled
2. **APIs Enabled**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable pubsub.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

3. **IAM Permissions**:
   - Vertex AI User
   - Pub/Sub Admin
   - Storage Admin

4. **GCS Bucket** for staging:
   ```bash
   gsutil mb -l us-central1 gs://your-project-staging-bucket
   ```

### Local Environment

- Python 3.10+
- Google Cloud SDK
- Vertex AI SDK

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd legacy-modernization-system
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings:
# PROJECT_ID=your-project-id
# LOCATION=us-central1
# STAGING_BUCKET=gs://your-staging-bucket
```

## Deployment

### Step 1: Deploy Agents to Vertex AI

```bash
python scripts/deploy_vertex_agents.py \
  --project-id YOUR_PROJECT_ID \
  --location us-central1 \
  --staging-bucket gs://your-staging-bucket \
  --config config/agents_config.yaml
```

This will:
1. Create Vertex AI Vector Search index and endpoint
2. Deploy all agents as Reasoning Engines
3. Setup Pub/Sub topics and subscriptions for A2A
4. Export agent registry to `config/agent_registry.json`

**Expected output:**
```
================================================================================
DEPLOYING AGENTS TO VERTEX AI AGENT ENGINE
================================================================================

[1/4] Setting up Vertex AI Vector Search...
Created index: projects/.../locations/.../indexes/...
Created endpoint: projects/.../locations/.../indexEndpoints/...
✓ Vector Search ready

[2/4] Deploying Orchestrator Agent...
✓ Orchestrator deployed: projects/.../locations/.../reasoningEngines/...

[3/4] Deploying Stage Agents...
  → Deploying Discovery agents...
    ✓ Discovery agents deployed
  → Deploying ETL agents...
    ✓ ETL agents deployed
  → Deploying Development agents...
    ✓ Development agents deployed
  → Deploying CI/CD agents...
    ✓ CI/CD agents deployed
  ✓ All stage agents deployed

[4/4] Configuring A2A Communication...
✓ A2A communication configured

================================================================================
DEPLOYMENT COMPLETE
================================================================================

Deployed Agents: 26

✓ Agent registry exported to: config/agent_registry.json
```

### Step 2: Load Legacy Code into Vector Search

```bash
python scripts/load_legacy_knowledge.py \
  --project-id YOUR_PROJECT_ID \
  --legacy-repo /path/to/legacy/code \
  --index-endpoint projects/.../indexEndpoints/...
```

This ingests your legacy codebase into Vertex AI Vector Search for semantic querying.

### Step 3: Run the Modernization Pipeline

```bash
python scripts/run_vertex_pipeline.py \
  --project-id YOUR_PROJECT_ID \
  --location us-central1 \
  --legacy-repo /path/to/legacy/code \
  --output ./modernized_output \
  --agent-registry config/agent_registry.json
```

## Architecture Deep Dive

### Vertex AI Agent Engine (Reasoning Engine)

Each agent is deployed as a Reasoning Engine:

```python
from vertexai.preview import reasoning_engines

# Deploy agent
reasoning_engine = reasoning_engines.ReasoningEngine.create(
    agent_instance,
    requirements=["google-cloud-aiplatform", "vertexai"],
    display_name="developer_agent",
    description="Developer agent for code implementation"
)
```

### Agent-to-Agent (A2A) Communication

Messages flow through Pub/Sub with filtering:

```python
# Create A2A message
message = A2AMessage(
    message_type=A2AMessageType.TASK_ASSIGNMENT,
    sender_agent_id="projects/.../orchestrator",
    recipient_agent_id="projects/.../developer",
    payload={"task_id": "dev_001", "component_id": "auth"}
)

# Send via message bus
message_bus.publish_message(message)
```

**Pub/Sub Topic Structure:**
- Topic: `legacy-modernization-messages`
- Subscriptions per agent with filters:
  - Filter: `attributes.recipient_agent_id="projects/.../developer"`

### Vertex AI Vector Search

Knowledge storage using Matching Engine:

```python
# Query for component context
results = vector_search.query_semantic(
    query_text="payment processing business logic",
    deployed_index_id="legacy_code_v1",
    top_k=10
)
```

**Index Structure:**
- Embeddings: 768-dimensional vectors from text-embedding-004
- Metadata: Component ID, file path, language, complexity
- Distance: Dot product similarity

## Agent Communication Patterns

### 1. Task Assignment Pattern

```
Orchestrator → Developer Agent
┌────────────┐         ┌──────────────┐
│Orchestrator│────────►│   Developer  │
│   Agent    │ Task    │     Agent    │
└────────────┘         └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │Code Validator│
                       └──────────────┘
```

### 2. Validation Loop Pattern

```
Developer → Validator → Orchestrator
┌──────────┐   Submit   ┌──────────┐
│Developer │──────────►│Validator │
│  Agent   │            │  Agent   │
└──────────┘            └──────────┘
     ▲                       │
     │                       │ Pass/Fail
     │                       ▼
     │                  ┌──────────┐
     └──────────────────│Orchestra-│
        Retry/Next      │   tor    │
                        └──────────┘
```

### 3. Escalation Pattern

```
After 3 rejections → Escalation Agent → Human
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
│Validator │─►│Orchestra-│─►│Escalation│─►│ Human  │
│  Agent   │  │   tor    │  │  Agent   │  │Oversight│
└──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Configuration

### agents_config.yaml

Key configuration sections for Vertex AI:

```yaml
global:
  model: "gemini-2.0-flash-exp"
  vertex_ai:
    project_id: "your-project-id"
    location: "us-central1"
    staging_bucket: "gs://your-bucket"

orchestration:
  orchestrator:
    name: "orchestrator_agent"
    model: "gemini-2.0-flash-exp"
    a2a_enabled: true
    pubsub_topic: "legacy-modernization-messages"

vector_search:
  provider: "vertex_ai_matching_engine"
  index_endpoint: "projects/.../indexEndpoints/..."
  deployed_index_id: "legacy_code_v1"
  embedding_model: "text-embedding-004"
  dimensions: 768
```

## Monitoring & Observability

### View Agents in Vertex AI Console

```
https://console.cloud.google.com/vertex-ai/reasoning-engines?project=YOUR_PROJECT_ID
```

### Monitor A2A Messages

```bash
# View Pub/Sub metrics
gcloud pubsub topics describe legacy-modernization-messages

# View subscription backlogs
gcloud pubsub subscriptions list \
  --filter="name:developer_agent"
```

### Query Vector Search

```bash
# Test vector search endpoint
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT/locations/LOCATION/indexEndpoints/INDEX_ENDPOINT:findNeighbors \
  -d '{...}'
```

### Agent Logs

```bash
# View agent logs in Cloud Logging
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit 50 \
  --format json
```

## Testing

The project includes **two comprehensive testing approaches**:

### 1. Mock Tests (No API Keys Required)

Fast, local testing of agent tool functions without LLM API calls:

```bash
# Test all agents with mock data
python scripts/test_agents_with_mocks.py

# Results:
# ✓ All 10 agents pass
# ✓ Validates tool function logic
# ✓ No cost, runs in < 5 seconds
```

**What it tests:**
- Tool function parameters and return values
- Data validation and error handling
- Output structure correctness

**When to use:**
- During active development
- Fast iteration cycles
- CI/CD pipeline validation

### 2. LLM Tests (Requires Google Cloud Credentials)

Real-world testing with actual LLM API calls:

```bash
# Setup credentials
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID

# Test all agents with LLM
python scripts/test_agents_with_llm.py --agent all

# Or test individual agents
python scripts/test_agents_with_llm.py --agent developer
```

**What it tests:**
- Natural language prompt understanding
- Tool selection logic
- End-to-end agent behavior
- Real code generation quality

**When to use:**
- Before production deployment
- Validating prompt engineering
- Testing complex scenarios
- Acceptance testing

**Cost:** ~$0.10-$0.30 per full test run (using Gemini 2.0 Flash)

### Testing Documentation

- **Quick Start**: See [TESTING-QUICK-START.md](TESTING-QUICK-START.md)
- **Comprehensive Guide**: See [AGENT-TESTING-GUIDE.md](AGENT-TESTING-GUIDE.md)
- **LLM Testing**: See [LLM-TESTING-GUIDE.md](LLM-TESTING-GUIDE.md)

### Example Test Results

```
################################################################################
# TEST SUMMARY (Mock Tests)
################################################################################
Total Agents Tested: 10
✓ Passed: 10
✗ Failed: 0

🎉 ALL AGENT TESTS PASSED!

Agents tested:
✓ Escalation Agent (2 tests)
✓ Telemetry Agent (2 tests)
✓ Discovery Agent (2 tests)
✓ Domain Expert Agent (2 tests)
✓ Developer Agent (3 tests) - Generated real code!
✓ Code Validator Agent (2 tests)
✓ Architect Agent (1 test)
✓ QA Tester Agent (2 tests)
✓ Deployer Agent (2 tests)
✓ Monitor Agent (2 tests)
```

## Development

### Adding a New Agent

1. **Create Agent Class**

```python
# agents/stage2_development/my_agent/agent.py
from vertexai.preview import reasoning_engines

class MyAgent:
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
    
    def process_task(self, task_data: Dict) -> Dict:
        # Agent logic here
        return {"status": "success"}
    
    def handle_a2a_message(self, message: Dict) -> Dict:
        # Handle incoming A2A messages
        return {"status": "processed"}

def create_my_agent(project_id: str, location: str):
    agent = MyAgent(project_id, location)
    return reasoning_engines.ReasoningEngine.create(
        agent,
        requirements=["google-cloud-aiplatform"],
        display_name="my_agent"
    )
```

2. **Register in Deployment Script**

```python
# scripts/deploy_vertex_agents.py
my_agent = create_my_agent(project_id, location)
self.deployed_agents["my_agent"] = {
    "resource_name": my_agent.resource_name,
    "type": "stage2"
}
```

3. **Add A2A Handler**

```python
# Register message handler
message_bus.register_agent(
    agent_id=my_agent.resource_name,
    agent_name="my_agent",
    message_handler=my_agent.handle_a2a_message
)
```

### Testing A2A Communication

```python
# Test script
from shared.utils.vertex_a2a_protocol import VertexA2AMessageBus, A2AProtocolHelper

# Initialize message bus
message_bus = VertexA2AMessageBus(project_id="your-project")

# Send test message
test_message = A2AProtocolHelper.create_task_assignment(
    sender_id="test_sender",
    sender_name="test",
    recipient_id="projects/.../developer",
    recipient_name="developer_agent",
    task_data={"task_id": "test_001"}
)

message_bus.publish_message(test_message)
```

## Cost Optimization

### Vertex AI Agent Engine Pricing

- **Reasoning Engine**: Pay per query/invocation
- **Vector Search**: Index storage + query costs
- **Pub/Sub**: Message volume based

### Cost Saving Tips

1. **Use smaller models for simple tasks**: `gemini-1.5-flash` vs `gemini-2.0-flash-exp`
2. **Batch Vector Search queries**: Reduce API calls
3. **Set Pub/Sub message retention**: 7 days instead of default
4. **Auto-scaling**: Configure min/max replicas for index endpoints
5. **Delete unused indexes**: Clean up after modernization complete

## Troubleshooting

### Agent Deployment Issues

**Issue**: Reasoning Engine creation fails
```bash
# Check quota limits
gcloud ai quotas describe \
  --project=YOUR_PROJECT \
  --location=us-central1 \
  --service=aiplatform.googleapis.com
```

**Solution**: Request quota increase or use different region

### A2A Communication Issues

**Issue**: Messages not being received
```bash
# Check Pub/Sub subscription
gcloud pubsub subscriptions describe developer_agent-subscription

# Check for dead-letter messages
gcloud pubsub topics list-subscriptions legacy-modernization-messages
```

**Solution**: Verify subscription filters and agent ID matching

### Vector Search Issues

**Issue**: Low quality search results
```bash
# Check index deployment status
gcloud ai index-endpoints describe INDEX_ENDPOINT_ID \
  --region=us-central1
```

**Solution**: 
- Retrain embeddings with better text preprocessing
- Increase `leaf_nodes_to_search_percent`
- Use different distance measure (COSINE vs DOT_PRODUCT)

### Agent Timeout Issues

**Issue**: Agent times out on complex tasks

**Solution**: Increase timeout in pipeline runner:
```python
response = self.orchestrator.send_and_wait(task_message, timeout=600)  # 10 minutes
```

## Production Deployment

### High Availability Setup

1. **Multiple Index Endpoints**:
   ```bash
   # Deploy to multiple regions
   --location us-central1
   --location europe-west1
   ```

2. **Pub/Sub with Dead Letter Queue**:
   ```python
   subscription.dead_letter_policy = {
       "dead_letter_topic": "projects/.../topics/dlq",
       "max_delivery_attempts": 5
   }
   ```

3. **Agent Monitoring**:
   - Setup Cloud Monitoring alerts
   - Configure SLOs for agent response times
   - Enable Cloud Trace for A2A message tracking

### Security Best Practices

1. **VPC Service Controls**: Restrict Vertex AI API access
2. **Workload Identity**: Use for agent authentication
3. **Private Service Connect**: Keep Vector Search private
4. **Pub/Sub encryption**: Use CMEK for message encryption
5. **Audit Logging**: Enable for all Vertex AI operations

## FAQ

**Q: How is this different from the generic ADK version?**
A: This version uses Vertex AI's native Agent Engine (Reasoning Engine), managed Vector Search (Matching Engine), and Pub/Sub-based A2A protocol instead of custom implementations.

**Q: Can I use this with on-premise code?**
A: Yes, but you'll need to upload code to GCS or setup hybrid connectivity to access on-premise repositories.

**Q: What's the cost for a typical modernization?**
A: Depends on codebase size. Example for 100K LOC:
- Vector Search: ~$50-100/month
- Agent invocations: ~$200-500 for full pipeline
- Pub/Sub: ~$10/month

**Q: How do I scale to modernize multiple codebases?**
A: Deploy multiple pipeline instances with different agent registries, or use the Multi-Service Coordinator for parallel processing.

**Q: Can I use different Gemini models for different agents?**
A: Yes! Configure per-agent in `agents_config.yaml`:
```yaml
stage2_development:
  developer:
    model: "gemini-2.0-flash-exp"  # Fast for code generation
  architect:
    model: "gemini-1.5-pro"  # More reasoning for architecture
```

## Quick Start Examples

### Example 1: Build Frontend from Design Mockup

```bash
# Upload design mockup and requirements
python scripts/run_dynamic_pipeline.py \
  --inputs design_mockup.png requirements.pdf \
  --task "Build analytics dashboard" \
  --output ./dashboard_output

# System automatically:
# 1. Analyzes mockup with vision model → extracts components, colors, layout
# 2. Parses PDF → functional requirements, NFRs
# 3. Selects agents: UI Designer, React Developer, API Developer, Database Engineer
# 4. Executes in parallel: Frontend + Backend development
# 5. Outputs: Full-stack application
```

### Example 2: API from Architecture Diagram

```bash
# Upload architecture PDF
python scripts/run_dynamic_pipeline.py \
  --inputs architecture.pdf \
  --task "Implement microservices for e-commerce" \
  --output ./services_output

# System automatically:
# 1. Parses diagram → identifies services, communication patterns
# 2. Selects agents: Microservices Architect, API Developers × N, Kubernetes Agent
# 3. Generates: Service implementations, Docker files, K8s manifests
```

### Example 3: Mobile App from Competitor Demo Video

```bash
# Upload video demo
python scripts/run_dynamic_pipeline.py \
  --inputs competitor_app_demo.mp4 \
  --task "Build similar mobile app" \
  --output ./mobile_app_output

# System automatically:
# 1. Analyzes video → extracts UI screens, features, user flows
# 2. Selects agents: UI Designer, Mobile Developer, API Developer
# 3. Generates: React Native app + backend API
```

## Documentation

### Architecture & Design
- **Dynamic Architecture**: [DYNAMIC-ARCHITECTURE.md](DYNAMIC-ARCHITECTURE.md) - Complete dynamic orchestration guide
- **Original Design**: [Design Doc PDF](https://github.com/dharvpat/Agentic-Dev-Team/blob/main/Agentic%20Dev%20Team%20Design%20Doc.pdf)
- **Project Organization**: [PROJECT-DIR-ORGANIZATION.md](PROJECT-DIR-ORGANIZATION.md)

### Implementation Guides
- **A2A Communication**: [A2A-IMPLEMENTATION-GUIDE.md](A2A-IMPLEMENTATION-GUIDE.md)
- **Agent Testing**: [AGENT-TESTING-GUIDE.md](AGENT-TESTING-GUIDE.md)
- **LLM Testing**: [LLM-TESTING-GUIDE.md](LLM-TESTING-GUIDE.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Testing Quick Start**: [TESTING-QUICK-START.md](TESTING-QUICK-START.md)

### Project Info
- **Project Summary**: [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)
- **Main README**: You are here

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/repo/issues)
- **GCP Support**: [Google Cloud Support](https://cloud.google.com/support)
- **Community**: [Google Cloud Community](https://www.googlecloudcommunity.com/)

## License

[Your License Here]

---

**Built with Vertex AI Agent Engine, Gemini 2.0, and Vector Search**
