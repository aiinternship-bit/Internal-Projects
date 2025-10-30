# Real-World Agent Testing Guide

This guide covers the comprehensive real-world testing framework for **Agentic Dev Team Capella** agents. These tests validate standalone development capabilities **without requiring a legacy knowledge base**, focusing on greenfield software development scenarios.

## Table of Contents

1. [Overview](#overview)
2. [Test Suites](#test-suites)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Writing New Tests](#writing-new-tests)
6. [Test Results](#test-results)

---

## Overview

### Purpose

The real-world test suites validate that agents can:
- **Build complete applications from scratch** (no legacy context required)
- **Handle modern development scenarios** (e-commerce, social media, IoT, etc.)
- **Generate production-quality code** (with tests, documentation, best practices)
- **Coordinate across multiple agents** (full-stack integration)

### Test Philosophy

**Two-Tier Testing (from existing framework):**
1. **Mock Tests**: Fast tests calling agent tool functions directly
2. **LLM Tests**: End-to-end tests with real LLM calls

**New: Real-World Tests**:
3. **Real-World Scenario Tests**: Complex, realistic development scenarios without legacy context
4. **Integration Tests**: Multi-agent coordination for full-stack applications

---

## Test Suites

### 1. Backend Development Tests
**File**: `tests/agent_tests/test_backend_realworld.py`

Tests standalone backend development capabilities.

#### API Developer Tests (5 scenarios)
- **E-commerce REST API**: FastAPI + PostgreSQL product catalog with CRUD
- **Social Media GraphQL API**: Apollo + TypeScript for posts, comments, likes
- **Payment gRPC Service**: Go-based gRPC microservice with Stripe integration
- **Webhook Handler**: Flask API for Stripe, GitHub, Slack webhooks
- **Real-time Chat API**: Express + Socket.io with WebSocket support

#### Database Engineer Tests (5 scenarios)
- **E-commerce Schema**: PostgreSQL schema for 10M users, 1M products
- **SaaS Multi-Tenant**: Schema-per-tenant architecture with RLS
- **IoT Time-Series**: TimescaleDB for sensor data with hypertables
- **Social Network NoSQL**: MongoDB schema for 100M users with sharding
- **Data Warehouse**: BigQuery star schema for analytics

#### Microservices Architect Tests (5 scenarios)
- **Food Delivery Platform**: Uber Eats-style microservices (order, delivery, payment)
- **E-Learning Platform**: Course platform with video streaming, CQRS, event sourcing
- **Digital Banking**: PCI-DSS compliant microservices with Saga pattern
- **Healthcare (HIPAA)**: Telemedicine platform with FHIR and compliance
- **Gaming Platform**: Multiplayer gaming with matchmaking, real-time state sync

**Run Backend Tests:**
```bash
# Test all backend agents
python tests/agent_tests/test_backend_realworld.py --agent all

# Test specific agent
python tests/agent_tests/test_backend_realworld.py --agent api_developer_agent
python tests/agent_tests/test_backend_realworld.py --agent database_engineer_agent
python tests/agent_tests/test_backend_realworld.py --agent microservices_architect_agent
```

---

### 2. Frontend Development Tests
**File**: `tests/agent_tests/test_frontend_realworld.py`

Tests standalone UI and frontend development capabilities.

#### UI Developer Tests (5 scenarios)
- **Analytics Dashboard**: React + Tailwind dashboard with charts, tables, filters
- **E-commerce Product Grid**: Product listing with filters, cart, state management
- **Authentication Flow**: Login, signup, forgot password, reset password
- **Real-time Chat Interface**: WebSocket chat with typing indicators
- **Data Visualization Dashboard**: Interactive charts with Recharts

#### React Specialist Tests (5 scenarios)
- **Multi-Step Form Wizard**: Wizard with validation, Context API, custom hooks
- **Infinite Scroll Feed**: Virtualized feed with react-window and react-query
- **Drag-and-Drop Kanban**: Kanban board with react-beautiful-dnd and Redux
- **Collaborative Editor**: Real-time Slate editor with WebSocket sync
- **Advanced Data Grid**: AG Grid with server-side pagination, sorting, filtering

#### CSS Specialist Tests (5 scenarios)
- **Responsive Landing Page**: Modern landing with animations, dark mode
- **Magazine CSS Grid Layout**: Complex grid with masonry, sticky sidebar
- **Animation Library**: Reusable CSS animations and transitions
- **Dark Mode Theme System**: CSS variables with system preference detection
- **Glassmorphism Components**: Modern glass UI with backdrop filters

#### Accessibility Specialist Tests (5 scenarios)
- **WCAG 2.1 AA E-commerce**: Make product listing fully accessible
- **Accessible Multi-Step Form**: Form with ARIA live regions, keyboard nav
- **Accessible Data Table**: Table with sorting announcements, keyboard nav
- **Accessible Modals**: Focus trap, escape to close, ARIA modal
- **Accessible Video Player**: Video with captions, transcripts, keyboard controls

**Run Frontend Tests:**
```bash
# Test all frontend agents
python tests/agent_tests/test_frontend_realworld.py --agent all

# Test specific agent
python tests/agent_tests/test_frontend_realworld.py --agent ui_developer_agent
python tests/agent_tests/test_frontend_realworld.py --agent react_specialist_agent
python tests/agent_tests/test_frontend_realworld.py --agent css_specialist_agent
python tests/agent_tests/test_frontend_realworld.py --agent accessibility_specialist_agent
```

---

### 3. Full-Stack Integration Tests
**File**: `tests/agent_tests/test_fullstack_integration.py`

Tests multi-agent coordination for complete applications.

#### Full-Stack Applications (3 scenarios)
- **Todo App**: React + FastAPI + PostgreSQL with JWT auth
- **Blog Platform**: React + Express + PostgreSQL with markdown editor
- **E-commerce Store**: React + FastAPI + PostgreSQL + Stripe payments

#### Real-Time Applications (3 scenarios)
- **Chat Application**: WebSocket chat with Socket.io + Redis
- **Collaborative Whiteboard**: Real-time drawing with Fabric.js sync
- **Live Polling**: Real-time voting with WebSocket result updates

#### Dashboards (2 scenarios)
- **Analytics Dashboard**: Business metrics with time-series charts
- **IoT Monitoring**: Real-time sensor data with MQTT

#### Social Platforms (1 scenario)
- **Social Network**: Feed, posts, comments, likes, follows

#### Auth Systems (1 scenario)
- **Multi-Tenant SaaS Auth**: Organizations, teams, RBAC, OAuth

**Run Integration Tests:**
```bash
# Test all integration scenarios
python tests/agent_tests/test_fullstack_integration.py --suite all

# Test specific suite
python tests/agent_tests/test_fullstack_integration.py --suite todo
python tests/agent_tests/test_fullstack_integration.py --suite realtime
python tests/agent_tests/test_fullstack_integration.py --suite dashboard
python tests/agent_tests/test_fullstack_integration.py --suite social
python tests/agent_tests/test_fullstack_integration.py --suite auth
```

---

## Test Coverage

### Total Test Scenarios

| Test Suite | Scenarios | Agents Tested |
|------------|-----------|---------------|
| Backend | 15 | API Developer, Database Engineer, Microservices Architect |
| Frontend | 20 | UI Developer, React Specialist, CSS Specialist, Accessibility |
| Integration | 10 | Multi-agent orchestration |
| **Total** | **45** | **7 agents** |

### Real-World Use Cases Covered

**Industries:**
- E-commerce (product catalogs, payments, inventory)
- Social Media (feeds, posts, chat, notifications)
- Healthcare (telemedicine, HIPAA compliance, FHIR)
- Finance (banking, payments, fraud detection, PCI-DSS)
- Education (e-learning, video streaming, certifications)
- Gaming (multiplayer, matchmaking, real-time sync)
- IoT (sensor data, telemetry, monitoring)
- SaaS (multi-tenancy, RBAC, organizations)

**Technical Patterns:**
- REST APIs, GraphQL, gRPC
- WebSocket real-time communication
- Multi-tenancy (schema-per-tenant, shared schema)
- Time-series data (TimescaleDB, hypertables)
- Microservices (CQRS, Event Sourcing, Saga pattern)
- Authentication (JWT, OAuth, 2FA)
- WCAG 2.1 AA/AAA accessibility
- Dark mode and theming
- Infinite scroll and virtualization
- Drag-and-drop interactions

---

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# For LLM tests (requires Google Cloud):
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
gcloud auth application-default login
```

### Quick Test Commands

```bash
# Backend tests
python tests/agent_tests/test_backend_realworld.py --agent all

# Frontend tests
python tests/agent_tests/test_frontend_realworld.py --agent all

# Integration tests
python tests/agent_tests/test_fullstack_integration.py --suite all

# Don't save results (for quick testing)
python tests/agent_tests/test_backend_realworld.py --agent api_developer_agent --no-save
```

### Test Modes

**1. Mock Mode (Fast - No API Calls)**
Tests call agent tool functions directly with mock data.

```bash
# Uses existing mock test framework
python scripts/test_agents_with_mocks.py
```

**2. LLM Mode (Slow - Real API Calls)**
Tests use real LLM calls via `agent.query(prompt)`.

```bash
# Requires Google Cloud credentials
python scripts/test_agents_with_llm.py --agent all
```

**3. Real-World Mode (New - Comprehensive Scenarios)**
Tests validate agents on complex, realistic scenarios.

```bash
# New real-world test suites
python tests/agent_tests/test_backend_realworld.py --agent all
python tests/agent_tests/test_frontend_realworld.py --agent all
python tests/agent_tests/test_fullstack_integration.py --suite all
```

---

## Test Results

### Result Files

Test results are saved to `tests/agent_tests/results/`:

```
tests/agent_tests/results/
├── api_developer_agent_realworld_results.json
├── database_engineer_agent_realworld_results.json
├── microservices_architect_agent_realworld_results.json
├── ui_developer_agent_realworld_results.json
├── react_specialist_agent_realworld_results.json
├── css_specialist_agent_realworld_results.json
├── accessibility_specialist_agent_realworld_results.json
├── fullstack_orchestrator_integration_results.json
├── realtime_orchestrator_integration_results.json
└── dashboard_orchestrator_integration_results.json
```

### Result Format

Each result file contains:
- Test case details (ID, name, description, input)
- Test execution results (status, output, execution time)
- Validation results (pass/fail, checks performed)
- Error messages (if any)

**Example:**
```json
{
  "agent_name": "api_developer_agent",
  "timestamp": "2025-10-30T10:30:00Z",
  "test_results": [
    {
      "test_case": {
        "test_id": "api_001",
        "test_name": "E-commerce REST API - From Scratch",
        "input_prompt": "Build a REST API for e-commerce product catalog"
      },
      "status": "passed",
      "execution_time_seconds": 12.5,
      "validation_details": {
        "valid": true,
        "checks": [...]
      }
    }
  ]
}
```

### Viewing Results

Use the existing result viewer:

```bash
python scripts/view_test_results.py tests/agent_tests/results/
```

---

## Writing New Tests

### Adding a New Test Scenario

**Example: Add a "Build Notification Service" test to API Developer**

```python
# In tests/agent_tests/test_backend_realworld.py

def create_api_developer_tests() -> AgentTestSuite:
    suite = AgentTestSuite("api_developer_agent")

    # ... existing tests ...

    # NEW TEST
    suite.add_test(
        test_id="api_006",
        test_name="Notification Service API",
        description="Build notification service with email, SMS, and push",
        input_prompt="Create a notification service API with multiple channels",
        input_data={
            "language": "python",
            "framework": "fastapi",
            "channels": ["email", "sms", "push", "webhook"],
            "features": [
                "template_management",
                "scheduling",
                "retry_logic",
                "delivery_tracking"
            ],
            "integrations": {
                "email": "sendgrid",
                "sms": "twilio",
                "push": "firebase"
            }
        },
        expected_status="success",
        expected_fields=["code", "api_endpoints", "integrations"],
        validation_function=lambda r: {
            "valid": (
                "sendgrid" in r.get("code", "").lower() and
                "twilio" in r.get("code", "").lower() and
                len(r.get("api_endpoints", [])) >= 4
            ),
            "details": "Should include email and SMS integrations"
        }
    )

    return suite
```

### Test Case Structure

Every test case needs:

1. **test_id**: Unique identifier (e.g., "api_001")
2. **test_name**: Human-readable name
3. **description**: What the test validates
4. **input_prompt**: Natural language description
5. **input_data**: Parameters for the agent tool
6. **expected_status**: Expected result status ("success", "error", etc.)
7. **expected_fields**: Required fields in the result
8. **validation_function**: Custom validation logic (lambda or function)

### Validation Functions

**Simple field checks:**
```python
expected_fields=["code", "schema", "tests"]
```

**Custom validation:**
```python
validation_function=lambda r: {
    "valid": (
        "FastAPI" in r.get("code", "") and
        len(r.get("endpoints", [])) >= 5 and
        "pytest" in r.get("tests", "")
    ),
    "details": "Should use FastAPI with 5+ endpoints and pytest"
}
```

**Complex validation with helper:**
```python
from tests.agent_tests.agent_test_framework import create_validation_function

validation_function=create_validation_function(
    min_length=100,  # Code must be > 100 chars
    required_keys=["code", "tests", "docs"],
    custom_checks=[
        lambda r: "async def" in r.get("code", ""),
        lambda r: len(r.get("endpoints", [])) >= 3
    ]
)
```

---

## Best Practices

### 1. Test Naming Conventions

- **Test IDs**: `{category}_{number}` (e.g., "api_001", "db_002")
- **Test Names**: Descriptive, indicates scenario (e.g., "E-commerce REST API - From Scratch")
- **Descriptions**: Explain what capability is being tested

### 2. Input Data Design

Make input data realistic and comprehensive:

```python
# GOOD: Realistic e-commerce scenario
input_data={
    "language": "python",
    "framework": "fastapi",
    "endpoints": [
        {"path": "/products", "methods": ["GET", "POST"]},
        {"path": "/products/{id}", "methods": ["GET", "PUT", "DELETE"]}
    ],
    "database": "postgresql",
    "authentication": "JWT",
    "include_tests": True,
    "include_openapi": True
}

# BAD: Too vague
input_data={
    "type": "api",
    "language": "python"
}
```

### 3. Validation Coverage

Test multiple aspects:

```python
validation_function=lambda r: {
    "valid": (
        # Code quality
        "from fastapi import" in r.get("code", "") and
        "@app.get" in r.get("code", "") and

        # Completeness
        len(r.get("endpoints", [])) >= 4 and

        # Best practices
        "pytest" in r.get("tests", "") and
        "openapi" in r.get("openapi_spec", {}) and

        # Documentation
        len(r.get("documentation", "")) > 0
    ),
    "details": "Should include FastAPI code, 4+ endpoints, tests, OpenAPI spec, and docs"
}
```

### 4. Test Independence

Each test should be independent:
- Don't rely on previous test results
- Use fresh input data
- Clean up any state if needed

### 5. Realistic Scenarios

Base tests on real-world applications:
- Study existing products (Uber Eats, Airbnb, Slack)
- Include realistic scale (1M users, 100K requests/day)
- Cover edge cases and error handling
- Include compliance requirements (HIPAA, PCI-DSS, GDPR)

---

## Troubleshooting

### Common Issues

**1. Agent Import Errors**
```
Error: No module named 'agents.backend.api_developer'
```
**Fix**: Ensure Phase 2 agents are implemented in `agents/backend/`, `agents/frontend/`, etc.

**2. Test Failures**
```
✗ TEST FAILED - Missing expected field: 'openapi_spec'
```
**Fix**: Update validation to match actual agent output structure, or fix agent implementation.

**3. Timeout Errors**
```
Test timeout after 30 seconds
```
**Fix**: Increase timeout in test case:
```python
suite.add_test(
    ...
    timeout_seconds=60  # Increase for complex tests
)
```

**4. Google Cloud Auth Errors**
```
Error: Application Default Credentials not found
```
**Fix**:
```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project-id
```

---

## Future Enhancements

### Planned Additions

1. **Infrastructure Tests**: Kubernetes, Terraform, CI/CD pipelines
2. **Performance Tests**: Load testing, stress testing, benchmarking
3. **Security Tests**: Penetration testing, vulnerability scanning
4. **Quality Tests**: Code complexity, test coverage, security scanning
5. **Multimodal Tests**: Image-to-code, PDF requirements, video analysis

### Contributing

To add new test scenarios:

1. Identify a real-world use case not yet covered
2. Create test case following the structure above
3. Add to appropriate test suite file
4. Run tests to validate
5. Document in this guide

---

## Summary

The real-world testing framework provides:

**45 comprehensive test scenarios** across backend, frontend, and full-stack
**Zero knowledge base dependency** - all tests are greenfield development
**Industry coverage** - e-commerce, social media, healthcare, finance, gaming, IoT, SaaS
**Technical depth** - REST, GraphQL, gRPC, WebSocket, microservices, accessibility
**Production-ready** - tests validate code quality, best practices, compliance
**Easy to extend** - add new scenarios following established patterns

This framework ensures that Agentic Dev Team Capella agents can **build modern, production-quality applications from scratch**.
