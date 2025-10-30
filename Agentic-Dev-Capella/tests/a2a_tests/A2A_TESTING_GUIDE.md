# A2A Protocol and GCP Testing Guide

Comprehensive testing guide for Agent-to-Agent (A2A) communication protocol and Google Cloud Platform (GCP) integrations in Agentic Dev Team Capella.

## Table of Contents

1. [Overview](#overview)
2. [Test Organization](#test-organization)
3. [Running Tests](#running-tests)
4. [Test Suites](#test-suites)
5. [GCP Integration Tests](#gcp-integration-tests)
6. [Writing New Tests](#writing-new-tests)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose

These tests validate the **A2A protocol** and **GCP integrations** that power multi-agent communication:

- **A2A Protocol**: Message types, serialization, factory methods
- **Google Cloud Pub/Sub**: Message routing, subscriptions, filtering
- **Validation Loops**: Retry logic, escalation, feedback incorporation
- **Multi-Agent Workflows**: End-to-end communication patterns
- **Vector Search**: Semantic code search with Vertex AI Matching Engine
- **Vertex AI Reasoning Engine**: Agent deployment and execution

### Test Philosophy

**Three Testing Tiers:**

1. **Unit Tests** (No GCP required):
   - A2A protocol message creation and serialization
   - Mock Pub/Sub message bus operations
   - Validation loop logic with mocked agents

2. **Integration Tests** (Require GCP project):
   - Real Pub/Sub message publishing and receiving
   - Real Vector Search queries
   - Real Vertex AI Reasoning Engine deployment

3. **Workflow Tests** (Mock-based):
   - Multi-agent communication patterns
   - Orchestrator → Developer → Validator workflows
   - Error reporting and escalation flows

---

## Test Organization

### Directory Structure

```
tests/
├── a2a_tests/                          # A2A protocol and workflow tests
│   ├── test_a2a_protocol.py           # Message types, serialization (470 lines)
│   ├── test_pubsub_integration.py     # Pub/Sub mock + integration (550 lines)
│   ├── test_validation_loop.py        # Validation retry/escalation (600 lines)
│   ├── test_multi_agent_workflows.py  # End-to-end workflows (550 lines)
│   └── A2A_TESTING_GUIDE.md           # This file
│
├── gcp_tests/                          # GCP service-specific tests
│   ├── test_vector_search.py          # Vector Search mock + integration (450 lines)
│   ├── test_vertex_ai_reasoning_engine.py  # Agent deployment (400 lines)
│   └── GCP_TESTING_GUIDE.md           # GCP testing guide
│
└── agent_tests/                        # Agent capability tests (existing)
    ├── test_backend_realworld.py      # Backend development scenarios
    ├── test_frontend_realworld.py     # Frontend development scenarios
    └── test_fullstack_integration.py  # Full-stack integration scenarios
```

### Test Count Summary

| Category | Test Files | Test Cases | Lines | GCP Required |
|----------|-----------|------------|-------|--------------|
| A2A Protocol | 1 | 30+ | 470 | No |
| Pub/Sub Mock | 1 | 8 | 300 | No |
| Pub/Sub Integration | 1 | 4 | 250 | Yes |
| Validation Loop | 1 | 15+ | 600 | No |
| Multi-Agent Workflows | 1 | 10+ | 550 | No |
| Vector Search Mock | 1 | 8 | 250 | No |
| Vector Search Integration | 1 | 2 | 200 | Yes |
| Vertex AI Mock | 1 | 10+ | 250 | No |
| Vertex AI Integration | 1 | 2 | 150 | Yes |
| **Total** | **9** | **90+** | **3,020** | **Mixed** |

---

## Running Tests

### Prerequisites

**For All Tests:**
```bash
# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-cov pytest-mock
```

**For GCP Integration Tests:**
```bash
# Set up Google Cloud authentication
gcloud auth application-default login

# Set environment variables
export GCP_PROJECT_ID=your-project-id
export STAGING_BUCKET=gs://your-project-staging
export VECTOR_SEARCH_ENDPOINT=projects/X/locations/Y/indexEndpoints/Z
```

### Quick Test Commands

**Run All A2A Tests (No GCP Required):**
```bash
# All A2A unit tests
pytest tests/a2a_tests/ -v

# Specific test file
pytest tests/a2a_tests/test_a2a_protocol.py -v

# Specific test class
pytest tests/a2a_tests/test_a2a_protocol.py::TestA2AProtocolHelper -v

# With coverage
pytest tests/a2a_tests/ --cov=shared.utils.vertex_a2a_protocol --cov-report=html
```

**Run GCP Integration Tests:**
```bash
# Set required environment variables first
export GCP_PROJECT_ID=your-project-id

# Run Pub/Sub integration tests
pytest tests/a2a_tests/test_pubsub_integration.py::TestVertexA2AMessageBusIntegration -v

# Run Vector Search integration tests
export VECTOR_SEARCH_ENDPOINT=your-endpoint-id
pytest tests/gcp_tests/test_vector_search.py::TestVectorSearchIntegration -v

# Run Vertex AI integration tests
export STAGING_BUCKET=gs://your-bucket
pytest tests/gcp_tests/test_vertex_ai_reasoning_engine.py::TestVertexAIReasoningEngineIntegration -v
```

**Run All Tests (Skip Integration if No GCP):**
```bash
# Runs all tests, skips integration tests if GCP_PROJECT_ID not set
pytest tests/a2a_tests/ tests/gcp_tests/ -v
```

---

## Test Suites

### 1. A2A Protocol Tests (`test_a2a_protocol.py`)

**Purpose**: Validate A2A message types, serialization, and factory methods.

**Test Classes:**

#### `TestA2AMessageType`
- All 10 message types exist
- Correct enum values (e.g., `TASK_ASSIGNMENT` = "task_assignment")

#### `TestA2AMessage`
- Message creation with all required fields
- Message serialization to dict and JSON
- Message deserialization from dict
- Round-trip serialization (dict → message → dict)
- Priority, retry_count, ttl_seconds handling
- Correlation ID propagation

#### `TestA2AProtocolHelper`
- `create_task_assignment()` - Orchestrator assigns work
- `create_validation_request()` - Request artifact validation
- `create_validation_result()` - Return pass/fail with feedback
- `create_escalation_request()` - Escalate after max retries
- `create_state_update()` - Update task state
- `create_error_report()` - Report errors with priority=1
- `create_query_request()` / `create_query_response()` - Inter-agent queries
- `create_task_completion()` - Report task completion

#### `TestA2AMessageValidation`
- Priority range (1-10)
- Retry count increments
- Timestamp ISO format

**Run:**
```bash
pytest tests/a2a_tests/test_a2a_protocol.py -v
```

---

### 2. Pub/Sub Integration Tests (`test_pubsub_integration.py`)

**Purpose**: Test Google Cloud Pub/Sub message bus for A2A communication.

**Test Classes:**

#### `TestVertexA2AMessageBusMock` (No GCP Required)
- Message bus initialization
- Message publishing with attributes
- Subscription creation with filters (`attributes.recipient_agent_id="{agent_id}"`)
- Message filtering by recipient
- Send-and-wait request-response pattern
- Error handling on publish failure
- Message retry logic

#### `TestVertexA2AMessageBusIntegration` (Requires GCP)
- End-to-end message publishing and receiving
- Message filtering across multiple agents
- Request-response with correlation IDs
- High-priority message delivery
- Real topic and subscription management
- Automatic cleanup after tests

**Run Mock Tests:**
```bash
pytest tests/a2a_tests/test_pubsub_integration.py::TestVertexA2AMessageBusMock -v
```

**Run Integration Tests (Requires GCP):**
```bash
export GCP_PROJECT_ID=your-project-id
pytest tests/a2a_tests/test_pubsub_integration.py::TestVertexA2AMessageBusIntegration -v
```

**What Integration Tests Do:**
1. Create temporary test topic (`test-a2a-messages-{random}`)
2. Register multiple agents with filtered subscriptions
3. Publish messages and verify routing
4. Test request-response patterns
5. Clean up topics and subscriptions

---

### 3. Validation Loop Tests (`test_validation_loop.py`)

**Purpose**: Test validation-retry-escalation workflow.

**Test Classes:**

#### `TestValidationLoopHandler`
- Validation success on first attempt
- Retry with feedback incorporation (up to 3 times)
- Escalation after max retries exceeded
- Timeout handling
- Validation criteria passed to validator
- Rejection history tracking
- Custom max_retries setting

#### `TestA2AIntegrationTaskTracking`
- `@with_task_tracking` decorator on success
- `@with_task_tracking` decorator on failure
- Manual task status updates
- Manual error reporting
- Validation request sending

**Run:**
```bash
pytest tests/a2a_tests/test_validation_loop.py -v
```

**Key Pattern Tested:**
```python
validation_handler = ValidationLoopHandler(
    a2a_integration=a2a,
    max_retries=3,
    escalation_agent_id=escalation_id
)

result = validation_handler.validate_with_retry(
    task_id="dev_001",
    validator_id=validator_id,
    validator_name="code_validator",
    artifact_generator=lambda feedback: generate_code_with_feedback(feedback),
    validation_criteria=["correctness", "security"]
)

# Returns: {"status": "validated" | "escalated", "attempts": N, ...}
```

---

### 4. Multi-Agent Workflow Tests (`test_multi_agent_workflows.py`)

**Purpose**: Test end-to-end multi-agent communication workflows.

**Test Classes:**

#### `TestMultiAgentWorkflows`
- Orchestrator → Developer task assignment
- Developer → Validator validation request
- Full workflow: Orchestrator → Developer → Validator → Developer → Orchestrator
- State update tracking during execution
- Error reporting workflow
- Query request-response between agents
- Escalation workflow after max retries

**Mock Agents Included:**
- `MockDeveloperAgent` - Generates code, requests validation
- `MockValidatorAgent` - Validates artifacts, returns feedback
- `MockOrchestratorAgent` - Assigns tasks, tracks completions

**Run:**
```bash
pytest tests/a2a_tests/test_multi_agent_workflows.py -v
```

**Example Workflow Tested:**
```
1. Orchestrator sends TASK_ASSIGNMENT → Developer
2. Developer receives task
3. Developer generates code
4. Developer sends VALIDATION_REQUEST → Validator
5. Validator validates code
6. Validator sends VALIDATION_RESULT → Developer (pass/fail + feedback)
7. If fail: Developer retries with feedback (up to 3 times)
8. If still failing: Developer sends ESCALATION_REQUEST → Escalation Agent
9. Developer sends TASK_COMPLETION → Orchestrator
```

---

### 5. Vector Search Tests (`test_vector_search.py`)

**Purpose**: Test Vertex AI Vector Search for semantic code search.

**Test Classes:**

#### `TestVectorSearchMock` (No GCP Required)
- Vector Search client initialization
- Embedding generation (768-dim)
- Semantic search query execution
- Filter by metadata
- Batch embedding generation

#### `TestVectorSearchIntegration` (Requires GCP)
- Generate embeddings with real API
- Semantic search with real endpoint

#### `TestUniversalVectorDBClient`
- Search similar implementations
- Search best practices
- Hybrid search (semantic + keyword)
- Result caching

#### `TestDynamicKnowledgeBaseIntegration`
- Dynamic query execution from agents
- Fallback to LLM when KB empty

**Run Mock Tests:**
```bash
pytest tests/gcp_tests/test_vector_search.py::TestVectorSearchMock -v
```

**Run Integration Tests (Requires GCP + Vector Search Endpoint):**
```bash
export GCP_PROJECT_ID=your-project-id
export VECTOR_SEARCH_ENDPOINT=projects/.../indexEndpoints/...
pytest tests/gcp_tests/test_vector_search.py::TestVectorSearchIntegration -v
```

---

### 6. Vertex AI Reasoning Engine Tests (`test_vertex_ai_reasoning_engine.py`)

**Purpose**: Test agent deployment and execution on Vertex AI.

**Test Classes:**

#### `TestVertexAIReasoningEngineMock` (No GCP Required)
- Agent deployment to Vertex AI
- Agent query execution
- Agent tool function execution
- Agent resource ID format validation
- Vertex AI initialization
- Deployment requirements specification

#### `TestVertexAIReasoningEngineIntegration` (Requires GCP)
- Deploy simple agent to real Vertex AI
- Query deployed agent
- List deployed Reasoning Engines
- Clean up deployed agents

#### `TestAgentFactory`
- Create agent from configuration
- Load agents from registry
- Batch agent deployment

#### `TestVertexAIGenerativeModels`
- Gemini model initialization
- Content generation
- Model selection by use case

**Run Mock Tests:**
```bash
pytest tests/gcp_tests/test_vertex_ai_reasoning_engine.py::TestVertexAIReasoningEngineMock -v
```

**Run Integration Tests (Requires GCP + Staging Bucket):**
```bash
export GCP_PROJECT_ID=your-project-id
export STAGING_BUCKET=gs://your-project-staging
pytest tests/gcp_tests/test_vertex_ai_reasoning_engine.py::TestVertexAIReasoningEngineIntegration -v
```

**Warning**: Integration tests deploy real agents to Vertex AI (incurs costs). Agents are automatically cleaned up after tests.

---

## GCP Integration Tests

### Setup Requirements

**1. Google Cloud Project:**
```bash
# Create project or use existing
gcloud projects create your-project-id

# Set active project
gcloud config set project your-project-id
```

**2. Enable Required APIs:**
```bash
# Pub/Sub
gcloud services enable pubsub.googleapis.com

# Vertex AI
gcloud services enable aiplatform.googleapis.com

# Cloud Storage
gcloud services enable storage.googleapis.com
```

**3. Authentication:**
```bash
# Application Default Credentials
gcloud auth application-default login

# Verify authentication
gcloud auth list
```

**4. Create Resources:**
```bash
# Create staging bucket for Vertex AI
gsutil mb -l us-central1 gs://your-project-staging

# Create Vector Search index (optional, for Vector Search tests)
# Follow: https://cloud.google.com/vertex-ai/docs/vector-search/create-manage-index
```

**5. Set Environment Variables:**
```bash
# Required for all integration tests
export GCP_PROJECT_ID=your-project-id

# Required for Vertex AI tests
export STAGING_BUCKET=gs://your-project-staging

# Required for Vector Search tests
export VECTOR_SEARCH_ENDPOINT=projects/X/locations/Y/indexEndpoints/Z
```

### Running Integration Tests

**Run All Integration Tests:**
```bash
# Ensure environment variables are set
export GCP_PROJECT_ID=your-project-id
export STAGING_BUCKET=gs://your-project-staging

# Run all integration tests (will skip if env vars not set)
pytest tests/a2a_tests/ tests/gcp_tests/ -v -m integration
```

**Run Specific Integration Test:**
```bash
# Pub/Sub integration
pytest tests/a2a_tests/test_pubsub_integration.py::TestVertexA2AMessageBusIntegration::test_publish_and_receive_message -v

# Vector Search integration
pytest tests/gcp_tests/test_vector_search.py::TestVectorSearchIntegration::test_generate_embeddings_real -v

# Vertex AI integration
pytest tests/gcp_tests/test_vertex_ai_reasoning_engine.py::TestVertexAIReasoningEngineIntegration::test_deploy_simple_agent_real -v
```

### Cost Considerations

**Integration tests incur GCP costs:**

- **Pub/Sub**: ~$0.40 per million messages (tests send < 100 messages)
- **Vertex AI Vector Search**: ~$0.50/hour per node (tests query existing endpoint)
- **Vertex AI Reasoning Engine**: ~$0.001 per 1K characters generated
- **Cloud Storage**: Negligible (staging bucket)

**Estimated cost per test run**: < $0.10

**To minimize costs:**
- Run integration tests only when needed (e.g., before deployment)
- Use separate test project
- Clean up resources after testing (done automatically)

---

## Writing New Tests

### Adding A2A Protocol Tests

**Example: Test new message type**

```python
# In tests/a2a_tests/test_a2a_protocol.py

def test_create_new_message_type(self):
    """Test creating NEW_MESSAGE_TYPE."""
    message = A2AProtocolHelper.create_new_message(
        sender_id=self.sender_id,
        sender_name="agent1",
        recipient_id=self.recipient_id,
        recipient_name="agent2",
        custom_data={"key": "value"}
    )

    self.assertEqual(message.message_type, A2AMessageType.NEW_MESSAGE_TYPE)
    self.assertEqual(message.payload["custom_data"]["key"], "value")
```

### Adding Pub/Sub Tests

**Example: Test new message routing pattern**

```python
# In tests/a2a_tests/test_pubsub_integration.py

def test_broadcast_message(self):
    """Test broadcasting message to multiple agents."""
    agents = ["agent1", "agent2", "agent3"]
    received_by = []

    def message_handler(agent_id):
        def handler(message):
            received_by.append(agent_id)
        return handler

    # Register all agents
    for agent_id in agents:
        self.message_bus.register_agent(agent_id, f"{agent_id}_name", message_handler(agent_id))

    # Broadcast message
    # (Implementation depends on broadcast pattern)

    # Verify all received
    self.assertEqual(len(received_by), len(agents))
```

### Adding Validation Loop Tests

**Example: Test new retry strategy**

```python
# In tests/a2a_tests/test_validation_loop.py

def test_exponential_backoff_retry(self):
    """Test validation retry with exponential backoff."""
    # Mock validator that fails first 2 attempts
    attempts = []

    def artifact_generator(feedback=None):
        attempts.append(time.time())
        if len(attempts) < 3:
            return {"code": "incomplete"}
        return {"code": "complete"}

    # Custom validation handler with backoff
    # (Implementation details)

    result = validation_handler.validate_with_retry(...)

    # Verify exponential backoff timing
    if len(attempts) >= 3:
        delay1 = attempts[1] - attempts[0]
        delay2 = attempts[2] - attempts[1]
        self.assertGreater(delay2, delay1 * 1.5)  # Exponential increase
```

### Adding Multi-Agent Workflow Tests

**Example: Test new agent collaboration pattern**

```python
# In tests/a2a_tests/test_multi_agent_workflows.py

def test_parallel_task_execution(self):
    """Test multiple agents working in parallel."""
    tasks = [
        {"task_id": "task1", "agent": "agent1"},
        {"task_id": "task2", "agent": "agent2"},
        {"task_id": "task3", "agent": "agent3"}
    ]

    completed_tasks = []

    # Assign tasks in parallel
    for task in tasks:
        # Orchestrator assigns task
        # Agent processes task
        # Track completion
        completed_tasks.append(task["task_id"])

    # Verify all completed
    self.assertEqual(len(completed_tasks), len(tasks))
```

---

## Troubleshooting

### Common Issues

**1. Import Errors**
```
ModuleNotFoundError: No module named 'shared.utils.vertex_a2a_protocol'
```
**Fix**:
```bash
# Ensure project root is in Python path
export PYTHONPATH=/path/to/Agentic-Dev-Capella:$PYTHONPATH

# Or run from project root
cd /path/to/Agentic-Dev-Capella
pytest tests/a2a_tests/ -v
```

**2. GCP Authentication Errors**
```
DefaultCredentialsError: Could not automatically determine credentials
```
**Fix**:
```bash
gcloud auth application-default login
```

**3. Pub/Sub Permission Errors**
```
PermissionDenied: 403 User not authorized
```
**Fix**:
```bash
# Grant Pub/Sub permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:YOUR_EMAIL" \
    --role="roles/pubsub.editor"
```

**4. Integration Tests Skipped**
```
SKIPPED [1] test_pubsub_integration.py:250: Skipping integration tests - set GCP_PROJECT_ID
```
**Expected**: Integration tests skip if `GCP_PROJECT_ID` not set. This is normal.

**To run**:
```bash
export GCP_PROJECT_ID=your-project-id
pytest tests/a2a_tests/test_pubsub_integration.py::TestVertexA2AMessageBusIntegration -v
```

**5. Vector Search Endpoint Not Found**
```
SkipTest: Vector Search endpoint not ready
```
**Fix**: Ensure Vector Search index is created and endpoint is deployed. Set `VECTOR_SEARCH_ENDPOINT` environment variable.

**6. Vertex AI Deployment Failures**
```
SkipTest: Deployment failed: Staging bucket not accessible
```
**Fix**:
```bash
# Ensure staging bucket exists
gsutil mb -l us-central1 gs://your-project-staging

# Grant access
gsutil iam ch user:YOUR_EMAIL:objectAdmin gs://your-project-staging
```

---

## Best Practices

### 1. Test Independence

Each test should be independent:
- Don't rely on test execution order
- Clean up resources after each test
- Use unique IDs for test data

### 2. Mock by Default, Integrate When Needed

- Write mock tests for fast feedback
- Use integration tests for pre-deployment validation
- Don't run integration tests in CI/CD unless necessary

### 3. Clear Test Names

```python
# Good
def test_validation_retry_with_feedback_incorporation(self):

# Bad
def test_validation(self):
```

### 4. Comprehensive Assertions

```python
# Good
self.assertEqual(result["status"], "validated")
self.assertEqual(result["attempts"], 2)
self.assertTrue(result["validation_passed"])
self.assertEqual(len(result["issues"]), 0)

# Insufficient
self.assertTrue(result["validation_passed"])
```

### 5. Use Fixtures for Common Setup

```python
@pytest.fixture
def message_bus():
    """Provide mocked message bus for all tests."""
    return MagicMock()

def test_something(message_bus):
    # Use message_bus fixture
    pass
```

---

## Summary

This testing framework provides **comprehensive coverage** for A2A protocol and GCP integrations:

**90+ test cases** across 9 test files
**3,020+ lines** of test code
**Unit tests** (no GCP required) for fast feedback
**Integration tests** (with GCP) for production validation
**Mock agents** for workflow testing
**Automatic cleanup** of test resources
**Clear documentation** with examples

**Ready to ensure A2A communication and GCP integrations work flawlessly!**
