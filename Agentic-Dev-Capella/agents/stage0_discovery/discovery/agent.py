"""
agents/stage0_discovery/discovery/agent_llm.py

Enhanced Discovery agent with LLM-powered analysis for intelligent technology detection.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration

# Import existing file scanning functions
from .agent import (
    scan_repository,
    detect_dependencies,
    create_asset_metadata,
    _detect_languages,
    _detect_frameworks,
    _detect_databases
)


class DiscoveryAgentLLM(A2AEnabledAgent):
    """
    Enhanced Discovery Agent with LLM-powered technology analysis.

    Capabilities:
    - Comprehensive file system scanning (existing logic)
    - LLM-powered technology stack inference
    - Intelligent business domain detection
    - Modernization complexity assessment with LLM
    - Smart recommendations based on actual code analysis
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Discovery Agent with LLM."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            agent_context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id") if hasattr(context, 'get') else getattr(context, 'project_id', None),
            location=context.get("location", "us-central1") if hasattr(context, 'get') else getattr(context, 'location', "us-central1")
        )

        self.model = GenerativeModel(model_name)

    def discover_and_analyze(
        self,
        repo_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete discovery and analysis workflow.

        Args:
            repo_path: Path to legacy repository
            task_id: Optional task ID

        Returns:
            Complete discovery report with LLM-powered insights
        """
        print(f"[Discovery Agent] Starting comprehensive discovery of {repo_path}")

        # Step 1: Scan repository (existing logic - fast and accurate)
        scan_result = scan_repository(repo_path)

        if scan_result.get("scan_status") != "completed":
            return scan_result

        inventory = scan_result.get("inventory", {})

        # Step 2: Basic technology detection (existing keyword matching)
        basic_tech_stack = self._get_basic_tech_stack(inventory)

        # Step 3: LLM-powered technology inference (intelligent analysis)
        tech_stack_enhanced = self.identify_technology_stack_llm(
            inventory=inventory,
            basic_detection=basic_tech_stack,
            task_id=task_id
        )

        # Step 4: Business domain inference using LLM
        business_domain = self.infer_business_domain(
            inventory=inventory,
            task_id=task_id
        )

        # Step 5: Modernization complexity assessment using LLM
        complexity_assessment = self.assess_modernization_complexity_llm(
            tech_stack=tech_stack_enhanced.get("technology_stack", {}),
            business_domain=business_domain.get("domain", {}),
            task_id=task_id
        )

        # Combine all results
        return {
            "status": "success",
            "repo_path": repo_path,
            "scan_results": scan_result,
            "technology_stack": tech_stack_enhanced.get("technology_stack", {}),
            "business_domain": business_domain.get("domain", {}),
            "modernization_assessment": complexity_assessment,
            "timestamp": datetime.utcnow().isoformat()
        }

    def identify_technology_stack_llm(
        self,
        inventory: Dict[str, List],
        basic_detection: Dict[str, List],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to intelligently identify technology stack."""
        print(f"[Discovery Agent] Analyzing technology stack with LLM")

        # Sample file names and paths for LLM analysis
        sample_files = self._sample_files_for_analysis(inventory)

        prompt = self._build_tech_stack_prompt(sample_files, basic_detection)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        tech_stack = self._parse_tech_stack_response(response.text, basic_detection)

        return {
            "status": "success",
            "technology_stack": tech_stack
        }

    def infer_business_domain(
        self,
        inventory: Dict[str, List],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to infer business domain from code and documentation."""
        print(f"[Discovery Agent] Inferring business domain")

        # Sample code snippets and documentation
        samples = self._sample_content_for_domain_analysis(inventory)

        prompt = self._build_domain_inference_prompt(samples)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        domain_info = self._parse_domain_response(response.text)

        return {
            "status": "success",
            "domain": domain_info
        }

    def assess_modernization_complexity_llm(
        self,
        tech_stack: Dict[str, List],
        business_domain: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to assess modernization complexity and generate recommendations."""
        print(f"[Discovery Agent] Assessing modernization complexity")

        prompt = self._build_complexity_assessment_prompt(tech_stack, business_domain)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.4)
        )

        assessment = self._parse_complexity_response(response.text)

        return assessment

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_basic_tech_stack(self, inventory: Dict[str, List]) -> Dict[str, List]:
        """Get basic technology detection using existing keyword matching."""
        source_files = inventory.get("source_code", [])
        config_files = inventory.get("configuration_files", [])
        db_files = inventory.get("database_schemas", [])

        return {
            "languages": _detect_languages(source_files),
            "frameworks": _detect_frameworks(source_files, config_files),
            "databases": _detect_databases(db_files, config_files, source_files)
        }

    def _sample_files_for_analysis(self, inventory: Dict[str, List], max_samples: int = 20) -> List[Dict]:
        """Sample representative files for LLM analysis."""
        samples = []

        # Get file names and paths from each category
        for category, files in inventory.items():
            category_samples = files[:5] if len(files) > 5 else files
            for file_info in category_samples:
                if isinstance(file_info, dict):
                    samples.append({
                        "category": category,
                        "name": file_info.get("name", ""),
                        "path": file_info.get("path", ""),
                        "extension": file_info.get("extension", "")
                    })

        return samples[:max_samples]

    def _sample_content_for_domain_analysis(self, inventory: Dict[str, List]) -> Dict[str, List[str]]:
        """Sample actual file content for domain inference."""
        samples = {
            "file_names": [],
            "code_snippets": [],
            "documentation": []
        }

        # Collect file names (they often contain domain keywords)
        for category, files in inventory.items():
            for file_info in files[:10]:
                if isinstance(file_info, dict):
                    samples["file_names"].append(file_info.get("name", ""))

        # Read small code snippets (first 50 lines of first 3 source files)
        source_files = inventory.get("source_code", [])[:3]
        for file_info in source_files:
            if isinstance(file_info, dict):
                path = Path(file_info.get("path", ""))
                if path.exists() and path.stat().st_size < 100000:  # Only read small files
                    try:
                        content = path.read_text(errors='ignore')
                        lines = content.split('\n')[:50]
                        samples["code_snippets"].append('\n'.join(lines))
                    except:
                        pass

        # Read documentation files
        docs = inventory.get("documentation", [])[:2]
        for file_info in docs:
            if isinstance(file_info, dict):
                path = Path(file_info.get("path", ""))
                if path.exists() and path.stat().st_size < 50000:
                    try:
                        content = path.read_text(errors='ignore')
                        samples["documentation"].append(content[:2000])
                    except:
                        pass

        return samples

    # ========================================================================
    # PROMPT BUILDERS
    # ========================================================================

    def _build_tech_stack_prompt(self, sample_files: List[Dict], basic_detection: Dict) -> str:
        """Build prompt for technology stack analysis."""

        files_summary = "\n".join([
            f"- {f.get('name', '')} ({f.get('category', '')}) - {f.get('path', '')}"
            for f in sample_files[:20]
        ])

        basic_tech = json.dumps(basic_detection, indent=2)

        prompt = f"""You are a technology stack expert analyzing a legacy codebase.

**Sample Files from Codebase:**
{files_summary}

**Basic Detection Results:**
{basic_tech}

**Task**: Analyze these files to identify the COMPLETE technology stack including:

1. **Programming Languages** - All languages used (not just file extensions)
2. **Frameworks & Libraries** - Web frameworks, ORM, testing frameworks
3. **Databases** - Relational, NoSQL, cache systems
4. **Infrastructure** - Docker, Kubernetes, cloud platforms
5. **Build Tools** - Maven, Gradle, NPM, Make
6. **Architecture Patterns** - Monolith, Microservices, SOA
7. **Hidden Technologies** - Look for clues in file paths, names, and patterns

**Response Format:**

**Languages:** [List with confidence scores]
**Frameworks:** [List with evidence]
**Databases:** [List with evidence]
**Infrastructure:** [List]
**Build Tools:** [List]
**Architecture Pattern:** [Pattern name with reasoning]
**Additional Technologies:** [Any other tech detected]

Provide evidence for each technology identified. Be specific and accurate.
"""

        return prompt

    def _build_domain_inference_prompt(self, samples: Dict[str, List[str]]) -> str:
        """Build prompt for business domain inference."""

        file_names = '\n'.join(samples.get("file_names", [])[:30])
        code_sample = samples.get("code_snippets", [""])[0][:2000] if samples.get("code_snippets") else "No code samples"
        doc_sample = samples.get("documentation", [""])[0][:1500] if samples.get("documentation") else "No documentation"

        prompt = f"""You are a business analyst expert at identifying business domains from code.

**File Names:**
{file_names}

**Code Sample:**
{code_sample}

**Documentation Sample:**
{doc_sample}

**Task**: Infer the business domain and key business entities from this legacy system.

**Analysis Criteria:**
1. What industry/domain is this system for? (e.g., Finance, Healthcare, E-commerce)
2. What are the core business entities? (e.g., Customer, Order, Payment)
3. What are the main business processes? (e.g., order processing, inventory management)
4. What business rules or constraints exist?

**Response Format:**

**Industry/Domain:** [Domain name with confidence]
**Core Entities:** [List of business entities]
**Business Processes:** [List of key processes]
**Business Rules:** [List of identified rules]
**Domain Complexity:** [low/medium/high with reasoning]

Base your analysis on actual evidence from the files, not assumptions.
"""

        return prompt

    def _build_complexity_assessment_prompt(self, tech_stack: Dict, business_domain: Dict) -> str:
        """Build prompt for modernization complexity assessment."""

        tech_summary = json.dumps(tech_stack, indent=2)
        domain_summary = json.dumps(business_domain, indent=2)

        prompt = f"""You are a modernization consultant assessing legacy system complexity.

**Technology Stack:**
{tech_summary}

**Business Domain:**
{domain_summary}

**Task**: Assess the modernization complexity and provide actionable recommendations.

**Assessment Factors:**
1. Technology Obsolescence (COBOL, old Java versions, etc.)
2. Number of different technologies (integration complexity)
3. Database complexity (proprietary vs standard)
4. Business domain complexity
5. Testing coverage expectations
6. Migration risk level

**Response Format:**

**Complexity Level:** [very_low/low/medium/high/very_high]

**Risk Factors:**
- Factor 1: [Description with severity]
- Factor 2: [Description with severity]

**Estimated Effort:** [Small/Medium/Large/Very Large]

**Modernization Strategy:** [Recommended approach]

**Prioritized Recommendations:**
1. [Highest priority recommendation]
2. [Second priority]
3. [Third priority]

**Technology Migration Path:**
- From: [Old tech]
- To: [Modern equivalent]
- Reason: [Why]

Be specific, practical, and focus on reducing risk while maximizing business value.
"""

        return prompt

    # ========================================================================
    # RESPONSE PARSERS
    # ========================================================================

    def _parse_tech_stack_response(self, response_text: str, basic_detection: Dict) -> Dict[str, List[str]]:
        """Parse LLM response for technology stack."""

        tech_stack = {
            "languages": basic_detection.get("languages", []),
            "frameworks": basic_detection.get("frameworks", []),
            "databases": basic_detection.get("databases", []),
            "infrastructure": [],
            "build_tools": [],
            "architecture_pattern": "Unknown"
        }

        # Extract from LLM response
        import re

        # Languages
        lang_match = re.search(r"\*\*Languages:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if lang_match:
            langs = re.findall(r"[-•]\s*([A-Za-z0-9+#\.]+)", lang_match.group(1))
            tech_stack["languages"] = list(set(tech_stack["languages"] + langs))

        # Frameworks
        framework_match = re.search(r"\*\*Frameworks:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if framework_match:
            frameworks = re.findall(r"[-•]\s*([A-Za-z0-9\./\-]+)", framework_match.group(1))
            tech_stack["frameworks"] = list(set(tech_stack["frameworks"] + frameworks))

        # Databases
        db_match = re.search(r"\*\*Databases:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if db_match:
            dbs = re.findall(r"[-•]\s*([A-Za-z0-9\s]+)", db_match.group(1))
            tech_stack["databases"] = list(set(tech_stack["databases"] + [db.strip() for db in dbs]))

        # Infrastructure
        infra_match = re.search(r"\*\*Infrastructure:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if infra_match:
            infra = re.findall(r"[-•]\s*([A-Za-z0-9\s/\-]+)", infra_match.group(1))
            tech_stack["infrastructure"] = [i.strip() for i in infra if i.strip()]

        # Architecture Pattern
        arch_match = re.search(r"\*\*Architecture Pattern:\*\*\s*([^\n]+)", response_text)
        if arch_match:
            tech_stack["architecture_pattern"] = arch_match.group(1).strip()

        return tech_stack

    def _parse_domain_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for business domain."""

        domain_info = {
            "industry": "Unknown",
            "core_entities": [],
            "business_processes": [],
            "business_rules": [],
            "complexity": "medium"
        }

        import re

        # Industry
        industry_match = re.search(r"\*\*Industry/Domain:\*\*\s*([^\n]+)", response_text)
        if industry_match:
            domain_info["industry"] = industry_match.group(1).strip()

        # Core Entities
        entities_match = re.search(r"\*\*Core Entities:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if entities_match:
            entities = re.findall(r"[-•]\s*([A-Za-z0-9\s]+)", entities_match.group(1))
            domain_info["core_entities"] = [e.strip() for e in entities if e.strip()]

        # Business Processes
        processes_match = re.search(r"\*\*Business Processes:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if processes_match:
            processes = re.findall(r"[-•]\s*([^\n]+)", processes_match.group(1))
            domain_info["business_processes"] = [p.strip() for p in processes if p.strip()][:10]

        # Domain Complexity
        complexity_match = re.search(r"\*\*Domain Complexity:\*\*\s*(\w+)", response_text)
        if complexity_match:
            domain_info["complexity"] = complexity_match.group(1).lower()

        return domain_info

    def _parse_complexity_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for complexity assessment."""

        assessment = {
            "complexity_level": "medium",
            "risk_factors": [],
            "estimated_effort": "Medium",
            "recommendations": [],
            "migration_path": []
        }

        import re

        # Complexity Level
        complexity_match = re.search(r"\*\*Complexity Level:\*\*\s*([a-z_]+)", response_text, re.IGNORECASE)
        if complexity_match:
            assessment["complexity_level"] = complexity_match.group(1).lower()

        # Risk Factors
        risk_match = re.search(r"\*\*Risk Factors:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if risk_match:
            risks = re.findall(r"[-•]\s*([^\n]+)", risk_match.group(1))
            assessment["risk_factors"] = [r.strip() for r in risks if r.strip()][:10]

        # Estimated Effort
        effort_match = re.search(r"\*\*Estimated Effort:\*\*\s*([^\n]+)", response_text)
        if effort_match:
            assessment["estimated_effort"] = effort_match.group(1).strip()

        # Recommendations
        rec_match = re.search(r"\*\*Prioritized Recommendations:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if rec_match:
            recs = re.findall(r"\d+\.\s*([^\n]+)", rec_match.group(1))
            assessment["recommendations"] = [r.strip() for r in recs if r.strip()][:10]

        return assessment

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_discovery_agent_llm(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced discovery agent."""
    return DiscoveryAgentLLM(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )
