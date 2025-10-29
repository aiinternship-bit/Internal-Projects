#!/usr/bin/env python3
"""
scripts/run_dynamic_pipeline.py

Dynamic multi-agent pipeline runner with multimodal input support.
Uses AI-powered agent selection and parallel execution.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from google.cloud import aiplatform
from vertexai.preview import reasoning_engines

from shared.utils.vertex_a2a_protocol import VertexA2AMessageBus
from shared.services.agent_registry import AgentRegistryService
from shared.models.agent_capability import AgentCapability
from shared.models.task_requirements import TaskRequirements
from shared.models.execution_plan import ExecutionPlan, ExecutionPhase


class DynamicMultiAgentPipeline:
    """
    Dynamic pipeline that processes multimodal inputs and orchestrates agents
    based on capability matching and intelligent task analysis.
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        agent_registry_path: str,
        output_dir: str,
        mode: str = "dynamic"
    ):
        """
        Initialize dynamic pipeline.

        Args:
            project_id: GCP project ID
            location: Vertex AI location
            agent_registry_path: Path to agent_registry.json
            output_dir: Output directory for artifacts
            mode: "dynamic" or "static"
        """
        self.project_id = project_id
        self.location = location
        self.output_dir = Path(output_dir)
        self.mode = mode

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        # Load agent registry
        self.agent_registry = AgentRegistryService(persistence_path=agent_registry_path)

        # Initialize message bus
        self.message_bus = VertexA2AMessageBus(
            project_id=project_id,
            topic_name="dynamic-pipeline-messages"
        )

        # Initialize orchestrator (lazy loading)
        self._orchestrator = None
        self._orchestrator_id = None

        # Execution state
        self.execution_start = None
        self.execution_results: Dict[str, Any] = {}

        print(f"✓ Dynamic Pipeline initialized (mode: {mode})")
        print(f"  Project: {project_id}")
        print(f"  Location: {location}")
        print(f"  Output: {output_dir}")

    @property
    def orchestrator(self):
        """Lazy load orchestrator."""
        if self._orchestrator is None:
            # Load Dynamic Orchestrator from agent registry
            orchestrator_info = self.agent_registry.get_agent("dynamic_orchestrator_agent")
            if orchestrator_info:
                self._orchestrator_id = orchestrator_info["resource_name"]
                self._orchestrator = reasoning_engines.ReasoningEngine(self._orchestrator_id)
                print(f"✓ Loaded Dynamic Orchestrator: {self._orchestrator_id}")
            else:
                raise RuntimeError(
                    "Dynamic Orchestrator not found in agent registry. "
                    "Please deploy agents first using deploy_vertex_agents.py"
                )
        return self._orchestrator

    def run(
        self,
        task_description: str,
        input_files: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run dynamic orchestration pipeline.

        Args:
            task_description: Natural language description of the task
            input_files: List of input file paths (images, PDFs, videos, etc.)
            context: Additional context for the task
            constraints: Constraints (max_cost_usd, max_duration_hours, etc.)

        Returns:
            Execution results with artifacts, metrics, and report

        Flow:
            1. Process multimodal inputs (images, PDFs, videos)
            2. Analyze task requirements (TaskAnalyzer)
            3. Select agents dynamically (AgentSelector)
            4. Create execution plan (ExecutionPlanner)
            5. Execute plan with parallel coordination
            6. Track progress and handle failures
            7. Generate execution report
        """
        self.execution_start = datetime.now()
        input_files = input_files or []
        context = context or {}
        constraints = constraints or {}

        print("\n" + "=" * 80)
        print("DYNAMIC MULTI-AGENT PIPELINE")
        print("=" * 80)
        print(f"\nTask: {task_description}")
        print(f"Input files: {len(input_files)}")
        if constraints:
            print(f"Constraints: {constraints}")

        try:
            # Step 1: Process multimodal inputs
            print("\n[1/6] Processing multimodal inputs...")
            processed_inputs = self._process_multimodal_inputs(input_files)
            print(f"✓ Processed {len(processed_inputs)} inputs")

            # Step 2: Analyze task with orchestrator
            print("\n[2/6] Analyzing task requirements...")
            analysis_result = self.orchestrator.query({
                "action": "analyze_task",
                "task_description": task_description,
                "processed_inputs": processed_inputs,
                "context": context,
                "constraints": constraints
            })

            task_requirements = analysis_result.get("task_requirements")
            print(f"✓ Task analyzed")
            print(f"  Required capabilities: {', '.join(task_requirements.get('required_capabilities', [])[:5])}")
            print(f"  Complexity: {task_requirements.get('estimated_complexity', 'medium')}")

            # Step 3: Select agents
            print("\n[3/6] Selecting optimal agents...")
            selection_result = self.orchestrator.query({
                "action": "select_agents",
                "task_requirements": task_requirements
            })

            selected_agents = selection_result.get("selected_agents", [])
            print(f"✓ Selected {len(selected_agents)} agents")
            for agent in selected_agents[:5]:
                print(f"  - {agent['agent_name']} (score: {agent.get('score', 0):.2f})")

            # Step 4: Create execution plan
            print("\n[4/6] Creating execution plan...")
            planning_result = self.orchestrator.query({
                "action": "create_execution_plan",
                "selected_agents": selected_agents,
                "task_requirements": task_requirements
            })

            execution_plan = planning_result.get("execution_plan")
            print(f"✓ Execution plan created")
            print(f"  Phases: {execution_plan.get('total_phases', 0)}")
            print(f"  Estimated duration: {execution_plan.get('total_estimated_duration_minutes', 0):.1f} minutes")
            print(f"  Estimated cost: ${execution_plan.get('total_estimated_cost_usd', 0):.2f}")
            print(f"  Max parallel agents: {execution_plan.get('max_parallel_agents', 0)}")

            # Step 5: Execute plan
            print("\n[5/6] Executing plan...")
            execution_results = self._execute_plan(execution_plan, task_description)
            print(f"✓ Execution complete")

            # Step 6: Generate report
            print("\n[6/6] Generating execution report...")
            report = self._generate_execution_report(
                task_description=task_description,
                task_requirements=task_requirements,
                selected_agents=selected_agents,
                execution_plan=execution_plan,
                execution_results=execution_results,
                constraints=constraints
            )
            print(f"✓ Report generated")

            # Save report
            report_path = self.output_dir / "execution_report.json"
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"  Report saved to: {report_path}")

            print("\n" + "=" * 80)
            print("PIPELINE COMPLETE")
            print("=" * 80)
            print(f"\nTotal duration: {report['execution_metrics']['total_duration_minutes']:.1f} minutes")
            print(f"Total cost: ${report['execution_metrics']['total_cost_usd']:.2f}")
            print(f"Success rate: {report['execution_metrics']['success_rate']*100:.1f}%")
            print(f"\nArtifacts: {self.output_dir}")

            return report

        except Exception as e:
            print(f"\n✗ Pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _process_multimodal_inputs(self, input_files: List[str]) -> Dict[str, Any]:
        """
        Process multimodal inputs (images, PDFs, videos, audio).

        Routes each file to appropriate processor agent:
        - Images (.png, .jpg, .svg) → vision_agent
        - PDFs (.pdf) → pdf_parser_agent
        - Videos (.mp4, .mov) → video_processor_agent
        - Audio (.mp3, .wav) → audio_transcriber_agent
        - Design files (.fig) → design_parser_agent

        Returns:
            Dict with processed requirements from all inputs
        """
        if not input_files:
            return {"processed_files": [], "extracted_requirements": []}

        processed = []
        extracted_requirements = []

        for input_file in input_files:
            file_path = Path(input_file)
            if not file_path.exists():
                print(f"  ⚠ File not found: {input_file}")
                continue

            file_type = file_path.suffix.lower()
            print(f"  Processing {file_path.name} ({file_type})...")

            # Route to appropriate processor
            if file_type in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
                # Vision agent
                agent = self.agent_registry.get_agent("vision_agent")
                if agent:
                    result = self._process_with_agent(agent, file_path, "image")
                    processed.append({"file": str(file_path), "type": "image", "result": result})
                    extracted_requirements.extend(result.get("requirements", []))

            elif file_type == '.pdf':
                # PDF parser agent
                agent = self.agent_registry.get_agent("pdf_parser_agent")
                if agent:
                    result = self._process_with_agent(agent, file_path, "pdf")
                    processed.append({"file": str(file_path), "type": "pdf", "result": result})
                    extracted_requirements.extend(result.get("requirements", []))

            elif file_type in ['.mp4', '.mov', '.avi']:
                # Video processor agent
                agent = self.agent_registry.get_agent("video_processor_agent")
                if agent:
                    result = self._process_with_agent(agent, file_path, "video")
                    processed.append({"file": str(file_path), "type": "video", "result": result})
                    extracted_requirements.extend(result.get("requirements", []))

            elif file_type in ['.mp3', '.wav', '.m4a']:
                # Audio transcriber agent
                agent = self.agent_registry.get_agent("audio_transcriber_agent")
                if agent:
                    result = self._process_with_agent(agent, file_path, "audio")
                    processed.append({"file": str(file_path), "type": "audio", "result": result})
                    extracted_requirements.extend(result.get("requirements", []))

            else:
                print(f"    ⚠ Unsupported file type: {file_type}")

        return {
            "processed_files": processed,
            "extracted_requirements": extracted_requirements,
            "total_files": len(input_files),
            "successfully_processed": len(processed)
        }

    def _process_with_agent(
        self,
        agent_info: Dict[str, Any],
        file_path: Path,
        input_type: str
    ) -> Dict[str, Any]:
        """Process single file with appropriate agent."""
        try:
            agent_id = agent_info.get("resource_name")
            agent = reasoning_engines.ReasoningEngine(agent_id)

            # Query agent to process file
            result = agent.query({
                "action": "process_input",
                "file_path": str(file_path),
                "input_type": input_type
            })

            return result

        except Exception as e:
            print(f"    ✗ Error processing with agent: {str(e)}")
            return {"error": str(e), "requirements": []}

    def _execute_plan(
        self,
        execution_plan: Dict[str, Any],
        task_description: str
    ) -> Dict[str, Any]:
        """
        Execute execution plan with parallel phase coordination.

        For each phase:
        - Start all assignments in parallel (up to max_parallel_agents)
        - Track completion via A2A messages
        - Handle failures and retries
        - Move to next phase when all complete

        Returns:
            Execution results with metrics and artifacts
        """
        phases = execution_plan.get("phases", [])
        results = {
            "phase_results": [],
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "artifacts": []
        }

        for phase_num, phase in enumerate(phases, 1):
            print(f"\n  Phase {phase_num}/{len(phases)}: {len(phase['assignments'])} agents")

            phase_start = time.time()
            phase_results = []

            # Execute all assignments in this phase (in parallel)
            for assignment in phase['assignments']:
                agent_name = assignment.get('agent_name')
                task_id = assignment.get('task_id')

                print(f"    → {agent_name} starting...")

                try:
                    # Send task assignment via orchestrator
                    result = self.orchestrator.query({
                        "action": "execute_assignment",
                        "assignment": assignment,
                        "task_description": task_description
                    })

                    phase_results.append({
                        "agent": agent_name,
                        "task_id": task_id,
                        "status": "completed",
                        "result": result
                    })

                    results["completed_tasks"] += 1
                    results["artifacts"].extend(result.get("artifacts", []))
                    print(f"    ✓ {agent_name} completed")

                except Exception as e:
                    phase_results.append({
                        "agent": agent_name,
                        "task_id": task_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    results["failed_tasks"] += 1
                    print(f"    ✗ {agent_name} failed: {str(e)}")

                results["total_tasks"] += 1

            phase_duration = time.time() - phase_start
            results["phase_results"].append({
                "phase_number": phase_num,
                "duration_seconds": phase_duration,
                "results": phase_results
            })

            print(f"  ✓ Phase {phase_num} complete ({phase_duration:.1f}s)")

        return results

    def _generate_execution_report(
        self,
        task_description: str,
        task_requirements: Dict[str, Any],
        selected_agents: List[Dict[str, Any]],
        execution_plan: Dict[str, Any],
        execution_results: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive execution report.

        Includes:
        - Task description and requirements
        - Selected agents and scores
        - Execution timeline
        - Performance metrics
        - Cost breakdown
        - Critical path analysis
        - Artifacts generated
        - Recommendations
        """
        total_duration = (datetime.now() - self.execution_start).total_seconds() / 60.0

        report = {
            "pipeline_version": "1.0.0",
            "execution_timestamp": self.execution_start.isoformat(),
            "task": {
                "description": task_description,
                "requirements": task_requirements,
                "constraints": constraints
            },
            "agent_selection": {
                "total_agents_available": len(self.agent_registry.get_all_agents()),
                "selected_agents": selected_agents,
                "selection_criteria": {
                    "capability_match": "40%",
                    "performance_history": "30%",
                    "availability": "20%",
                    "cost_efficiency": "10%"
                }
            },
            "execution_plan": execution_plan,
            "execution_results": execution_results,
            "execution_metrics": {
                "total_duration_minutes": total_duration,
                "total_tasks": execution_results["total_tasks"],
                "completed_tasks": execution_results["completed_tasks"],
                "failed_tasks": execution_results["failed_tasks"],
                "success_rate": (
                    execution_results["completed_tasks"] / execution_results["total_tasks"]
                    if execution_results["total_tasks"] > 0 else 0.0
                ),
                "total_cost_usd": execution_plan.get("total_estimated_cost_usd", 0.0),
                "parallelism_efficiency": self._calculate_parallelism_efficiency(execution_plan, execution_results)
            },
            "artifacts": {
                "total_artifacts": len(execution_results.get("artifacts", [])),
                "artifact_list": execution_results.get("artifacts", []),
                "output_directory": str(self.output_dir)
            },
            "critical_path": execution_plan.get("critical_path", []),
            "recommendations": self._generate_recommendations(
                execution_plan,
                execution_results,
                total_duration
            )
        }

        return report

    def _calculate_parallelism_efficiency(
        self,
        execution_plan: Dict[str, Any],
        execution_results: Dict[str, Any]
    ) -> float:
        """
        Calculate how efficiently parallelism was utilized.

        Efficiency = actual_duration / sequential_duration
        Lower is better (more parallel execution)
        """
        phases = execution_plan.get("phases", [])
        if not phases:
            return 1.0

        # Sum phase durations (actual parallel execution)
        actual_duration = sum(
            phase_result["duration_seconds"]
            for phase_result in execution_results.get("phase_results", [])
        )

        # Sum all task durations (if run sequentially)
        sequential_duration = sum(
            assignment.get("estimated_duration_minutes", 15) * 60
            for phase in phases
            for assignment in phase.get("assignments", [])
        )

        if sequential_duration == 0:
            return 1.0

        efficiency = actual_duration / sequential_duration
        return round(efficiency, 2)

    def _generate_recommendations(
        self,
        execution_plan: Dict[str, Any],
        execution_results: Dict[str, Any],
        total_duration: float
    ) -> List[str]:
        """Generate optimization recommendations based on execution."""
        recommendations = []

        # Check success rate
        success_rate = (
            execution_results["completed_tasks"] / execution_results["total_tasks"]
            if execution_results["total_tasks"] > 0 else 0.0
        )

        if success_rate < 0.8:
            recommendations.append(
                f"Low success rate ({success_rate*100:.0f}%). "
                "Consider reviewing agent capabilities or task complexity."
            )

        # Check duration vs estimate
        estimated_duration = execution_plan.get("total_estimated_duration_minutes", 0)
        if total_duration > estimated_duration * 1.5:
            recommendations.append(
                f"Execution took {total_duration/estimated_duration:.1f}x longer than estimated. "
                "Review agent performance metrics."
            )

        # Check parallelism
        phases = execution_plan.get("phases", [])
        if len(phases) > 3:
            avg_agents_per_phase = sum(
                len(phase.get("assignments", []))
                for phase in phases
            ) / len(phases)

            if avg_agents_per_phase < 2:
                recommendations.append(
                    "Low parallelism detected. Consider refactoring task dependencies "
                    "to enable more parallel execution."
                )

        if not recommendations:
            recommendations.append("Execution performed optimally. No recommendations at this time.")

        return recommendations


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dynamic Multi-Agent Pipeline with Multimodal Input Support"
    )

    # Required arguments
    parser.add_argument(
        "--project-id",
        required=True,
        help="GCP project ID"
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task description in natural language"
    )

    # Optional arguments
    parser.add_argument(
        "--inputs",
        nargs="+",
        help="Input files (images, PDFs, videos, audio, design files)"
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="Output directory for artifacts (default: ./output)"
    )
    parser.add_argument(
        "--agent-registry",
        default="config/agent_registry.json",
        help="Path to agent registry JSON (default: config/agent_registry.json)"
    )
    parser.add_argument(
        "--location",
        default="us-central1",
        help="Vertex AI location (default: us-central1)"
    )
    parser.add_argument(
        "--max-cost",
        type=float,
        help="Maximum cost in USD"
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        help="Maximum duration in hours"
    )
    parser.add_argument(
        "--mode",
        choices=["dynamic", "static"],
        default="dynamic",
        help="Orchestration mode (default: dynamic)"
    )
    parser.add_argument(
        "--report",
        help="Save execution report to this file"
    )

    args = parser.parse_args()

    # Build constraints
    constraints = {}
    if args.max_cost:
        constraints["max_cost_usd"] = args.max_cost
    if args.max_duration:
        constraints["max_duration_hours"] = args.max_duration

    # Initialize pipeline
    pipeline = DynamicMultiAgentPipeline(
        project_id=args.project_id,
        location=args.location,
        agent_registry_path=args.agent_registry,
        output_dir=args.output,
        mode=args.mode
    )

    # Run pipeline
    report = pipeline.run(
        task_description=args.task,
        input_files=args.inputs,
        constraints=constraints
    )

    # Save report if specified
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n✓ Full report saved to: {args.report}")


if __name__ == "__main__":
    main()
