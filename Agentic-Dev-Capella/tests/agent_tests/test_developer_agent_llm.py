"""
tests/agent_tests/test_developer_agent_llm.py

Comprehensive tests for Developer Agent with real LLM implementation.
Tests code generation quality, refactoring, migrations, and cross-cutting concerns.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock google.cloud modules before importing agents
sys.modules['google.cloud.aiplatform'] = MagicMock()
sys.modules['google.cloud.pubsub_v1'] = MagicMock()
sys.modules['vertexai'] = MagicMock()
sys.modules['vertexai.generative_models'] = MagicMock()
sys.modules['vertexai.preview'] = MagicMock()
sys.modules['vertexai.preview.reasoning_engines'] = MagicMock()
sys.modules['vertexai.language_models'] = MagicMock()
sys.modules['google.adk'] = MagicMock()
sys.modules['google.adk.agents'] = MagicMock()


# ============================================================================
# MOCK TESTS (No LLM API Calls Required)
# ============================================================================

class TestDeveloperAgentMock(unittest.TestCase):
    """Test Developer Agent with mocked LLM responses."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = {
            "project_id": "test-project",
            "location": "us-central1",
            "model": "gemini-2.0-flash"
        }
        self.message_bus = MagicMock()
        self.orchestrator_id = "orchestrator_123"

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_implement_component_python(self, mock_aiplatform_init, mock_model):
        """Test implementing a Python component with LLM."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        # Mock LLM responses
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock code generation response
        code_response = MagicMock()
        code_response.text = """
```python
class PaymentProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_payment(self, amount: float, currency: str) -> dict:
        \"\"\"Process a payment transaction.\"\"\"
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Validate currency
        valid_currencies = ["USD", "EUR", "GBP"]
        if currency not in valid_currencies:
            raise ValueError(f"Invalid currency: {currency}")

        # Process payment
        return {
            "status": "success",
            "transaction_id": "txn_123",
            "amount": amount,
            "currency": currency
        }
```
"""

        # Mock test generation response
        test_response = MagicMock()
        test_response.text = """
```python
import pytest
from payment_processor import PaymentProcessor

def test_process_payment_success():
    processor = PaymentProcessor(api_key="test_key")
    result = processor.process_payment(100.0, "USD")

    assert result["status"] == "success"
    assert result["amount"] == 100.0
    assert result["currency"] == "USD"

def test_process_payment_invalid_amount():
    processor = PaymentProcessor(api_key="test_key")

    with pytest.raises(ValueError, match="Amount must be positive"):
        processor.process_payment(-10.0, "USD")

def test_process_payment_invalid_currency():
    processor = PaymentProcessor(api_key="test_key")

    with pytest.raises(ValueError, match="Invalid currency"):
        processor.process_payment(100.0, "XXX")
```
"""

        mock_model_instance.generate_content.side_effect = [code_response, test_response]

        # Create agent
        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        # Test implementation
        architecture_spec = {
            "component_name": "PaymentProcessor",
            "component_id": "payment_001",
            "layers": [
                {"name": "Business Logic", "description": "Core payment processing"}
            ],
            "design_patterns": ["Factory", "Strategy"],
            "nfrs": {
                "response_time_ms": 100,
                "availability": 0.999
            },
            "dependencies": []
        }

        result = agent.implement_component(
            architecture_spec=architecture_spec,
            output_language="python",
            task_id="task_001"
        )

        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertIn("code", result)
        self.assertIn("unit_tests", result)
        self.assertIn("PaymentProcessor", result["code"])
        self.assertIn("process_payment", result["code"])
        self.assertIn("pytest", result["unit_tests"])
        self.assertGreater(result["lines_of_code"], 0)
        self.assertGreater(result["test_coverage_estimate"], 80)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_implement_component_typescript(self, mock_aiplatform_init, mock_model):
        """Test implementing a TypeScript component."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        code_response = MagicMock()
        code_response.text = """
```typescript
interface User {
    id: string;
    email: string;
    name: string;
}

class UserService {
    private users: Map<string, User>;

    constructor() {
        this.users = new Map();
    }

    createUser(email: string, name: string): User {
        if (!this.isValidEmail(email)) {
            throw new Error('Invalid email format');
        }

        const user: User = {
            id: crypto.randomUUID(),
            email,
            name
        };

        this.users.set(user.id, user);
        return user;
    }

    private isValidEmail(email: string): boolean {
        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        return emailRegex.test(email);
    }
}
```
"""

        test_response = MagicMock()
        test_response.text = """
```typescript
import { UserService } from './user-service';

describe('UserService', () => {
    let service: UserService;

    beforeEach(() => {
        service = new UserService();
    });

    it('should create a user with valid data', () => {
        const user = service.createUser('test@example.com', 'Test User');

        expect(user.id).toBeDefined();
        expect(user.email).toBe('test@example.com');
        expect(user.name).toBe('Test User');
    });

    it('should throw error for invalid email', () => {
        expect(() => {
            service.createUser('invalid-email', 'Test User');
        }).toThrow('Invalid email format');
    });
});
```
"""

        mock_model_instance.generate_content.side_effect = [code_response, test_response]

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        result = agent.implement_component(
            architecture_spec={"component_name": "UserService"},
            output_language="typescript",
            task_id="task_002"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("UserService", result["code"])
        self.assertIn("describe", result["unit_tests"])

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_refactor_code(self, mock_aiplatform_init, mock_model):
        """Test code refactoring functionality."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        refactor_response = MagicMock()
        refactor_response.text = """
```python
# Refactored code with improved structure
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    \"\"\"Process and validate data with improved error handling.\"\"\"

    def __init__(self, config: dict):
        self.config = config
        self.validate_config()

    def validate_config(self) -> None:
        \"\"\"Validate configuration parameters.\"\"\"
        required_keys = ['batch_size', 'timeout']
        missing = [k for k in required_keys if k not in self.config]
        if missing:
            raise ValueError(f"Missing config keys: {missing}")

    def process_batch(self, items: List[dict]) -> List[dict]:
        \"\"\"Process a batch of items with error handling.\"\"\"
        results = []
        for item in items:
            try:
                result = self._process_item(item)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process item: {e}")
                continue
        return results

    def _process_item(self, item: dict) -> dict:
        \"\"\"Process a single item.\"\"\"
        # Validation
        if not item.get('id'):
            raise ValueError("Item missing ID")

        # Processing logic
        return {
            'id': item['id'],
            'status': 'processed',
            'data': item.get('data', {})
        }
```

**Changes Made:**
- Added type hints for better code clarity
- Extracted validation logic to separate method
- Improved error handling with logging
- Added docstrings for all methods
- Used list comprehension for cleaner code

**Improvements:**
- Performance: More efficient error handling
- Maintainability: Better separation of concerns
- Quality: Type safety and documentation added
"""

        mock_model_instance.generate_content.return_value = refactor_response

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        existing_code = """
def process_data(items):
    results = []
    for item in items:
        results.append({'id': item['id'], 'status': 'done'})
    return results
"""

        result = agent.refactor_existing_code(
            existing_code=existing_code,
            refactor_goals=["Add type hints", "Improve error handling", "Add logging"],
            language="python",
            task_id="task_003"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("DataProcessor", result["refactored_code"])
        self.assertIn("logging", result["refactored_code"])
        self.assertGreater(len(result["changes_made"]), 0)
        self.assertIn("improvements", result)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_migration_script(self, mock_aiplatform_init, mock_model):
        """Test database migration script generation."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        migration_response = MagicMock()
        migration_response.text = """
**MIGRATION_SCRIPT:**
```sql
-- Add email column to users table
BEGIN TRANSACTION;

-- Add column
ALTER TABLE users ADD COLUMN email VARCHAR(255);

-- Add index for email lookups
CREATE INDEX idx_users_email ON users(email);

-- Add unique constraint
ALTER TABLE users ADD CONSTRAINT uk_users_email UNIQUE (email);

-- Update existing rows with placeholder emails
UPDATE users SET email = CONCAT('user_', id, '@legacy.com') WHERE email IS NULL;

-- Make column NOT NULL
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

COMMIT;
```

**ROLLBACK_SCRIPT:**
```sql
-- Rollback: Remove email column
BEGIN TRANSACTION;

DROP INDEX IF EXISTS idx_users_email;
ALTER TABLE users DROP COLUMN IF EXISTS email;

COMMIT;
```

**SAFETY_NOTES:**
- Backup database before running migration
- Test in staging environment first
- Estimated downtime: 2 minutes for 1M rows
- Verify data integrity after migration
- Keep rollback script ready
"""

        mock_model_instance.generate_content.return_value = migration_response

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        result = agent.generate_migration_script(
            schema_changes={
                "table": "users",
                "add_columns": [
                    {"name": "email", "type": "VARCHAR(255)", "nullable": False}
                ]
            },
            data_transformations=[
                {"description": "Generate email addresses for existing users"}
            ],
            database_type="postgresql",
            task_id="task_004"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("migration_script", result)
        self.assertIn("rollback_script", result)
        self.assertIn("ALTER TABLE", result["migration_script"])
        self.assertIn("DROP", result["rollback_script"])
        self.assertGreater(len(result["safety_checks"]), 0)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_add_cross_cutting_concerns(self, mock_aiplatform_init, mock_model):
        """Test adding cross-cutting concerns to code."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        enhanced_response = MagicMock()
        enhanced_response.text = """
```python
import logging
import time
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)

def with_logging(func: Callable) -> Callable:
    \"\"\"Decorator to add logging to functions.\"\"\"
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    return wrapper

def with_timing(func: Callable) -> Callable:
    \"\"\"Decorator to add performance timing.\"\"\"
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

class DataService:
    @with_logging
    @with_timing
    def process_data(self, data: dict) -> dict:
        \"\"\"Process data with logging and timing.\"\"\"
        # Validation
        if not data:
            raise ValueError("Data cannot be empty")

        # Processing
        result = {'processed': True, 'data': data}
        return result
```

**Implementation Details:**
- logging: Added structured logging with INFO and ERROR levels
- monitoring: Added performance timing decorator
"""

        mock_model_instance.generate_content.return_value = enhanced_response

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        base_code = """
def process_data(data):
    return {'processed': True, 'data': data}
"""

        result = agent.handle_cross_cutting_concerns(
            code=base_code,
            concerns=["logging", "monitoring"],
            language="python",
            task_id="task_005"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("logging", result["enhanced_code"])
        self.assertIn("with_logging", result["enhanced_code"])
        self.assertEqual(len(result["concerns_added"]), 2)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_query_vector_db_mock(self, mock_aiplatform_init, mock_model):
        """Test Vector DB query with mock client."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock vector DB client
        mock_vector_db = MagicMock()
        mock_vector_db.query_semantic.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "business_logic": {
                        "description": "Payment validation logic",
                        "key_algorithms": ["Amount validation", "Currency check"],
                        "edge_cases": ["Negative amounts", "Unknown currencies"]
                    }
                }
            }
        ]

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id,
            vector_db_client=mock_vector_db
        )

        result = agent.query_vector_db(
            component_id="payment_validator",
            query_type="business_logic",
            task_id="task_006"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["component_id"], "payment_validator")
        self.assertEqual(result["kb_results_count"], 1)
        self.assertIn("context", result)

    def test_prompt_building(self):
        """Test prompt building methods."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        # Test implementation prompt
        prompt = agent._build_implementation_prompt(
            component_name="TestComponent",
            architecture_spec={
                "layers": [{"name": "API Layer", "description": "REST API"}],
                "design_patterns": ["Factory"],
                "nfrs": {"performance": "high"},
                "dependencies": ["database"]
            },
            legacy_context={"description": "Legacy system details"},
            output_language="python"
        )

        self.assertIn("TestComponent", prompt)
        self.assertIn("python", prompt.lower())
        self.assertIn("Factory", prompt)

        # Test refactoring prompt
        refactor_prompt = agent._build_refactoring_prompt(
            existing_code="def foo(): pass",
            refactor_goals=["Add type hints", "Improve naming"],
            language="python"
        )

        self.assertIn("type hints", refactor_prompt.lower())
        self.assertIn("def foo(): pass", refactor_prompt)

    def test_response_parsing(self):
        """Test response parsing methods."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        # Test code parsing with markdown
        response_with_markdown = """
```python
def hello():
    print("world")
```
"""
        result = agent._parse_implementation_response(response_with_markdown, "python")
        self.assertIn("hello", result["code"])
        self.assertNotIn("```", result["code"])

        # Test code parsing without markdown
        response_plain = "def hello():\n    print('world')"
        result = agent._parse_implementation_response(response_plain, "python")
        self.assertIn("hello", result["code"])


# ============================================================================
# INTEGRATION TESTS (Require Google Cloud Credentials)
# ============================================================================

import os

@unittest.skipUnless(
    os.getenv("GOOGLE_CLOUD_PROJECT"),
    "Skipping integration tests - set GOOGLE_CLOUD_PROJECT to run"
)
class TestDeveloperAgentIntegration(unittest.TestCase):
    """
    Integration tests with real Gemini LLM.

    Set environment variables:
    export GOOGLE_CLOUD_PROJECT=your-project-id
    gcloud auth application-default login
    """

    @classmethod
    def setUpClass(cls):
        """Set up Vertex AI."""
        cls.context = {
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "location": "us-central1",
            "model": "gemini-2.0-flash"
        }
        cls.message_bus = MagicMock()
        cls.orchestrator_id = "test_orchestrator"

        print(f"\nInitialized for project: {cls.context['project_id']}")

    def test_implement_simple_component_real(self):
        """Test implementing a simple component with real LLM."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        architecture_spec = {
            "component_name": "TemperatureConverter",
            "component_id": "temp_conv_001",
            "description": "Convert between Celsius and Fahrenheit",
            "layers": [],
            "design_patterns": [],
            "nfrs": {},
            "dependencies": []
        }

        result = agent.implement_component(
            architecture_spec=architecture_spec,
            output_language="python",
            task_id="test_real_001"
        )

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("code", result)
        self.assertIn("unit_tests", result)

        # Check code quality
        code = result["code"]
        self.assertGreater(len(code), 50)  # Non-trivial implementation
        # Should have some conversion logic
        self.assertTrue(
            "celsius" in code.lower() or "fahrenheit" in code.lower(),
            "Code should mention temperature units"
        )

        # Check tests
        tests = result["unit_tests"]
        self.assertGreater(len(tests), 30)
        self.assertTrue(
            "test" in tests.lower() or "def test_" in tests.lower(),
            "Should contain test functions"
        )

        print(f"\n[REAL LLM TEST] Generated {result['lines_of_code']} lines of code")
        print(f"[REAL LLM TEST] Test coverage estimate: {result['test_coverage_estimate']}%")

    def test_refactor_code_real(self):
        """Test refactoring code with real LLM."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        # Simple code to refactor
        existing_code = """
def calc(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b
"""

        result = agent.refactor_existing_code(
            existing_code=existing_code,
            refactor_goals=[
                "Use strategy pattern",
                "Add type hints",
                "Improve error handling"
            ],
            language="python",
            task_id="test_real_002"
        )

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("refactored_code", result)

        refactored = result["refactored_code"]
        self.assertGreater(len(refactored), len(existing_code))
        # Should have improvements
        self.assertGreater(len(result["changes_made"]), 0)

        print(f"\n[REAL LLM TEST] Made {len(result['changes_made'])} changes")


# ============================================================================
# CODE QUALITY TESTS
# ============================================================================

class TestDeveloperAgentCodeQuality(unittest.TestCase):
    """Test code quality metrics and standards."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = {
            "project_id": "test-project",
            "location": "us-central1",
            "model": "gemini-2.0-flash"
        }
        self.message_bus = MagicMock()

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generated_code_has_docstrings(self, mock_init, mock_model):
        """Test that generated code includes docstrings."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        code_response = MagicMock()
        code_response.text = '''
```python
def calculate_tax(income: float, tax_rate: float) -> float:
    """
    Calculate tax based on income and tax rate.

    Args:
        income: Total income amount
        tax_rate: Tax rate as decimal (e.g., 0.25 for 25%)

    Returns:
        Tax amount
    """
    if income < 0:
        raise ValueError("Income cannot be negative")
    return income * tax_rate
```
'''

        test_response = MagicMock()
        test_response.text = "# tests"

        mock_model_instance.generate_content.side_effect = [code_response, test_response]

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.implement_component(
            architecture_spec={"component_name": "TaxCalculator"},
            output_language="python"
        )

        # Verify docstrings present
        code = result["code"]
        self.assertIn('"""', code, "Should have docstrings")
        self.assertIn("Args:", code, "Should document parameters")

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generated_code_has_error_handling(self, mock_init, mock_model):
        """Test that generated code includes error handling."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        code_response = MagicMock()
        code_response.text = '''
```python
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```
'''

        test_response = MagicMock()
        test_response.text = "# tests"

        mock_model_instance.generate_content.side_effect = [code_response, test_response]

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.implement_component(
            architecture_spec={"component_name": "Calculator"},
            output_language="python"
        )

        code = result["code"]
        # Should have error handling
        self.assertTrue(
            "raise" in code or "except" in code or "ValueError" in code,
            "Should include error handling"
        )

    def test_multiple_languages_supported(self):
        """Test that agent supports multiple programming languages."""
        from agents.stage2_development.developer.agent import DeveloperAgent

        agent = DeveloperAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        # Test prompt building for different languages
        languages = ["python", "typescript", "java", "go", "cpp"]

        for lang in languages:
            prompt = agent._build_implementation_prompt(
                component_name="TestComponent",
                architecture_spec={},
                legacy_context={},
                output_language=lang
            )

            self.assertIn(lang, prompt.lower(), f"Prompt should mention {lang}")


class TestAPIDevAgentCodeGeneration(unittest.TestCase):
    """Test API Developer Agent code generation with different frameworks."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = MagicMock()
        self.context.project_id = "test-project"
        self.context.location = "us-central1"
        self.context.model = "gemini-2.0-flash"
        self.context.agent_id = "test_api_dev"
        self.context.get = lambda k, default=None: getattr(self.context, k, default)
        self.message_bus = MagicMock()

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_fastapi_rest_api(self, mock_init, mock_model):
        """Test generating FastAPI REST API."""
        from agents.backend.api_developer.agent import APIDevAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        api_response = MagicMock()
        api_response.text = '''
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float

products_db = {}

@app.get("/products")
async def get_products() -> List[Product]:
    return list(products_db.values())

@app.post("/products")
async def create_product(product: Product) -> Product:
    if product.id in products_db:
        raise HTTPException(status_code=400, detail="Product exists")
    products_db[product.id] = product
    return product
```
'''

        mock_model_instance.generate_content.return_value = api_response

        agent = APIDevAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.generate_rest_api(
            language="python",
            framework="fastapi",
            endpoints=[
                {"method": "GET", "path": "/products", "description": "List products"},
                {"method": "POST", "path": "/products", "description": "Create product"}
            ],
            auth_type="none",
            task_id="api_test_001"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("api_code", result)
        self.assertIn("FastAPI", result["api_code"])
        self.assertIn("@app.get", result["api_code"])

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_express_rest_api(self, mock_init, mock_model):
        """Test generating Express.js REST API."""
        from agents.backend.api_developer.agent import APIDevAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        api_response = MagicMock()
        api_response.text = '''
```typescript
import express from 'express';
const app = express();

app.use(express.json());

interface User {
    id: string;
    name: string;
    email: string;
}

const users: Map<string, User> = new Map();

app.get('/users', (req, res) => {
    res.json(Array.from(users.values()));
});

app.post('/users', (req, res) => {
    const user: User = req.body;
    users.set(user.id, user);
    res.status(201).json(user);
});
```
'''

        mock_model_instance.generate_content.return_value = api_response

        agent = APIDevAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.generate_rest_api(
            language="typescript",
            framework="express",
            endpoints=[
                {"method": "GET", "path": "/users"},
                {"method": "POST", "path": "/users"}
            ],
            auth_type="jwt",
            task_id="api_test_002"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("express", result["api_code"])


class TestCodeValidatorAgent(unittest.TestCase):
    """Test Code Validator Agent with real LLM validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = MagicMock()
        self.context.project_id = "test-project"
        self.context.location = "us-central1"
        self.context.model = "gemini-2.0-flash"
        self.context.agent_id = "test_code_validator"
        self.context.get = lambda k, default=None: getattr(self.context, k, default)
        self.message_bus = MagicMock()

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_validate_good_code(self, mock_init, mock_model):
        """Test validating good quality code."""
        from agents.stage2_development.validation.code_validator.agent import CodeValidatorAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock responses for each validation check
        correctness_response = MagicMock()
        correctness_response.text = """
**Requirements Met:** 0.95
**Business Logic Correct:** true
**Edge Cases Handled:** true

**Issues Found:**
None

**Recommendations:**
- Consider adding more unit tests
"""

        security_response = MagicMock()
        security_response.text = """
**Vulnerabilities Found:**
None

**Security Score:** 9.5
**SQL Injection Safe:** true
**XSS Safe:** true

**Recommendations:**
- Code is secure
"""

        error_response = MagicMock()
        error_response.text = """
**Exceptions Handled:** true
**Logging Present:** true
**Graceful Degradation:** true
**Error Handling Score:** 9.0

**Recommendations:**
- Good error handling
"""

        quality_response = MagicMock()
        quality_response.text = """
**Complexity:** 3
**Maintainability:** 85
**Duplication:** 0.02
**Quality Passed:** true

**Recommendations:**
- Well-written code
"""

        mock_model_instance.generate_content.side_effect = [
            correctness_response,
            security_response,
            error_response,
            quality_response
        ]

        agent = CodeValidatorAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        code = """
def process_payment(amount: float, currency: str) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return {"status": "success", "amount": amount}
"""

        result = agent.validate_code_complete(
            code=code,
            specification={"function": "process_payment", "validates_amount": True},
            language="python",
            task_id="val_001"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["validation_result"], "approved")
        self.assertGreater(result["summary"]["correctness_score"], 0.9)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_validate_code_with_issues(self, mock_init, mock_model):
        """Test validating code with security issues."""
        from agents.stage2_development.validation.code_validator.agent import CodeValidatorAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        correctness_response = MagicMock()
        correctness_response.text = """
**Requirements Met:** 0.7
**Business Logic Correct:** true
**Edge Cases Handled:** false

**Issues Found:**
- Missing input validation for edge cases
"""

        security_response = MagicMock()
        security_response.text = """
**Vulnerabilities Found:**
- HIGH: SQL Injection vulnerability in query construction
- MEDIUM: Missing input sanitization

**Security Score:** 4.5
**SQL Injection Safe:** false

**Recommendations:**
- Use parameterized queries
- Sanitize all user inputs
"""

        error_response = MagicMock()
        error_response.text = """
**Exceptions Handled:** false
**Logging Present:** false
**Error Handling Score:** 3.0

**Issues:**
- No exception handling
"""

        quality_response = MagicMock()
        quality_response.text = """
**Complexity:** 8
**Maintainability:** 55
**Quality Passed:** false

**Issues:**
- High complexity
- Poor naming conventions
"""

        mock_model_instance.generate_content.side_effect = [
            correctness_response,
            security_response,
            error_response,
            quality_response
        ]

        agent = CodeValidatorAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        bad_code = """
def query_db(user_input):
    sql = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return execute(sql)
"""

        result = agent.validate_code_complete(
            code=bad_code,
            specification={},
            language="python",
            task_id="val_002"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["validation_result"], "rejected")
        self.assertGreater(len(result["issues"]), 0)
        self.assertIn("SQL Injection", str(result["issues"]))


class TestQATesterAgent(unittest.TestCase):
    """Test QA Tester Agent test generation and planning."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = MagicMock()
        self.context.project_id = "test-project"
        self.context.location = "us-central1"
        self.context.model = "gemini-2.0-flash"
        self.context.agent_id = "test_qa_tester"
        self.context.get = lambda k, default=None: getattr(self.context, k, default)
        self.message_bus = MagicMock()

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_test_cases(self, mock_init, mock_model):
        """Test generating test cases from specification."""
        from agents.stage2_development.qa.tester.agent import QATesterAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        test_cases_response = MagicMock()
        test_cases_response.text = """
**Test ID:** TC001
**Name:** Verify successful payment processing
**Type:** functional
**Priority:** high
**Description:** Validate that valid payment is processed correctly
**Steps:**
1. Initialize payment processor with valid API key
2. Call process_payment with amount=100.0, currency="USD"
3. Verify response status is "success"
4. Verify transaction_id is returned

**Test ID:** TC002
**Name:** Reject negative payment amounts
**Type:** negative
**Priority:** high
**Description:** Ensure negative amounts are rejected
**Steps:**
1. Initialize payment processor
2. Call process_payment with amount=-50.0
3. Verify ValueError is raised
4. Verify error message contains "Amount must be positive"

**Test ID:** TC003
**Name:** Handle invalid currency codes
**Type:** negative
**Priority:** medium
**Description:** Validate currency validation
**Steps:**
1. Initialize payment processor
2. Call process_payment with currency="XXX"
3. Verify ValueError is raised
4. Verify error message mentions invalid currency

**Test ID:** TC004
**Name:** Process large transaction amounts
**Type:** edge_case
**Priority:** medium
**Description:** Test boundary with large amounts
**Steps:**
1. Initialize payment processor
2. Call process_payment with amount=999999.99
3. Verify successful processing
4. Verify amount is correctly stored

**Test ID:** TC005
**Name:** Prevent SQL injection in payment data
**Type:** security
**Priority:** high
**Description:** Ensure payment data is sanitized
**Steps:**
1. Initialize payment processor
2. Attempt process_payment with malicious SQL in metadata
3. Verify SQL is escaped/sanitized
4. Verify no database error occurs
"""

        mock_model_instance.generate_content.return_value = test_cases_response

        agent = QATesterAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.generate_test_cases(
            specification={
                "component_name": "PaymentProcessor",
                "methods": ["process_payment"],
                "description": "Process payment transactions"
            },
            language="python"
        )

        self.assertEqual(result["status"], "success")
        self.assertGreater(result["total_cases"], 0)
        self.assertIn("test_cases", result)

        # Verify test case structure
        test_cases = result["test_cases"]
        self.assertGreater(len(test_cases), 0)

        first_test = test_cases[0]
        self.assertIn("id", first_test)
        self.assertIn("name", first_test)
        self.assertIn("type", first_test)
        self.assertIn("priority", first_test)
        self.assertIn("steps", first_test)

        # Verify test coverage categorization
        self.assertIn("coverage", result)
        coverage = result["coverage"]
        self.assertGreater(len(coverage), 0)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_analyze_test_coverage_needs(self, mock_init, mock_model):
        """Test coverage analysis functionality."""
        from agents.stage2_development.qa.tester.agent import QATesterAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        coverage_response = MagicMock()
        coverage_response.text = """
**Critical Paths:**
- Payment validation flow (amount > 0, valid currency)
- Transaction processing and database commit
- Error handling for failed transactions

**Risk Areas:**
- Currency conversion logic (complex calculations)
- Database transaction rollback (edge cases)
- Concurrent payment processing (race conditions)

**Coverage Goals:**
- Line Coverage: 85
- Branch Coverage: 80

**Recommended Test Priorities:**
1. Payment validation (critical path)
2. Error recovery mechanisms
3. Concurrent processing scenarios
"""

        mock_model_instance.generate_content.return_value = coverage_response

        agent = QATesterAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        code_sample = """
def process_payment(amount, currency):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if currency not in valid_currencies:
        raise ValueError("Invalid currency")
    return {"status": "success"}
"""

        result = agent.analyze_test_coverage_needs(
            specification={"component": "PaymentProcessor"},
            code=code_sample,
            language="python"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("coverage_needs", result)

        coverage_needs = result["coverage_needs"]
        self.assertIn("coverage_goals", coverage_needs)
        self.assertIn("critical_paths", coverage_needs)
        self.assertIn("risk_areas", coverage_needs)

        # Verify coverage goals
        goals = coverage_needs["coverage_goals"]
        self.assertIn("line_coverage", goals)
        self.assertGreater(goals["line_coverage"], 0)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_load_test_plan(self, mock_init, mock_model):
        """Test load test plan generation."""
        from agents.stage2_development.qa.tester.agent import QATesterAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        load_test_response = MagicMock()
        load_test_response.text = """
**Test Scenarios:**
1. **Normal Load**
   - Users: 100
   - Duration: 10 minutes
   - Expected RPS: 500

2. **Peak Load**
   - Users: 500
   - Duration: 5 minutes
   - Expected RPS: 2000

3. **Stress Test**
   - Users: 1000
   - Duration: 3 minutes
   - Expected RPS: 5000

**Metrics:**
- Response Time Target: < 200ms
- Error Rate Target: < 0.1%
- CPU Utilization: < 70%

**Success Criteria:**
- P95 response time under 200ms during normal load
- Zero errors during normal load scenario
- System remains stable during stress test
- Auto-recovery after load spike
"""

        mock_model_instance.generate_content.return_value = load_test_response

        agent = QATesterAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.run_load_tests(
            endpoint="/api/payments",
            config={
                "expected_rps": 1000,
                "sla_response_ms": 200,
                "duration_minutes": 10
            }
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("load_test_plan", result)

        plan = result["load_test_plan"]
        self.assertIn("scenarios", plan)
        self.assertIn("success_criteria", plan)

        # Verify simulated results
        self.assertIn("simulated_results", result)
        sim_results = result["simulated_results"]
        self.assertIn("requests_per_second", sim_results)
        self.assertIn("average_response_ms", sim_results)
        self.assertIn("p95_response_ms", sim_results)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_comprehensive_test_plan(self, mock_init, mock_model):
        """Test comprehensive test plan generation."""
        from agents.stage2_development.qa.tester.agent import QATesterAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock test cases generation
        test_cases_response = MagicMock()
        test_cases_response.text = """
**Test ID:** TC001
**Name:** Basic validation test
**Type:** functional
**Priority:** high
**Description:** Test basic functionality
**Steps:**
1. Execute test
2. Verify result
"""

        # Mock coverage analysis
        coverage_response = MagicMock()
        coverage_response.text = """
**Critical Paths:**
- Main execution path

**Risk Areas:**
- Error handling

**Coverage Goals:**
- Line Coverage: 80
- Branch Coverage: 75
"""

        # Mock test plan
        test_plan_response = MagicMock()
        test_plan_response.text = """
**Test Strategy:**
Comprehensive testing approach covering unit, integration, and system tests.
Focus on critical paths first, then edge cases.

**Test Phases:**
1. **Phase 1**: Unit Testing (3 days)
   - Test individual components
   - Mock dependencies
2. **Phase 2**: Integration Testing (4 days)
   - Test component interactions
   - Database integration
3. **Phase 3**: System Testing (3 days)
   - End-to-end scenarios
   - Performance validation

**Resource Requirements:**
- Environments: Dev, Staging, Performance test environment
- Tools: pytest, locust, coverage.py

**Estimated Timeline:** 10-12 days

**Risks:**
- Risk 1: Test environment availability - Reserve environments in advance
- Risk 2: Test data quality - Generate synthetic data before testing
"""

        mock_model_instance.generate_content.side_effect = [
            test_cases_response,
            coverage_response,
            test_plan_response
        ]

        agent = QATesterAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.generate_comprehensive_tests(
            specification={
                "component_name": "PaymentService",
                "description": "Payment processing service"
            },
            code="def process_payment(): pass",
            language="python",
            task_id="test_plan_001"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("test_plan", result)
        self.assertIn("test_cases", result)
        self.assertIn("total_cases", result)

        test_plan = result["test_plan"]
        self.assertIn("test_strategy", test_plan)
        self.assertIn("phases", test_plan)
        self.assertIn("resources", test_plan)
        self.assertIn("timeline", test_plan)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_generate_test_report(self, mock_init, mock_model):
        """Test generating test execution report."""
        from agents.stage2_development.qa.tester.agent import QATesterAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        report_response = MagicMock()
        report_response.text = """
**Validation Result:** approved

**Key Findings:**
All 45 test cases executed successfully with 98% pass rate.
Code coverage achieved 87% line coverage and 82% branch coverage, exceeding targets.
Performance tests show system handles 1200 RPS with P95 latency of 150ms.
Minor issues found in error logging, but non-critical.

**Recommendations:**
1. Add more edge case tests for currency conversion edge cases
2. Increase test coverage for error recovery paths to 90%
3. Implement automated regression test suite
4. Add integration tests for payment gateway timeouts
"""

        mock_model_instance.generate_content.return_value = report_response

        agent = QATesterAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.generate_test_report(
            test_cases={"total_cases": 45},
            execution={
                "test_execution": {
                    "total": 45,
                    "passed": 44,
                    "failed": 1,
                    "environment": "staging"
                }
            },
            coverage={
                "coverage": {
                    "line_coverage": 0.87,
                    "branch_coverage": 0.82
                }
            },
            load_test={
                "load_test_plan": {
                    "meets_sla": True
                }
            }
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("test_report", result)

        report = result["test_report"]
        self.assertIn("summary", report)
        self.assertIn("validation_result", report)
        self.assertIn("recommendations", report)

        # Verify summary
        summary = report["summary"]
        self.assertEqual(summary["total_tests"], 45)
        self.assertEqual(summary["passed"], 44)
        self.assertEqual(summary["failed"], 1)

        # Verify validation result
        self.assertEqual(report["validation_result"], "approved")

        # Verify recommendations exist
        self.assertGreater(len(report["recommendations"]), 0)

    @patch('vertexai.generative_models.GenerativeModel')
    @patch('google.cloud.aiplatform.init')
    def test_test_case_categorization(self, mock_init, mock_model):
        """Test that test cases are properly categorized."""
        from agents.stage2_development.qa.tester.agent import QATesterAgent

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        test_cases_response = MagicMock()
        test_cases_response.text = """
**Test ID:** TC001
**Name:** Happy path test
**Type:** functional
**Priority:** high
**Steps:**
1. Execute
2. Verify

**Test ID:** TC002
**Name:** Error test
**Type:** negative
**Priority:** high
**Steps:**
1. Trigger error
2. Verify handling

**Test ID:** TC003
**Name:** Security test
**Type:** security
**Priority:** high
**Steps:**
1. Attempt attack
2. Verify blocked

**Test ID:** TC004
**Name:** Edge case test
**Type:** edge_case
**Priority:** medium
**Steps:**
1. Test boundary
2. Verify behavior
"""

        mock_model_instance.generate_content.return_value = test_cases_response

        agent = QATesterAgent(
            context=self.context,
            message_bus=self.message_bus,
            orchestrator_id="test_orch"
        )

        result = agent.generate_test_cases(
            specification={"component": "TestComponent"},
            language="python"
        )

        self.assertEqual(result["status"], "success")

        # Verify coverage categorization
        coverage = result["coverage"]
        self.assertIn("functional", coverage)
        self.assertIn("negative", coverage)
        self.assertIn("security", coverage)
        self.assertIn("edge_case", coverage)

        # Verify counts
        self.assertEqual(coverage["functional"], 1)
        self.assertEqual(coverage["negative"], 1)
        self.assertEqual(coverage["security"], 1)
        self.assertEqual(coverage["edge_case"], 1)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
