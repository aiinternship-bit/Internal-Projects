# A2A Implementation Guide

## Overview

This guide documents the **Agent-to-Agent (A2A) Communication Protocol** implementation for the Legacy Modernization multi-agent system. All 26 agents communicate asynchronously via Google Cloud Pub/Sub using standardized message patterns.

## Architecture

### Communication Flow

```
┌─────────────┐         Pub/Sub          ┌──────────────┐
│Orchestrator │────────Messages──────────►│   Developer  │
│   Agent     │◄────────────────────────  │    Agent     │
└─────────────┘                           └──────────────┘
      │                                          │
      │ Escalation                              │ Validation
      │ (after 3x)                              │ Request
      ▼                                          ▼
┌─────────────┐                           ┌──────────────┐
│ Escalation  │                           │ Code         │
│   Agent     │                           │ Validator    │
└─────────────┘                           └──────────────┘
```

### Key Components

1. **VertexA2AMessageBus** (`shared/utils/vertex_a2a_protocol.py`)
   - Pub/Sub message bus for async communication
   - Topic: `legacy-modernization-messages`
   - Per-agent subscriptions with filtering

2. **A2AIntegration** (`shared/utils/a2a_integration.py`)
   - Integration layer for embedding A2A in agents
   - Automatic task tracking
   - Error reporting
   - Validation loops with retry

3. **AgentBase** (`shared/utils/agent_base.py`)
   - Base class for A2A-enabled agents
   - Standard message handler patterns
   - Validator base class

4. **AgentFactory** (`shared/utils/agent_factory.py`)
   - Factory for creating agents with consistent configuration
   - Deployment to Vertex AI
   - A2A registration

## Implemented Agents

### Complete Agent List (26 Total)

#### Orchestration (3)
- ✅ `orchestrator_agent` - Central coordinator
- ✅ `escalation_agent` - Handles deadlocks and escalations
- ✅ `telemetry_audit_agent` - Tracks all activities

#### Stage 0: Discovery (2)
- ✅ `discovery_agent` - Scans legacy codebase
- ✅ `domain_expert_agent` - Infers business domain

#### Stage 1: ETL (5)
- ✅ `code_ingestion_agent` - Parses and stores code
- ✅ `static_analysis_agent` - Analyzes code quality
- ✅ `documentation_mining_agent` - Extracts documentation
- ✅ `knowledge_synthesis_agent` - Creates knowledge base
- ✅ `delta_monitoring_agent` - Tracks legacy changes

#### Stage 2: Development (11)
- ✅ `technical_architect_agent` - Designs architecture
- ✅ `architecture_validator_agent` - Validates designs
- ✅ `developer_agent` - Implements code
- ✅ `code_validator_agent` - Validates code correctness
- ✅ `quality_attribute_validator_agent` - Validates NFRs
- ✅ `builder_agent` - Builds artifacts
- ✅ `build_validator_agent` - Validates builds
- ✅ `qa_tester_agent` - Generates and runs tests
- ✅ `qa_validator_agent` - Validates test quality
- ✅ `integration_validator_agent` - Validates integration
- ✅ `integration_coordinator_agent` - Coordinates deployments

#### Stage 3: CI/CD (5)
- ✅ `deployment_agent` - Deploys services
- ✅ `deployment_validator_agent` - Validates deployments
- ✅ `monitoring_agent` - Monitors system health
- ✅ `root_cause_analysis_agent` - Analyzes incidents
- ✅ `supply_chain_security_agent` - Scans dependencies

## A2A Message Types

```python
class A2AMessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"           # Assign work to agent
    TASK_COMPLETION = "task_completion"           # Report task done
    VALIDATION_REQUEST = "validation_request"     # Request validation
    VALIDATION_RESULT = "validation_result"       # Return validation result
    ESCALATION_REQUEST = "escalation_request"     # Escalate for help
    QUERY_REQUEST = "query_request"               # Query another agent
    QUERY_RESPONSE = "query_response"             # Respond to query
    STATE_UPDATE = "state_update"                 # Update task state
    ERROR_REPORT = "error_report"                 # Report error
    HUMAN_APPROVAL_REQUEST = "human_approval_request"  # Request human review
```

## Usage Patterns

### Pattern 1: Task Assignment

```python
from shared.utils.vertex_a2a_protocol import A2AProtocolHelper

# Orchestrator assigns task to developer
task_message = A2AProtocolHelper.create_task_assignment(
    sender_id=orchestrator_id,
    sender_name="orchestrator_agent",
    recipient_id=developer_id,
    recipient_name="developer_agent",
    task_data={
        "task_id": "dev_001",
        "component_id": "payment_processor",
        "architecture_spec": {...}
    }
)

message_bus.publish_message(task_message)
```

### Pattern 2: Validation Loop with Retry

```python
from shared.utils.a2a_integration import ValidationLoopHandler

# Create handler with max 3 retries
validation_handler = ValidationLoopHandler(
    a2a_integration=a2a,
    max_retries=3,
    escalation_agent_id=escalation_id
)

# Run validation loop
result = validation_handler.validate_with_retry(
    task_id="dev_001",
    validator_id=validator_id,
    validator_name="code_validator_agent",
    artifact_generator=generate_code,  # Function that incorporates feedback
    validation_criteria=["correctness", "security"]
)

# Result statuses:
# - "validated" - passed validation
# - "escalated" - max retries reached, escalated to human
# - "failed" - error occurred
```

### Pattern 3: Automatic Task Tracking

```python
from shared.utils.a2a_integration import A2AIntegration

# Create integration
a2a = A2AIntegration(agent_context, message_bus, orchestrator_id)

# Decorate tool functions for automatic tracking
@a2a.with_task_tracking
def design_architecture(task_id: str, component_id: str) -> Dict[str, Any]:
    # Automatically sends:
    # - Task start: pending → in_progress
    # - Task complete: in_progress → completed
    # - Error reports on failure

    architecture_spec = create_architecture(component_id)
    return {"status": "success", "spec": architecture_spec}
```

### Pattern 4: Escalation

```python
# After 3 validation failures, automatically escalates
escalation_message = A2AProtocolHelper.create_escalation_request(
    sender_id=orchestrator_id,
    sender_name="orchestrator_agent",
    task_id="dev_001",
    reason="validation_deadlock",
    rejection_count=3,
    context={
        "rejection_history": [...],
        "last_artifact": {...}
    }
)

message_bus.publish_message(escalation_message)
```

## Running the System

### 1. Deploy Agents

```bash
python scripts/deploy_vertex_agents.py \
  --project-id YOUR_PROJECT_ID \
  --location us-central1 \
  --staging-bucket gs://your-bucket \
  --config config/agents_config.yaml \
  --export-registry config/agent_registry.json
```

### 2. Run Pipeline with A2A

```bash
python scripts/run_pipeline_with_a2a.py \
  --project-id YOUR_PROJECT_ID \
  --location us-central1 \
  --legacy-repo /path/to/legacy/code \
  --output ./output \
  --agent-registry config/agent_registry.json
```

### 3. Run Examples

```bash
# See all A2A communication patterns
python examples/a2a_usage_example.py
```

## File Structure

```
Agentic-Dev-Team-Capella/
├── agents/                                # All 26 agent implementations
│   ├── orchestration/
│   │   ├── orchestrator/
│   │   ├── escalation/                   # ✅ NEW
│   │   └── telemetry/                    # ✅ NEW
│   ├── stage0_discovery/
│   │   ├── discovery/
│   │   └── domain_expert/                # ✅ NEW
│   ├── stage1_etl/                       # ✅ NEW (5 agents)
│   │   ├── code_ingestion/
│   │   ├── static_analysis/
│   │   ├── documentation_mining/
│   │   ├── knowledge_synthesis/
│   │   └── delta_monitoring/
│   ├── stage2_development/               # ✅ NEW (10 agents)
│   │   ├── architecture/
│   │   │   ├── architect/
│   │   │   └── validator/
│   │   ├── developer/
│   │   ├── validation/
│   │   │   ├── code_validator/
│   │   │   └── quality_attribute/
│   │   ├── build/
│   │   │   ├── builder/
│   │   │   └── validator/
│   │   ├── qa/
│   │   │   ├── tester/
│   │   │   └── validator/
│   │   └── integration/
│   │       ├── validator/
│   │       └── coordinator/
│   └── stage3_cicd/                      # ✅ NEW (5 agents)
│       ├── deployment/
│       │   ├── deployer/
│       │   └── validator/
│       ├── monitoring/
│       │   ├── monitor/
│       │   └── root_cause/
│       └── security/
│           └── supply_chain/
│
├── shared/
│   ├── utils/
│   │   ├── vertex_a2a_protocol.py        # Core A2A protocol
│   │   ├── a2a_integration.py            # ✅ NEW - Integration utilities
│   │   ├── agent_base.py                 # ✅ NEW - Base classes
│   │   └── agent_factory.py              # ✅ NEW - Agent factory
│   ├── tools/
│   │   └── vector_db.py
│   └── models/
│       └── task.py
│
├── scripts/
│   ├── deploy_vertex_agents.py
│   ├── run_pipeline.py
│   └── run_pipeline_with_a2a.py          # ✅ NEW - Complete A2A pipeline
│
├── examples/
│   └── a2a_usage_example.py              # ✅ NEW - Usage examples
│
├── config/
│   ├── agents_config.yaml
│   └── agent_registry.json               # Generated after deployment
│
├── CLAUDE.md                             # Claude Code guidance
├── A2A-IMPLEMENTATION-GUIDE.md           # ✅ THIS FILE
└── README.md
```

## Key Improvements

### 1. Base Classes for Consistency
- `A2AEnabledAgent` - Base class with standard message handling
- `ValidatorAgent` - Specialized base for validators
- Ensures all agents follow same patterns

### 2. Integration Layer
- `A2AIntegration` - Drop-in A2A for existing agents
- Decorators for automatic task tracking
- No code changes needed in tool functions

### 3. Validation Loop Handler
- Automatic retry on validation failure
- Incorporates feedback on each iteration
- Escalates after max retries (default: 3)
- Prevents deadlocks

### 4. Agent Factory
- Consistent agent creation
- Configuration loading from YAML
- Automatic A2A registration
- Deployment to Vertex AI

### 5. Complete Agent Implementations
- All 26 agents implemented
- Domain-appropriate tools
- Proper A2A message handling
- Ready for deployment

## Message Flow Examples

### Successful Development Flow

```
1. Orchestrator → Architect
   Task: Design architecture for "PaymentProcessor"

2. Architect → Developer
   Task: Implement code based on architecture spec

3. Developer → Code Validator
   Validation Request: Validate code for correctness, security

4. Code Validator → Developer
   Validation Result: PASS

5. Developer → QA Agent
   Task: Run tests on validated code

6. QA Agent → Build Agent
   Task: Build deployment artifacts

7. Build Agent → Orchestrator
   State Update: Component complete
```

### Validation Failure with Retry

```
1. Developer → Code Validator
   Validation Request: Validate code (Attempt 1)

2. Code Validator → Developer
   Validation Result: FAIL - Missing error handling
   Feedback: "Add try-catch blocks for database operations"

3. Developer incorporates feedback

4. Developer → Code Validator
   Validation Request: Validate code (Attempt 2)

5. Code Validator → Developer
   Validation Result: FAIL - Security vulnerability
   Feedback: "Use parameterized queries to prevent SQL injection"

6. Developer incorporates feedback

7. Developer → Code Validator
   Validation Request: Validate code (Attempt 3)

8. Code Validator → Developer
   Validation Result: PASS
```

### Escalation Flow

```
1. Developer → Code Validator
   Validation Request (Attempt 1) → FAIL

2. Developer → Code Validator
   Validation Request (Attempt 2) → FAIL

3. Developer → Code Validator
   Validation Request (Attempt 3) → FAIL

4. System detects 3 consecutive failures

5. Orchestrator → Escalation Agent
   Escalation Request: Validation deadlock detected

6. Escalation Agent analyzes rejection pattern

7. Escalation Agent determines: Requires human intervention

8. Escalation Agent → Human Oversight
   Approval Request: Task requires technical review
```

## Monitoring A2A Messages

### View Pub/Sub Messages

```bash
# View topic
gcloud pubsub topics describe legacy-modernization-messages

# View subscriptions
gcloud pubsub subscriptions list

# Monitor message flow
gcloud pubsub subscriptions pull developer_agent-subscription --limit=10
```

### Track Agent Activity

```bash
# View agent logs in Cloud Logging
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit 50 \
  --format json

# Filter by agent
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine AND \
  jsonPayload.agent_name='developer_agent'"
```

## Best Practices

### 1. Always Use Helper Functions
```python
# ✅ Good - Use helper
A2AProtocolHelper.create_task_assignment(...)

# ❌ Bad - Manual message creation
A2AMessage(message_type=A2AMessageType.TASK_ASSIGNMENT, ...)
```

### 2. Track All Tasks
```python
# ✅ Good - Automatic tracking
@a2a.with_task_tracking
def my_tool(task_id: str, **kwargs):
    ...

# ❌ Bad - Manual state updates
def my_tool(task_id: str, **kwargs):
    a2a.send_task_update(task_id, "pending", "in_progress")
    # ... work ...
    a2a.send_task_update(task_id, "in_progress", "completed")
```

### 3. Use Validation Loop Handler
```python
# ✅ Good - Automatic retry and escalation
validation_handler.validate_with_retry(...)

# ❌ Bad - Manual retry logic
for i in range(3):
    result = validate(...)
    if result.passed:
        break
```

### 4. Report Errors Immediately
```python
# ✅ Good - Automatic error reporting
@a2a.with_task_tracking
def risky_operation(task_id: str):
    # Errors automatically reported
    raise Exception("Something failed")

# ❌ Bad - Silent failures
def risky_operation(task_id: str):
    try:
        ...
    except Exception:
        pass  # Error swallowed
```

## Troubleshooting

### Messages Not Delivered
1. Check subscription filters match agent IDs
2. Verify Pub/Sub topic exists
3. Check dead-letter queue for failed messages

### Validation Deadlocks
1. Review rejection history in escalation report
2. Check if feedback is actionable
3. Consider if validation criteria are too strict

### Agent Not Responding
1. Check agent is deployed and healthy
2. Verify agent is listening on subscription
3. Check agent logs for errors

## Next Steps

1. **Deploy to Vertex AI**: Use `deploy_vertex_agents.py`
2. **Load Legacy Code**: Use `load_legacy_knowledge.py`
3. **Run Pipeline**: Use `run_pipeline_with_a2a.py`
4. **Monitor**: Track messages and agent activity
5. **Iterate**: Refine agents based on performance

## Support

- See `README.md` for project overview
- See `examples/a2a_usage_example.py` for code examples
- Review agent implementations in `agents/` for patterns
