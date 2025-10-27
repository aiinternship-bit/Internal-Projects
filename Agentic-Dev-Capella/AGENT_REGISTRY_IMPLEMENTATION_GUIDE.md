# Agent Registry Service - Implementation Guide

This guide will help you implement the Agent Registry Service methods. The basic structure is complete with method signatures, documentation, and TODOs.

## 📁 File Location
`shared/services/agent_registry.py`

## 🎯 Overview

The Agent Registry Service is a centralized catalog for all agents with:
- **Capability search** - Find agents by skills, languages, frameworks
- **Performance tracking** - Monitor success rates, duration, costs
- **KB usage statistics** - Track knowledge base query patterns
- **Availability monitoring** - Check agent load and capacity
- **Persistence** - Save/load registry to disk

## 📊 Data Structures

### Core Storage
```python
self._agents: Dict[str, AgentCapability]  # agent_id -> capability
self._agent_name_to_id: Dict[str, str]    # name -> agent_id
```

### Indexes (for fast lookup)
```python
self._capability_index: Dict[str, Set[str]]      # capability -> agent_ids
self._language_index: Dict[str, Set[str]]        # language -> agent_ids
self._framework_index: Dict[str, Set[str]]       # framework -> agent_ids
self._type_index: Dict[AgentType, Set[str]]      # type -> agent_ids
self._modality_index: Dict[InputModality, Set[str]]  # modality -> agent_ids
```

### Tracking
```python
self._performance_history: Dict[str, List[Dict]]  # agent_id -> performance records
self._kb_usage_stats: Dict[str, Dict]             # agent_id -> KB stats
self._agent_load: Dict[str, int]                  # agent_id -> active task count
self._agent_last_seen: Dict[str, str]             # agent_id -> timestamp
```

---

## 🔨 Implementation Order (Recommended)

Implement methods in this order for logical dependencies:

### Phase 1: Core Registration (Essential)
1. `register_agent()` - Register agent and build indexes
2. `get_agent()` - Retrieve agent by ID
3. `get_agent_by_name()` - Retrieve agent by name
4. `list_all_agents()` - List all agents with filters
5. `deregister_agent()` - Remove agent from registry

### Phase 2: Search and Discovery
6. `search_by_capability()` - Most important search method
7. `search_by_language()` - Filter by programming language
8. `search_by_framework()` - Filter by framework
9. `search_by_type()` - Filter by agent type
10. `search_by_modality()` - Filter by input modality
11. `recommend_agents()` - Smart recommendation with scoring

### Phase 3: Performance Tracking
12. `update_performance()` - Record task completion metrics
13. `get_performance_metrics()` - Get current metrics
14. `get_performance_history()` - Get historical data
15. `compare_agents()` - Compare multiple agents

### Phase 4: KB Usage Tracking
16. `update_kb_usage()` - Record KB query
17. `get_kb_usage_stats()` - Get KB statistics
18. `get_kb_effectiveness_score()` - Calculate effectiveness

### Phase 5: Availability
19. `update_agent_load()` - Update active task count
20. `get_agent_load()` - Get current load
21. `get_available_agents()` - Find agents with capacity
22. `is_agent_available()` - Check specific agent

### Phase 6: Analytics
23. `get_registry_stats()` - Overall statistics
24. `get_capability_coverage()` - Capability distribution
25. `identify_capability_gaps()` - Find missing capabilities

### Phase 7: Persistence
26. `_save_to_disk()` - Save to JSON file
27. `_load_from_disk()` - Load from JSON file
28. `export_to_json()` - Export registry
29. `import_from_json()` - Import registry

### Phase 8: Utilities
30. `update_agent_capability()` - Update existing agent
31. `clear_registry()` - Clear all data
32. `validate_registry_consistency()` - Validation checks

---

## 📝 Implementation Examples

### Example 1: `register_agent()`

```python
def register_agent(self, capability: AgentCapability) -> bool:
    """Register an agent with its capabilities."""

    # Check if agent already exists
    if capability.agent_id in self._agents:
        return False

    # Store agent capability
    self._agents[capability.agent_id] = capability

    # Update name index
    self._agent_name_to_id[capability.agent_name] = capability.agent_id

    # Update capability index
    for cap in capability.capabilities:
        if cap not in self._capability_index:
            self._capability_index[cap] = set()
        self._capability_index[cap].add(capability.agent_id)

    # Update language index
    for lang in capability.supported_languages:
        if lang not in self._language_index:
            self._language_index[lang] = set()
        self._language_index[lang].add(capability.agent_id)

    # Update framework index
    for fw in capability.supported_frameworks:
        if fw not in self._framework_index:
            self._framework_index[fw] = set()
        self._framework_index[fw].add(capability.agent_id)

    # Update type index
    if capability.agent_type not in self._type_index:
        self._type_index[capability.agent_type] = set()
    self._type_index[capability.agent_type].add(capability.agent_id)

    # Update modality index
    for modality in capability.input_modalities:
        if modality not in self._modality_index:
            self._modality_index[modality] = set()
        self._modality_index[modality].add(capability.agent_id)

    # Initialize performance tracking
    self._performance_history[capability.agent_id] = []

    # Initialize KB usage stats
    self._kb_usage_stats[capability.agent_id] = {
        "total_queries": 0,
        "queries_by_type": {},
        "avg_query_time_ms": 0.0,
        "cache_hit_rate": 0.0,
        "total_cache_hits": 0,
        "total_cache_misses": 0
    }

    # Set initial load and last seen
    self._agent_load[capability.agent_id] = 0
    self._agent_last_seen[capability.agent_id] = datetime.utcnow().isoformat()

    # Auto-save if enabled
    if self._auto_save:
        self._save_to_disk()

    return True
```

### Example 2: `search_by_capability()`

```python
def search_by_capability(
    self,
    required_capabilities: Set[str],
    optional_capabilities: Optional[Set[str]] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    agent_type: Optional[AgentType] = None,
    input_modality: Optional[InputModality] = None
) -> List[AgentCapability]:
    """Search for agents by capabilities and filters."""

    # Start with agents that have at least one required capability
    candidate_ids = set()

    if required_capabilities:
        # Find agents with each required capability
        capability_matches = []
        for cap in required_capabilities:
            if cap in self._capability_index:
                capability_matches.append(self._capability_index[cap])

        # Intersect to find agents with ALL required capabilities
        if capability_matches:
            candidate_ids = set.intersection(*capability_matches)
    else:
        # No required capabilities - start with all agents
        candidate_ids = set(self._agents.keys())

    # Apply language filter
    if language and language in self._language_index:
        candidate_ids &= self._language_index[language]

    # Apply framework filter
    if framework and framework in self._framework_index:
        candidate_ids &= self._framework_index[framework]

    # Apply type filter
    if agent_type and agent_type in self._type_index:
        candidate_ids &= self._type_index[agent_type]

    # Apply modality filter
    if input_modality and input_modality in self._modality_index:
        candidate_ids &= self._modality_index[input_modality]

    # Get agent capabilities
    candidates = [self._agents[aid] for aid in candidate_ids]

    # Calculate match scores
    scored_agents = []
    for agent in candidates:
        score = agent.calculate_match_score(
            required_capabilities=required_capabilities,
            optional_capabilities=optional_capabilities,
            language=language,
            framework=framework
        )
        scored_agents.append((agent, score))

    # Sort by score descending
    scored_agents.sort(key=lambda x: x[1], reverse=True)

    # Return agents only (without scores)
    return [agent for agent, score in scored_agents]
```

### Example 3: `update_performance()`

```python
def update_performance(
    self,
    agent_id: str,
    success: bool,
    duration_minutes: float,
    cost_usd: float = 0.0,
    task_type: Optional[str] = None,
    validation_failures: int = 0
) -> bool:
    """Update agent performance metrics after task completion."""

    # Check if agent exists
    if agent_id not in self._agents:
        return False

    agent = self._agents[agent_id]

    # Create performance record
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "success": success,
        "duration_minutes": duration_minutes,
        "cost_usd": cost_usd,
        "task_type": task_type,
        "validation_failures": validation_failures
    }

    # Add to history
    self._performance_history[agent_id].append(record)

    # Update aggregate metrics
    metrics = agent.performance_metrics

    if success:
        metrics.total_tasks_completed += 1
    else:
        metrics.total_tasks_failed += 1

    # Update moving average for duration (last 100 tasks)
    recent_history = self._performance_history[agent_id][-100:]
    durations = [r["duration_minutes"] for r in recent_history]
    metrics.avg_task_duration_minutes = sum(durations) / len(durations)

    # Update p95 duration
    sorted_durations = sorted(durations)
    p95_index = int(len(sorted_durations) * 0.95)
    metrics.p95_task_duration_minutes = sorted_durations[p95_index] if sorted_durations else 0.0

    # Update success rate
    metrics.success_rate = metrics.calculate_success_rate()

    # Update average validation failures
    validation_counts = [r["validation_failures"] for r in recent_history]
    metrics.avg_validation_failures = sum(validation_counts) / len(validation_counts)

    # Update retry rate (tasks with validation failures)
    tasks_with_retries = sum(1 for v in validation_counts if v > 0)
    metrics.retry_rate = tasks_with_retries / len(validation_counts) if validation_counts else 0.0

    # Auto-save if enabled
    if self._auto_save:
        self._save_to_disk()

    return True
```

### Example 4: `_save_to_disk()`

```python
def _save_to_disk(self) -> bool:
    """Save registry to disk."""

    try:
        # Create directory if doesn't exist
        path = Path(self._persistence_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare data for serialization
        data = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": {
                agent_id: agent.to_dict()
                for agent_id, agent in self._agents.items()
            },
            "performance_history": self._performance_history,
            "kb_usage_stats": self._kb_usage_stats,
            "agent_load": self._agent_load,
            "agent_last_seen": self._agent_last_seen
        }

        # Write to temp file first (atomic write)
        temp_path = str(path) + ".tmp"
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Rename to actual file (atomic operation)
        import os
        os.replace(temp_path, str(path))

        return True

    except Exception as e:
        print(f"Error saving registry to disk: {str(e)}")
        return False
```

---

## 🧪 Testing Your Implementation

### Basic Test Script

Create `tests/test_agent_registry.py`:

```python
from shared.services.agent_registry import AgentRegistryService
from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    KBQueryStrategy
)

def test_basic_operations():
    # Create registry
    registry = AgentRegistryService(
        persistence_path="./test_registry.json",
        enable_persistence=False
    )

    # Create test agent
    agent = AgentCapability(
        agent_id="test_agent_1",
        agent_name="Test Developer Agent",
        agent_type=AgentType.DEVELOPMENT,
        description="Test agent for development tasks",
        capabilities={"python_development", "api_development"},
        supported_languages=["python", "javascript"],
        supported_frameworks=["django", "fastapi"]
    )

    # Test registration
    assert registry.register_agent(agent) == True
    assert len(registry) == 1

    # Test retrieval
    retrieved = registry.get_agent("test_agent_1")
    assert retrieved is not None
    assert retrieved.agent_name == "Test Developer Agent"

    # Test search
    results = registry.search_by_capability({"python_development"})
    assert len(results) == 1
    assert results[0].agent_id == "test_agent_1"

    # Test performance update
    registry.update_performance(
        agent_id="test_agent_1",
        success=True,
        duration_minutes=15.5,
        cost_usd=0.05
    )

    metrics = registry.get_performance_metrics("test_agent_1")
    assert metrics.total_tasks_completed == 1

    print("✅ All basic tests passed!")

if __name__ == "__main__":
    test_basic_operations()
```

---

## 💡 Implementation Tips

### 1. Start Simple
Implement the basic CRUD operations first (register, get, list, deregister).

### 2. Use Indexes
Leverage the index dictionaries for fast lookups rather than iterating through all agents.

### 3. Handle Edge Cases
- Agent already exists (registration)
- Agent not found (retrieval, updates)
- Empty searches
- Division by zero in metrics

### 4. Maintain Consistency
When updating an agent, ensure ALL indexes are updated consistently.

### 5. Add Logging
Add print statements or proper logging for debugging:
```python
print(f"Registered agent: {capability.agent_name}")
```

### 6. Test Incrementally
Test each method as you implement it. Don't wait until all methods are done.

### 7. Use Type Hints
Keep the type hints consistent - they help with IDE autocomplete.

---

## 🎓 Learning Resources

### Index Pattern
```python
# Building an index
for item in items:
    if item.key not in index:
        index[item.key] = set()
    index[item.key].add(item.id)

# Using an index
matching_ids = index.get(search_key, set())
```

### Moving Average
```python
# Last N items
recent = history[-N:]
average = sum(recent) / len(recent) if recent else 0.0
```

### Atomic File Write
```python
# Write to temp file first
temp_path = path + ".tmp"
write_to_file(temp_path)

# Then rename (atomic)
os.replace(temp_path, path)
```

---

## ✅ Validation Checklist

Before considering implementation complete:

- [ ] All 30+ methods implemented
- [ ] Basic test script passes
- [ ] Registry can save/load from disk
- [ ] Search methods return correct results
- [ ] Performance tracking updates metrics
- [ ] KB usage stats are recorded
- [ ] Availability checks work correctly
- [ ] No crashes on edge cases (empty searches, missing agents)
- [ ] Indexes stay consistent with main storage
- [ ] Code follows existing style and conventions

---

## 🚀 Next Steps After Implementation

Once you complete the Agent Registry Service:

1. **Test it thoroughly** with multiple agents
2. **Create example registrations** for the 26 Phase 1 agents
3. **Integrate with Dynamic Orchestrator** (next milestone)
4. **Add REST API** endpoints (optional enhancement)
5. **Add Cloud Firestore** backend (optional enhancement)

---

## 📞 Need Help?

Common issues and solutions:

**Issue**: Index out of sync with main storage
**Solution**: Always update all indexes when modifying agents

**Issue**: Performance metrics not updating
**Solution**: Check that you're updating the AgentCapability object, not a copy

**Issue**: Search returning no results
**Solution**: Verify index was built during registration

**Issue**: File save/load errors
**Solution**: Check directory permissions and path validity

---

Good luck with implementation! Take it one method at a time, test frequently, and don't hesitate to refer back to this guide.
