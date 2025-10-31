# Agents Requiring LLM Implementation

**Status Report**: Agents with static/mock implementations that need real LLM integration.

**Date**: 2025-10-30
**Total Agents Analyzed**: 44
**Agents Needing Implementation**: 26 (Phase 1)
**Fully Implemented**: 18+ (Phase 2)

---

## Summary

### Phase 1 Agents (Legacy Modernization) - NEED LLM IMPLEMENTATION

All 26 Phase 1 agents currently use **static/hardcoded returns** and need to be upgraded with real LLM calls.

**Pattern**: Use `google.adk.agents.Agent` framework (deprecated/static)
**Required Change**: Migrate to `vertexai.generative_models.GenerativeModel` with real LLM calls

### Phase 2 Agents (Dynamic Development) - FULLY IMPLEMENTED

All 18+ Phase 2 agents are **production-ready** with real LLM integration.

**Pattern**: Use `vertexai.generative_models.GenerativeModel` with detailed prompts

---

## Phase 1 Agents Requiring Implementation

### Orchestration Agents (3 agents)

#### 1. **Orchestrator Agent**
- **Location**: `agents/orchestration/orchestrator/agent.py`
- **Current Status**: Static task routing logic
- **What It Returns**: Hardcoded task assignments based on simple rules
- **Needs Implementation**:
  - LLM-powered task analysis and decomposition
  - Intelligent agent selection based on task requirements
  - Dynamic pipeline planning
  - Workload balancing across agents
- **Complexity**: High (central coordination logic)
- **Lines**: ~800 lines
- **Priority**: High (core orchestration)

#### 2. **Escalation Agent**
- **Location**: `agents/orchestration/escalation/agent.py`
- **Current Status**: Static pattern matching
- **Tool Functions**:
  - `analyze_rejection_pattern()` - Lines 11-42: Returns hardcoded analysis
  - `determine_resolution_strategy()` - Lines 44-80: Static strategy selection
  - `create_escalation_report()` - Lines 82-115: Template-based reports
- **What It Returns**:
  ```python
  # Example from analyze_rejection_pattern (lines 32-41)
  return {
      "status": "success",
      "is_deadlock": total_rejections >= 3,
      "total_rejections": total_rejections,
      "root_cause": most_common_reason,  # Just most frequent string
      "most_common_issue": most_common_reason,
      "unique_issues": len(unique_reasons),
      "all_reasons": list(unique_reasons)
  }
  ```
- **Needs Implementation**:
  - LLM analysis of rejection patterns to identify root causes
  - Intelligent resolution strategy recommendation
  - Context-aware escalation report generation
  - Similarity analysis of different rejection reasons
- **Complexity**: Medium
- **Priority**: High (critical for handling failures)

#### 3. **Telemetry Audit Agent**
- **Location**: `agents/orchestration/telemetry/agent.py`
- **Current Status**: Static logging
- **Tool Functions**:
  - `log_agent_activity()` - Lines 13-32: Simple dict logging
  - `track_task_metrics()` - Lines 34-52: Basic metric storage
  - `track_validation_event()` - Lines 54-74: Static event recording
  - `monitor_system_health()` - Lines 76-104: Hardcoded health checks
- **What It Returns**: Simple acknowledgment dicts
- **Needs Implementation**:
  - LLM-powered anomaly detection in logs
  - Intelligent health analysis with recommendations
  - Pattern recognition in failure trends
  - Predictive alerts based on metrics
- **Complexity**: Medium
- **Priority**: Medium (monitoring/observability)

---

### Stage 0: Discovery Agents (2 agents)

#### 4. **Discovery Agent**
- **Location**: `agents/stage0_discovery/discovery/agent.py`
- **Current Status**: **Partial implementation** (file scanning works, analysis is static)
- **What Works**:
  - Lines 30-131: Real file system scanning (uses `pathlib`, `os.walk`)
  - Lines 133-188: Real file reading and inventory creation
- **Tool Functions with Static Returns**:
  - `identify_technology_stack()` - Lines 190-270: Simple extension mapping
    ```python
    # Lines 237-269: Hardcoded technology detection
    if ".cbl" in extensions or ".cobol" in extensions:
        languages.add("COBOL")
    if ".java" in extensions:
        languages.add("Java")
    # etc...
    ```
  - `infer_business_domain()` - Lines 272-348: Keyword pattern matching
    ```python
    # Lines 309-330: Simple keyword search
    if "payment" in file_path.lower() or "transaction" in file_path.lower():
        domain_indicators["finance"] += 1
    if "order" in file_path.lower() or "cart" in file_path.lower():
        domain_indicators["ecommerce"] += 1
    ```
  - `assess_modernization_complexity()` - Lines 350-424: Hardcoded formula
    ```python
    # Lines 400-417: Static complexity score
    complexity_score = (
        tech_stack_count * 10 +
        total_loc / 10000 +
        (100 - code_quality) +
        integration_count * 5
    )
    ```
- **Needs Implementation**:
  - LLM analysis of code patterns and architecture
  - Intelligent domain inference from code semantics
  - Deep complexity analysis considering code structure
  - Dependency graph analysis
- **Complexity**: Medium-High
- **Priority**: High (foundation for legacy modernization)

#### 5. **Domain Expert Agent**
- **Location**: `agents/stage0_discovery/domain_expert/agent.py`
- **Current Status**: Static domain model templates
- **Tool Functions**:
  - `analyze_business_domain()` - Lines 11-95: Returns hardcoded domain structure
    ```python
    # Lines 57-94: Static bounded context definitions
    return {
        "status": "success",
        "bounded_contexts": [{
            "name": "Payment Processing",
            "description": "Handles payment transactions...",
            # All hardcoded
        }],
        "domain_events": [{
            "name": "PaymentProcessed",
            # All hardcoded
        }]
    }
    ```
  - `identify_business_entities()` - Lines 97-172: Template-based entities
  - `extract_business_rules()` - Lines 174-247: Keyword pattern matching
  - `create_domain_model()` - Lines 249-315: Static DDD model
- **Needs Implementation**:
  - LLM-powered domain analysis from code and documentation
  - Intelligent bounded context identification
  - Business rule extraction from code semantics
  - Domain event inference
  - Entity relationship discovery
- **Complexity**: High (requires deep domain understanding)
- **Priority**: High (DDD modeling for modernization)

---

### Stage 1: ETL Agents (5 agents)

#### 6. **Code Parser Agent**
- **Location**: `agents/stage1_etl/parsing/code_parser/agent.py`
- **Current Status**: Basic regex/AST parsing, no semantic analysis
- **Tool Functions**:
  - `parse_cobol_code()` - Lines 11-98: Regex pattern matching
  - `parse_sql_schema()` - Lines 100-172: Basic SQL parsing
  - `extract_functions()` - Lines 174-235: Regex-based extraction
- **What It Returns**: Structural information only, no semantic understanding
- **Needs Implementation**:
  - LLM-powered semantic code analysis
  - Intent and purpose extraction
  - Business logic understanding
  - Cross-reference analysis
- **Complexity**: High (language-specific parsing + LLM)
- **Priority**: High (foundation for understanding legacy code)

#### 7. **Code Analyzer Agent**
- **Location**: `agents/stage1_etl/analysis/code_analyzer/agent.py`
- **Current Status**: Static code metrics
- **Tool Functions**:
  - `analyze_code_quality()` - Lines 11-82: Hardcoded quality scores
  - `identify_code_smells()` - Lines 84-155: Pattern matching only
  - `analyze_dependencies()` - Lines 157-228: Import parsing
  - `assess_technical_debt()` - Lines 230-295: Static formula
- **What It Returns**: Superficial metrics without deep understanding
- **Needs Implementation**:
  - LLM analysis of code quality and maintainability
  - Intelligent code smell detection
  - Technical debt assessment with reasoning
  - Refactoring opportunity identification
- **Complexity**: Medium-High
- **Priority**: Medium (quality analysis)

#### 8. **Legacy Pattern Extractor Agent**
- **Location**: `agents/stage1_etl/extraction/legacy_pattern_extractor/agent.py`
- **Current Status**: Template matching
- **Tool Functions**:
  - `extract_business_logic_patterns()` - Lines 11-95: Keyword search
  - `identify_integration_patterns()` - Lines 97-175: Static pattern library
  - `extract_data_access_patterns()` - Lines 177-248: SQL pattern matching
- **Needs Implementation**:
  - LLM-powered pattern recognition
  - Custom pattern extraction beyond templates
  - Pattern similarity analysis
  - Anti-pattern detection
- **Complexity**: High
- **Priority**: High (critical for preserving business logic)

#### 9. **Knowledge Base Indexer Agent**
- **Location**: `agents/stage1_etl/indexing/kb_indexer/agent.py`
- **Current Status**: Basic Vector DB indexing, no intelligent chunking
- **Tool Functions**:
  - `create_code_embeddings()` - Lines 11-72: Simple text embedding
  - `index_to_vector_db()` - Lines 74-138: Basic batch upload
  - `create_knowledge_graph()` - Lines 140-215: Hardcoded relationships
- **What It Returns**: Raw embeddings without semantic chunking
- **Needs Implementation**:
  - LLM-powered intelligent code chunking
  - Semantic relationship extraction
  - Context-aware embedding generation
  - Knowledge graph construction with reasoning
- **Complexity**: Medium
- **Priority**: Medium (improves KB quality)

#### 10. **Dependency Mapper Agent**
- **Location**: `agents/stage1_etl/analysis/dependency_mapper/agent.py`
- **Current Status**: Import/call graph parsing only
- **Tool Functions**:
  - `map_code_dependencies()` - Lines 11-88: Import statement parsing
  - `identify_coupling()` - Lines 90-162: Static coupling metrics
  - `suggest_decoupling()` - Lines 164-228: Template-based suggestions
- **Needs Implementation**:
  - LLM analysis of dependency semantics
  - Intelligent decoupling strategies
  - Impact analysis of dependency changes
  - Architectural boundary recommendations
- **Complexity**: Medium
- **Priority**: Medium (architecture analysis)

---

### Stage 2: Development Agents (11 agents)

#### 11. **Technical Architect Agent**
- **Location**: `agents/stage2_development/architecture/architect/agent.py`
- **Current Status**: Static architecture templates
- **Tool Functions**:
  - `design_architecture()` - Lines 11-79: Returns hardcoded architecture
    ```python
    # Lines 27-76: Static architecture structure
    return {
        "status": "success",
        "component_architecture": {
            "component_id": component_id,
            "component_name": component_name,
            "architecture_style": "microservices",  # Hardcoded
            "layers": [{
                "name": "API Layer",
                "technologies": ["FastAPI", "REST"],  # Hardcoded
                # etc...
            }]
        }
    }
    ```
  - `define_nfr_strategy()` - Lines 81-156: Template NFR strategies
  - `choose_design_patterns()` - Lines 158-227: Static pattern selection
  - `create_architecture_spec()` - Lines 229-298: Combined templates
  - `validate_architecture_feasibility()` - Lines 300-353: Always returns True
- **Needs Implementation**:
  - LLM-powered architecture design based on requirements
  - Intelligent NFR strategy formulation
  - Context-aware design pattern selection
  - Trade-off analysis and recommendations
  - Technology stack selection with reasoning
- **Complexity**: Very High (architectural reasoning)
- **Priority**: Critical (drives all implementation)

#### 12. **Architecture Validator Agent**
- **Location**: `agents/stage2_development/architecture/validator/agent.py`
- **Current Status**: Checklist validation only
- **Tool Functions**:
  - `validate()` - Lines 14-72: Static checklist checks
- **Needs Implementation**:
  - LLM analysis of architecture quality
  - Deep feasibility assessment
  - Anti-pattern detection
  - Security and scalability review
- **Complexity**: High
- **Priority**: High (architecture quality gate)

#### 13. **Developer Agent**
- **Location**: `agents/stage2_development/developer/agent.py`
- **Current Status**: **NEEDS FULL LLM IMPLEMENTATION**
- **Tool Functions**:
  - `query_vector_db()` - Lines 11-51: Returns mock KB results
    ```python
    # Lines 28-49: Mock Vector DB results
    return {
        "status": "success",
        "component_id": component_id,
        "context": {
            "business_logic": {
                "description": f"Mock business logic for {component_id}",
                "rules": [
                    "Validate all inputs",
                    "Handle edge cases"
                ],
                # All hardcoded
            }
        }
    }
    ```
  - `implement_component()` - Lines 53-110: **CODE GENERATION WITH TEMPLATES**
    ```python
    # Lines 71-84: Hardcoded code template
    generated_code = f"""
# Generated implementation for {component_name}
# Language: {output_language}
# Preserves business logic from legacy system

def {component_name.lower()}():
    \"\"\"
    Implementation based on architectural specification.
    Preserves business logic from legacy context.
    \"\"\"
    # TODO: Implement actual business logic
    pass
"""

    # Lines 86-92: Hardcoded unit tests template
    unit_tests = f"""
# Unit tests for {component_name}

def test_{component_name.lower()}():
    \"\"\"Test {component_name} functionality.\"\"\"
    assert True  # TODO: Implement actual tests
"""

    # Lines 99-110: Static return
    return {
        "status": "success",
        "component_name": component_name,
        "code": generated_code,  # ← Template, not LLM-generated
        "unit_tests": unit_tests,  # ← Template
        "test_coverage_estimate": 85,  # ← Hardcoded
        "implementation_notes": [  # ← Hardcoded list
            "Business logic preserved from legacy system",
            f"Implemented in modern {output_language}",
            "Unit tests cover main functionality and edge cases"
        ]
    }
    ```
  - `refactor_existing_code()` - Lines 112-158: No actual refactoring
  - `generate_migration_script()` - Lines 160-215: Template scripts
  - `handle_cross_cutting_concerns()` - Lines 217-280: Hardcoded patterns
- **Needs Implementation**:
  - **Real code generation with LLM** (like Phase 2 agents)
  - KB-informed implementation using legacy context
  - Intelligent refactoring with business logic preservation
  - Migration script generation with data transformation logic
  - Cross-cutting concern implementation (logging, security, etc.)
- **Complexity**: Very High (core implementation agent)
- **Priority**: **CRITICAL** (generates all modernized code)
- **Reference Implementation**: See Phase 2 `agents/backend/api_developer/agent.py` for LLM pattern

#### 14. **Code Validator Agent**
- **Location**: `agents/stage2_development/validation/code_validator/agent.py`
- **Current Status**: **ALWAYS RETURNS SUCCESS** - No actual validation
- **Tool Functions**:
  - `check_correctness()` - Lines 11-21: Hardcoded 95% success
    ```python
    return {
        "status": "success",
        "correctness": {
            "requirements_met": 0.95,  # Always 95%
            "business_logic_correct": True,  # Always True
            "edge_cases_handled": True,  # Always True
            "issues": []  # Never finds issues
        }
    }
    ```
  - `check_security()` - Lines 23-35: Always passes
  - `check_error_handling()` - Lines 37-48: Always passes
  - `check_code_quality()` - Lines 50-64: Always 90% quality
  - `generate_code_validation_report()` - Lines 66-86: Static report
- **Needs Implementation**:
  - **Real LLM-powered code analysis**
  - Correctness validation against specs
  - Security vulnerability detection
  - Error handling verification
  - Code quality assessment
  - **This is critical for validation loop to work!**
- **Complexity**: High
- **Priority**: **CRITICAL** (validation loop depends on this)

#### 15. **Multi-Service Coordinator Agent**
- **Location**: `agents/stage2_development/integration/coordinator/agent.py`
- **Current Status**: Simple task splitting
- **Tool Functions**:
  - `coordinate_multi_service_implementation()` - Lines 11-95: Static orchestration
  - `create_integration_contracts()` - Lines 97-165: Template contracts
- **Needs Implementation**:
  - LLM-powered service boundary analysis
  - Intelligent API contract generation
  - Integration pattern recommendation
  - Service choreography planning
- **Complexity**: High
- **Priority**: Medium (multi-service scenarios)

#### 16. **Integration Validator Agent**
- **Location**: `agents/stage2_development/integration/validator/agent.py`
- **Current Status**: Static checks
- **Tool Functions**:
  - `validate()` - Lines 14-68: Checklist validation
- **Needs Implementation**:
  - LLM analysis of integration quality
  - Contract compatibility verification
  - Integration test generation
- **Complexity**: Medium
- **Priority**: Medium

#### 17. **Builder Agent**
- **Location**: `agents/stage2_development/build/builder/agent.py`
- **Current Status**: Mock build outputs
- **Tool Functions**:
  - `build_artifacts()` - Lines 11-72: Returns mock build results
  - `create_dockerfile()` - Lines 74-135: Template Dockerfile
  - `run_static_analysis()` - Lines 137-192: Fake linting results
- **Needs Implementation**:
  - LLM-powered Dockerfile generation
  - Build script optimization
  - Intelligent build configuration
- **Complexity**: Medium
- **Priority**: Medium (build automation)

#### 18. **Build Validator Agent**
- **Location**: `agents/stage2_development/build/validator/agent.py`
- **Current Status**: Always passes
- **Tool Functions**:
  - `validate()` - Lines 14-58: Mock validation
- **Needs Implementation**:
  - Real build artifact validation
  - Security scanning
  - Dependency checking
- **Complexity**: Low-Medium
- **Priority**: Low (build quality gate)

#### 19. **QA Tester Agent**
- **Location**: `agents/stage2_development/qa/tester/agent.py`
- **Current Status**: Template test generation
- **Tool Functions**:
  - `generate_test_cases()` - Lines 11-88: Static test templates
  - `run_tests()` - Lines 90-145: Mock test execution (always passes)
  - `analyze_coverage()` - Lines 147-198: Fake 90% coverage
  - `run_load_tests()` - Lines 200-258: Mock performance results
  - `generate_test_report()` - Lines 260-310: Template reports
- **Needs Implementation**:
  - LLM-powered test case generation from requirements
  - Real test execution integration
  - Coverage gap analysis
  - Load test scenario generation
- **Complexity**: High
- **Priority**: High (quality assurance)

#### 20. **QA Validator Agent**
- **Location**: `agents/stage2_development/qa/validator/agent.py`
- **Current Status**: Static validation
- **Tool Functions**:
  - `validate()` - Lines 14-68: Checklist only
- **Needs Implementation**:
  - LLM analysis of test quality
  - Coverage adequacy assessment
  - Test strategy review
- **Complexity**: Medium
- **Priority**: Medium

#### 21. **Quality Attribute Validator Agent**
- **Location**: `agents/stage2_development/validation/quality_attribute/agent.py`
- **Current Status**: Always passes NFRs
- **Tool Functions**:
  - `validate()` - Lines 14-78: Mock NFR validation
- **Needs Implementation**:
  - Real performance analysis
  - Scalability assessment
  - Security review
  - Maintainability scoring
- **Complexity**: Medium-High
- **Priority**: Medium

---

### Stage 3: CI/CD Agents (5 agents)

#### 22. **Deployer Agent**
- **Location**: `agents/stage3_cicd/deployment/deployer/agent.py`
- **Current Status**: Mock deployment
- **Tool Functions**:
  - `deploy_to_environment()` - Lines 11-72: Returns success without deploying
  - `run_health_checks()` - Lines 74-125: Always healthy
  - `rollback_deployment()` - Lines 127-172: Mock rollback
  - `configure_infrastructure()` - Lines 174-228: Template configs
- **Needs Implementation**:
  - LLM-powered deployment strategy selection
  - Intelligent rollback decision making
  - Infrastructure configuration generation
- **Complexity**: Medium
- **Priority**: Medium (deployment automation)

#### 23. **Monitor Agent**
- **Location**: `agents/stage3_cicd/monitoring/monitor/agent.py`
- **Current Status**: Fake metrics
- **Tool Functions**:
  - `collect_metrics()` - Lines 11-68: Returns mock metrics
  - `check_sla_compliance()` - Lines 70-125: Always compliant
  - `detect_anomalies()` - Lines 127-185: No anomalies detected
  - `generate_alerts()` - Lines 187-238: No alerts
- **Needs Implementation**:
  - Real metrics collection integration
  - LLM-powered anomaly detection
  - Intelligent alert generation
  - Root cause analysis
- **Complexity**: Medium-High
- **Priority**: Medium (observability)

#### 24. **Security Scanner Agent**
- **Location**: `agents/stage3_cicd/security/scanner/agent.py`
- **Current Status**: Always secure
- **Tool Functions**:
  - `scan_vulnerabilities()` - Lines 11-75: Returns no vulnerabilities
  - `check_compliance()` - Lines 77-138: Always compliant
  - `analyze_secrets()` - Lines 140-192: No secrets found
  - `generate_security_report()` - Lines 194-248: Clean report
- **Needs Implementation**:
  - Real vulnerability scanning
  - LLM-powered security analysis
  - Compliance verification
  - Secret detection
- **Complexity**: Medium
- **Priority**: High (security is critical)

#### 25. **Performance Tester Agent**
- **Location**: `agents/stage3_cicd/testing/performance_tester/agent.py`
- **Current Status**: Mock performance results
- **Tool Functions**:
  - `run_load_tests()` - Lines 11-88: Fake load test results
  - `run_stress_tests()` - Lines 90-155: Mock stress results
  - `analyze_bottlenecks()` - Lines 157-218: No bottlenecks
  - `generate_performance_report()` - Lines 220-278: Template report
- **Needs Implementation**:
  - Real load testing integration
  - LLM analysis of performance data
  - Bottleneck identification with recommendations
  - Optimization suggestions
- **Complexity**: Medium
- **Priority**: Medium

#### 26. **Release Manager Agent**
- **Location**: `agents/stage3_cicd/release/manager/agent.py`
- **Current Status**: Template release plans
- **Tool Functions**:
  - `plan_release()` - Lines 11-82: Static release plan
  - `execute_release()` - Lines 84-148: Mock execution
  - `generate_release_notes()` - Lines 150-212: Template notes
  - `coordinate_rollout()` - Lines 214-272: Simple rollout
- **Needs Implementation**:
  - LLM-powered release planning
  - Risk assessment and mitigation
  - Intelligent rollout strategies
  - Release note generation from commits
- **Complexity**: Medium
- **Priority**: Medium

---

## Implementation Pattern to Follow

### Phase 2 Agents Show the Right Pattern

**Example from API Developer Agent** (`agents/backend/api_developer/agent.py`):

```python
from vertexai.generative_models import GenerativeModel

class APIDevAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    def __init__(self, context, message_bus, orchestrator_id):
        super().__init__(context, message_bus)

        # 1. Initialize LLM model
        model_name = context.model or "gemini-2.0-flash"
        self.model = GenerativeModel(model_name)

        # 2. A2A integration
        self.a2a = A2AIntegration(context, message_bus, orchestrator_id)

    @A2AIntegration.with_task_tracking
    def generate_rest_api(self, language, framework, endpoints, **kwargs):
        # 3. Build detailed prompt
        prompt = self._build_rest_api_prompt(language, framework, endpoints, ...)

        # 4. Call LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # 5. Parse LLM response
        result = self._parse_api_implementation(response.text, language)

        return {
            "status": "success",
            "code": result["code"],
            "openapi_spec": result["openapi_spec"],
            # Real LLM-generated content
        }

    def _build_rest_api_prompt(self, language, framework, endpoints, ...):
        """Build detailed multi-paragraph prompt."""
        return f"""You are an expert backend developer...

Generate a production-ready REST API with the following requirements:

**Language**: {language}
**Framework**: {framework}

**Endpoints**:
{self._format_endpoints(endpoints)}

**Requirements**:
- Include comprehensive error handling
- Add input validation
- Include OpenAPI/Swagger documentation
- Follow best practices for {framework}
...
"""

    def _get_generation_config(self):
        """Configure LLM generation."""
        return {
            "temperature": 0.2,  # Low temperature for code
            "max_output_tokens": 8192,
            "top_p": 0.95
        }
```

### Migration Steps for Each Agent

1. **Add LLM imports**:
   ```python
   from vertexai.generative_models import GenerativeModel
   ```

2. **Initialize model in `__init__`**:
   ```python
   self.model = GenerativeModel(context.model or "gemini-2.0-flash")
   ```

3. **Replace static returns with LLM calls**:
   - Build detailed prompts (300-500 lines of prompt engineering per agent)
   - Call `self.model.generate_content(prompt)`
   - Parse LLM response (JSON, code blocks, etc.)

4. **Add generation config**:
   - Temperature: 0.2-0.3 for code generation
   - Temperature: 0.5-0.7 for analysis/reasoning
   - Max tokens: 4096-8192 for code

5. **Test with real scenarios**

---

## Next Steps

1. **Start with Developer Agent** - Most critical, blocks everything
2. **Then Code Validator Agent** - Required for validation loop
3. **Then Technical Architect Agent** - Drives design decisions
4. **Use Phase 2 agents as reference implementations**
5. **Test each agent with real scenarios as you go**

---

## Reference Implementations (Phase 2 - Already Done)

Use these as templates for Phase 1 migration:

### Backend
- `agents/backend/api_developer/agent.py` - REST/GraphQL/gRPC generation
- `agents/backend/database_engineer/agent.py` - Schema design
- `agents/backend/microservices_architect/agent.py` - Architecture reasoning (uses thinking model!)

### Frontend
- `agents/frontend/ui_developer/agent.py` - React/Vue component generation
- `agents/frontend/react_specialist/agent.py` - Advanced React patterns
- `agents/frontend/css_specialist/agent.py` - Styling generation

### Infrastructure
- `agents/infrastructure/cloud_infrastructure/agent.py` - IaC generation
- `agents/infrastructure/kubernetes/agent.py` - K8s manifests

### Multimodal
- `agents/multimodal/vision/agent.py` - Image-to-code (uses multimodal model!)

---

## Summary

- **26 agents need LLM implementation** (all Phase 1)
- **18+ agents are production-ready** (all Phase 2)
- **Reference code exists**: Phase 2 agents show exactly how to do it