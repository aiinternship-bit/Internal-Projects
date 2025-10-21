# Legacy Code Modernization - Agentic Pipeline

An autonomous, multi-agent system for re-engineering legacy codebases into modern architectures using Google ADK.

## Overview

This system employs a three-stage pipeline to modernize legacy systems (e.g., COBOL on Oracle DB) into modern implementations (e.g., Python/C++ with TypeScript/React) while preserving business logic and ensuring functional parity.

### Architecture Stages

1. **Stage 0-1: Discovery & ETL (Knowledge Assembly)**
   - Asset discovery and inventory
   - Static analysis and documentation mining
   - Knowledge graph construction

2. **Stage 2: Development Team**
   - Architecture design and validation
   - Code development with embedded validation
   - Comprehensive testing (functional, regression, security)

3. **Stage 3: CI/CD & Operations**
   - Automated deployment with progressive rollout
   - Continuous monitoring and root cause analysis
   - Supply chain security

## Project Structure

```
legacy-modernization-system/
├── agents/                    # All agent implementations
│   ├── orchestration/         # Central coordination
│   ├── stage0_discovery/      # Asset discovery
│   ├── stage1_etl/           # Knowledge assembly
│   ├── stage2_development/    # Development team
│   └── stage3_cicd/          # CI/CD & operations
├── shared/                    # Shared utilities
│   ├── tools/                 # Reusable tools
│   ├── models/                # Data models
│   └── utils/                 # Utilities
├── config/                    # Configuration files
├── tests/                     # Test suite
└── scripts/                   # Utility scripts
```

## Installation

### Prerequisites

- Python 3.10+
- Google Cloud SDK
- Google ADK
- Access to Google AI models (Gemini)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd legacy-modernization-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google ADK**
   ```bash
   # Set up Google Cloud credentials
   gcloud auth application-default login
   
   # Set project ID
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

5. **Configure agents**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Initialize Vector DB** (Optional - for production)
   ```bash
   # Install and configure your chosen vector DB
   # Options: Chroma, Pinecone, Weaviate
   ```

## Usage

### Basic Usage

Run the complete pipeline:

```bash
python scripts/run_pipeline.py \
  --legacy-repo /path/to/legacy/code \
  --output ./modernized_output \
  --config config/agents_config.yaml
```

### Run Specific Stages

```bash
# Run only discovery stage
python scripts/run_pipeline.py \
  --legacy-repo /path/to/legacy/code \
  --stage discovery

# Run only development stage
python scripts/run_pipeline.py \
  --legacy-repo /path/to/legacy/code \
  --stage development
```

### Configuration

Edit `config/agents_config.yaml` to customize:
- Agent models and parameters
- Validation thresholds
- Deployment strategies
- Tool configurations

## Agent Communication

Agents communicate through a central message bus coordinated by the Orchestrator Agent. Key patterns:

1. **Task Assignment**: Orchestrator assigns work to agents
2. **Validation**: Validators review and approve/reject work
3. **Escalation**: Failed validations escalate after 3 attempts
4. **State Updates**: All agents report state changes

Example message flow:
```
Orchestrator → Developer Agent (task assignment)
Developer Agent → Code Validator (code submission)
Code Validator → Orchestrator (validation result)
Orchestrator → QA Agent (next stage)
```

## Key Components

### Orchestrator Agent
Central coordinator managing:
- Task routing and prioritization
- Deadlock detection
- Hierarchical task assignment (Infrastructure → Backend → Integration → UI)

### Vector DB Interface
Knowledge store containing:
- Code embeddings for semantic search
- Business logic mappings
- Dependency graphs
- Database schemas and stored procedures
- NFR metadata (performance, security requirements)
- Cross-cutting concerns

### Validation Gates
Multiple validation layers ensure quality:
- Architecture Validator: Design completeness and feasibility
- Code Validator: Functional correctness and security
- Quality Attribute Agent: Style and maintainability
- Build Validator: Compilation and test success
- QA Validator: Test coverage and completeness
- Integration Validator: End-to-end functional parity

## Development

### Adding a New Agent

1. **Create agent directory**
   ```bash
   mkdir -p agents/stage2_development/my_agent
   cd agents/stage2_development/my_agent
   ```

2. **Create agent.py**
   ```python
   from google.adk.agents import Agent

   def my_tool(param: str) -> dict:
       """Tool function for the agent."""
       return {"status": "success", "result": param}

   my_agent = Agent(
       name="my_agent",
       model="gemini-2.0-flash",
       description="Agent description",
       instruction="Agent instructions...",
       tools=[my_tool]
   )
   ```

3. **Create __init__.py**
   ```python
   from .agent import my_agent
   ```

4. **Register in agents/__init__.py**
   ```python
   from .stage2_development.my_agent.agent import my_agent
   # Add to registry in _register_all_agents()
   ```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/unit/test_orchestrator.py

# Run with coverage
pytest --cov=agents tests/
```

### Code Style

This project follows PEP 8 guidelines:
```bash
# Format code
black agents/ shared/ scripts/

# Check style
flake8 agents/ shared/ scripts/

# Type checking
mypy agents/ shared/ scripts/
```

## Configuration Reference

### Agent Configuration (`config/agents_config.yaml`)

Key sections:
- **global**: System-wide settings (model, retries, timeout)
- **orchestration**: Orchestrator, escalation, telemetry agents
- **stage0-3**: Stage-specific agent configurations
- **vector_db**: Vector database connection settings

### Validation Rules (`config/validation_rules.yaml`)

Define validation criteria:
- Code quality thresholds
- Test coverage requirements
- Security scan parameters
- Performance benchmarks

## Monitoring & Observability

### Telemetry

All agent actions are logged:
```python
from shared.utils.agent_communication import create_state_update_message

# Agents automatically log state changes
message = create_state_update_message(
    sender="developer_agent",
    task_id="task_123",
    old_status="in_progress",
    new_status="completed"
)
```

### Audit Trail

Complete traceability from legacy code to modernized implementation:
- Every agent action logged
- Decision rationale captured
- Human approvals recorded
- Validation feedback preserved

### Metrics

Key metrics tracked:
- **Functional Parity**: 100% business logic preserved (target)
- **Quality Gates**: <5% rejection rate (target)
- **Performance**: New system meets/exceeds legacy baseline
- **Deployment Success**: >95% without rollback (target)
- **Human Intervention**: <10% of tasks require escalation (target)

## Troubleshooting

### Common Issues

**Issue**: Agent fails to connect to Vector DB
```bash
# Solution: Check Vector DB configuration
cat config/vector_db_config.yaml
# Verify connection settings and restart Vector DB
```

**Issue**: Validation deadlock (>3 rejections)
```bash
# The system automatically escalates to escalation_agent
# Check logs for escalation details:
tail -f logs/escalation.log
```

**Issue**: Missing Google Cloud credentials
```bash
# Solution: Re-authenticate
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Debug Mode

Run with debug logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/run_pipeline.py --legacy-repo /path/to/code
```

### Health Check

Verify system health:
```bash
python scripts/health_check.py
```

## Production Deployment

### Prerequisites

1. **Vector Database**: Set up production Vector DB (Pinecone/Weaviate)
2. **Message Queue**: Configure RabbitMQ/Kafka for message bus
3. **Monitoring**: Set up Prometheus + Grafana
4. **Secrets**: Store credentials in Google Secret Manager

### Deployment Steps

1. **Deploy Vector DB**
   ```bash
   # Example: Deploy Weaviate on GKE
   kubectl apply -f kubernetes/vector-db.yaml
   ```

2. **Configure Message Bus**
   ```bash
   # Set up Pub/Sub topics
   gcloud pubsub topics create agent-messages
   gcloud pubsub subscriptions create orchestrator-sub --topic=agent-messages
   ```

3. **Deploy Agents**
   ```bash
   # Deploy as Cloud Run services or GKE pods
   gcloud run deploy orchestrator-agent \
     --image gcr.io/PROJECT/orchestrator:latest \
     --region us-central1
   ```

4. **Set up Monitoring**
   ```bash
   # Deploy monitoring stack
   kubectl apply -f kubernetes/monitoring/
   ```

### Scaling

- **Horizontal Scaling**: Deploy multiple instances of each agent
- **Vertical Scaling**: Increase memory/CPU for resource-intensive agents
- **Async Processing**: Use message queues for non-blocking communication

## Security

### Best Practices

1. **Credentials**: Never commit credentials to version control
2. **API Keys**: Store in Google Secret Manager
3. **Network**: Use VPC for agent communication
4. **Access Control**: Implement IAM roles for agents
5. **Audit**: Enable comprehensive audit logging
6. **Supply Chain**: Use Supply Chain Security Agent for dependency scanning

### Compliance

- **PCI DSS**: For payment processing components
- **GDPR**: Data anonymization for production data testing
- **SOC 2**: Complete audit trail maintained
- **HIPAA**: PHI handling if healthcare data present

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write comprehensive tests for all agents
- Follow existing code structure and patterns
- Document all tools and functions
- Update configuration files as needed
- Add examples for new functionality

## Architecture Decisions

### Why Google ADK?

- Native integration with Gemini models
- Built-in tool/function calling support
- Production-ready infrastructure
- Strong typing and validation

### Why Multi-Agent Architecture?

- **Separation of Concerns**: Each agent has a specific responsibility
- **Parallel Processing**: Multiple components modernized simultaneously
- **Fault Isolation**: Agent failures don't crash the entire system
- **Scalability**: Individual agents can be scaled independently
- **Validation Gates**: Multiple checkpoints ensure quality

### Why Three-Stage Pipeline?

1. **Stage 0-1**: Ensures complete understanding before modernization
2. **Stage 2**: Separates design from implementation with validation
3. **Stage 3**: Automated deployment with safety checks

## FAQ

**Q: Can I use this with non-COBOL legacy code?**
A: Yes! The system supports multiple languages. Configure file extensions in `config/agents_config.yaml`.

**Q: How long does modernization take?**
A: Depends on codebase size. Typical range: small (days), medium (weeks), large (months).

**Q: Can I modernize incrementally?**
A: Yes! The hierarchical task assignment enables component-by-component modernization.

**Q: What if the legacy system changes during modernization?**
A: Delta Monitoring Agent tracks changes and updates the Vector DB automatically.

**Q: Is human approval required?**
A: Configurable. Critical decisions (architecture, production deployment) require approval by default.

**Q: How is functional parity verified?**
A: Integration Validator runs modernized code against anonymized production data and compares outputs with the legacy system.

## Resources

- [Design Document](docs/architecture.md)
- [Agent Communication Protocol](docs/agent_protocols.md)
- [Google ADK Documentation](https://cloud.google.com/adk/docs)
- [Deployment Guide](docs/deployment_guide.md)

## License

[Your License Here]

## Support

- Issues: [GitHub Issues](https://github.com/your-org/repo/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/repo/discussions)
- Email: support@yourcompany.com

## Acknowledgments

Based on the Legacy Code Re-engineering: Agentic Pipeline Design Document.

---

**Built with ❤️ using Google ADK and Gemini**
