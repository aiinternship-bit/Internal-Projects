"""
tests/agent_tests/test_fullstack_integration.py

Full-stack integration test scenarios WITHOUT knowledge base dependency.
Tests multi-agent collaboration for building complete applications end-to-end.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.agent_tests.agent_test_framework import (
    AgentTestRunner,
    AgentTestSuite,
    create_validation_function
)


# ============================================================================
# FULL-STACK APPLICATION TESTS - End-to-End Scenarios
# ============================================================================

def create_fullstack_todo_app_tests() -> AgentTestSuite:
    """
    Build complete Todo App - Backend + Frontend + Database.
    Tests coordinated development across multiple agents.
    """
    suite = AgentTestSuite("fullstack_orchestrator")

    # Test 1: Build Complete CRUD Todo Application
    suite.add_test(
        test_id="fullstack_001",
        test_name="Todo App - Complete Stack",
        description="Build full-stack Todo application with React frontend and FastAPI backend",
        input_prompt="Build a complete todo application with user authentication",
        input_data={
            "project_name": "todo_app",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "styling": "tailwind",
                    "state_management": "zustand"
                },
                "backend": {
                    "language": "python",
                    "framework": "fastapi",
                    "orm": "sqlalchemy",
                    "async": True
                },
                "database": {
                    "type": "postgresql",
                    "orm": "sqlalchemy"
                },
                "authentication": {
                    "method": "JWT",
                    "features": ["signup", "login", "logout", "password_reset"]
                }
            },
            "features": [
                "user_registration_and_login",
                "create_todo",
                "list_todos",
                "update_todo",
                "delete_todo",
                "mark_todo_complete",
                "filter_todos",
                "search_todos"
            ],
            "agents_required": [
                "database_engineer",  # Design schema
                "api_developer",      # Build REST API
                "ui_developer",       # Build React components
                "code_validator"      # Validate all code
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "integration_tests", "deployment_config"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("database_schema", "")) > 0 and
                len(r.get("api_code", "")) > 0 and
                len(r.get("frontend_code", "")) > 0 and
                "CREATE TABLE" in r.get("database_schema", "") and
                ("from fastapi import" in r.get("api_code", "") or "FastAPI" in r.get("api_code", "")) and
                ("import React" in r.get("frontend_code", "") or "const" in r.get("frontend_code", ""))
            ),
            "details": "Should include database schema, API code, and React frontend"
        }
    )

    # Test 2: Build Blog Platform
    suite.add_test(
        test_id="fullstack_002",
        test_name="Blog Platform - Complete Stack",
        description="Build blog platform with markdown editor, comments, and tags",
        input_prompt="Build a blog platform with rich text editor and commenting system",
        input_data={
            "project_name": "blog_platform",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "editor": "slate",
                    "styling": "styled_components"
                },
                "backend": {
                    "language": "typescript",
                    "framework": "express",
                    "orm": "prisma"
                },
                "database": {
                    "type": "postgresql"
                },
                "file_storage": "aws_s3"
            },
            "features": [
                "user_profiles",
                "create_post_with_markdown",
                "edit_post",
                "delete_post",
                "comment_on_posts",
                "like_posts",
                "tag_posts",
                "search_posts",
                "author_following",
                "image_uploads"
            ],
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer",
                "react_specialist"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "file_upload_config"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("database_schema", "")) > 0 and
                len(r.get("api_code", "")) > 0 and
                len(r.get("frontend_code", "")) > 0 and
                ("posts" in r.get("database_schema", "").lower() or "articles" in r.get("database_schema", "").lower()) and
                "comments" in r.get("database_schema", "").lower()
            ),
            "details": "Should include posts and comments in database schema"
        }
    )

    # Test 3: Build E-commerce Store
    suite.add_test(
        test_id="fullstack_003",
        test_name="E-commerce Store - Complete Stack",
        description="Build e-commerce store with products, cart, checkout, and payment",
        input_prompt="Build an e-commerce store with shopping cart and Stripe payments",
        input_data={
            "project_name": "ecommerce_store",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "styling": "tailwind"
                },
                "backend": {
                    "language": "python",
                    "framework": "fastapi",
                    "payment": "stripe"
                },
                "database": {
                    "type": "postgresql"
                }
            },
            "features": [
                "product_catalog",
                "product_search_and_filters",
                "shopping_cart",
                "checkout_flow",
                "payment_processing",
                "order_management",
                "user_accounts",
                "order_history",
                "admin_dashboard",
                "inventory_management"
            ],
            "integrations": {
                "payment_gateway": "stripe",
                "email": "sendgrid",
                "analytics": "google_analytics"
            },
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer",
                "microservices_architect"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "payment_integration", "admin_panel"],
        validation_function=lambda r: {
            "valid": (
                "products" in r.get("database_schema", "").lower() and
                "orders" in r.get("database_schema", "").lower() and
                "cart" in r.get("database_schema", "").lower() and
                len(r.get("payment_integration", "")) > 0 and
                ("stripe" in r.get("payment_integration", "").lower() or "stripe" in r.get("api_code", "").lower())
            ),
            "details": "Should include products, orders, cart tables and Stripe integration"
        }
    )

    return suite


# ============================================================================
# REAL-TIME APPLICATION TESTS
# ============================================================================

def create_realtime_app_tests() -> AgentTestSuite:
    """
    Build real-time applications with WebSocket communication.
    """
    suite = AgentTestSuite("realtime_orchestrator")

    # Test 1: Build Chat Application
    suite.add_test(
        test_id="realtime_001",
        test_name="Real-time Chat Application",
        description="Build chat app with WebSocket, message persistence, and typing indicators",
        input_prompt="Build a real-time chat application with WebSocket support",
        input_data={
            "project_name": "chat_app",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "websocket": "socket.io-client",
                    "styling": "tailwind"
                },
                "backend": {
                    "language": "typescript",
                    "framework": "express",
                    "websocket": "socket.io",
                    "orm": "prisma"
                },
                "database": {
                    "type": "postgresql"
                },
                "cache": {
                    "type": "redis",
                    "use_cases": ["presence", "pub_sub"]
                }
            },
            "features": [
                "one_to_one_messaging",
                "group_chat",
                "typing_indicators",
                "read_receipts",
                "message_history",
                "file_sharing",
                "online_status",
                "push_notifications",
                "message_search"
            ],
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer",
                "react_specialist"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "websocket_server", "frontend_code", "redis_config"],
        validation_function=lambda r: {
            "valid": (
                "messages" in r.get("database_schema", "").lower() and
                ("socket.io" in r.get("websocket_server", "") or "websocket" in r.get("websocket_server", "").lower()) and
                len(r.get("frontend_code", "")) > 0 and
                len(r.get("redis_config", "")) > 0
            ),
            "details": "Should include messages table, WebSocket server, and Redis config"
        }
    )

    # Test 2: Build Collaborative Whiteboard
    suite.add_test(
        test_id="realtime_002",
        test_name="Collaborative Whiteboard",
        description="Build real-time collaborative whiteboard with drawing tools",
        input_prompt="Build a collaborative whiteboard application with real-time synchronization",
        input_data={
            "project_name": "collaborative_whiteboard",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "canvas_library": "fabric.js",
                    "websocket": "socket.io-client"
                },
                "backend": {
                    "language": "typescript",
                    "framework": "express",
                    "websocket": "socket.io"
                },
                "database": {
                    "type": "mongodb"
                }
            },
            "features": [
                "freehand_drawing",
                "shapes (rectangle, circle, line)",
                "text_tool",
                "color_picker",
                "brush_size",
                "eraser",
                "undo_redo",
                "multi_user_cursors",
                "real_time_sync",
                "save_and_load_boards",
                "export_to_image"
            ],
            "collaboration": {
                "conflict_resolution": "last_write_wins",
                "cursor_sharing": True,
                "user_colors": True
            },
            "agents_required": [
                "api_developer",
                "ui_developer",
                "react_specialist"
            ]
        },
        expected_status="success",
        expected_fields=["backend_code", "frontend_code", "websocket_events", "canvas_implementation"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("websocket_events", [])) >= 5 and
                ("fabric" in r.get("canvas_implementation", "").lower() or "canvas" in r.get("frontend_code", "").lower()) and
                ("socket.io" in r.get("backend_code", "") or "websocket" in r.get("backend_code", "").lower())
            ),
            "details": "Should include WebSocket events, canvas implementation, and real-time sync"
        }
    )

    # Test 3: Build Live Polling/Voting App
    suite.add_test(
        test_id="realtime_003",
        test_name="Live Polling and Voting Platform",
        description="Build real-time polling app with live result updates",
        input_prompt="Build a live polling platform with real-time vote counting",
        input_data={
            "project_name": "live_polls",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "charts": "recharts",
                    "websocket": "socket.io-client"
                },
                "backend": {
                    "language": "python",
                    "framework": "fastapi",
                    "websocket": "websockets",
                    "orm": "sqlalchemy"
                },
                "database": {
                    "type": "postgresql"
                },
                "cache": {
                    "type": "redis"
                }
            },
            "features": [
                "create_poll",
                "multiple_choice_questions",
                "live_voting",
                "real_time_results",
                "results_visualization",
                "poll_expiration",
                "anonymous_voting",
                "vote_once_enforcement",
                "poll_sharing"
            ],
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "websocket_handlers"],
        validation_function=lambda r: {
            "valid": (
                ("polls" in r.get("database_schema", "").lower() or "questions" in r.get("database_schema", "").lower()) and
                "votes" in r.get("database_schema", "").lower() and
                len(r.get("websocket_handlers", [])) > 0
            ),
            "details": "Should include polls and votes tables with WebSocket handlers"
        }
    )

    return suite


# ============================================================================
# DASHBOARD AND ANALYTICS TESTS
# ============================================================================

def create_dashboard_app_tests() -> AgentTestSuite:
    """
    Build data visualization and analytics dashboards.
    """
    suite = AgentTestSuite("dashboard_orchestrator")

    # Test 1: Build Analytics Dashboard
    suite.add_test(
        test_id="dashboard_001",
        test_name="Business Analytics Dashboard",
        description="Build analytics dashboard with multiple chart types and filters",
        input_prompt="Build a business analytics dashboard with sales, revenue, and user metrics",
        input_data={
            "project_name": "analytics_dashboard",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "charts": "recharts",
                    "styling": "tailwind"
                },
                "backend": {
                    "language": "python",
                    "framework": "fastapi",
                    "data_processing": "pandas"
                },
                "database": {
                    "type": "postgresql",
                    "analytics_db": "timescaledb"
                }
            },
            "metrics": [
                "total_revenue",
                "sales_by_product",
                "user_acquisition",
                "conversion_rate",
                "churn_rate",
                "customer_lifetime_value"
            ],
            "visualizations": [
                "line_charts (time series)",
                "bar_charts (comparisons)",
                "pie_charts (distributions)",
                "heatmaps",
                "kpi_cards"
            ],
            "features": [
                "date_range_filter",
                "product_filter",
                "region_filter",
                "export_to_csv",
                "export_to_pdf",
                "scheduled_reports"
            ],
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer",
                "react_specialist"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "chart_configs"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("chart_configs", [])) >= 3 and
                len(r.get("api_code", "")) > 0 and
                ("recharts" in r.get("frontend_code", "").lower() or "chart" in r.get("frontend_code", "").lower())
            ),
            "details": "Should include multiple chart configurations and API endpoints"
        }
    )

    # Test 2: Build IoT Monitoring Dashboard
    suite.add_test(
        test_id="dashboard_002",
        test_name="IoT Device Monitoring Dashboard",
        description="Build real-time IoT dashboard with device telemetry and alerts",
        input_prompt="Build IoT monitoring dashboard for sensor data visualization",
        input_data={
            "project_name": "iot_dashboard",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "charts": "recharts",
                    "websocket": "socket.io-client"
                },
                "backend": {
                    "language": "python",
                    "framework": "fastapi",
                    "mqtt": "paho-mqtt"
                },
                "database": {
                    "type": "timescaledb"
                },
                "message_broker": {
                    "type": "mqtt"
                }
            },
            "features": [
                "real_time_sensor_data",
                "device_status",
                "alert_thresholds",
                "historical_data_charts",
                "device_groups",
                "alert_notifications",
                "data_export",
                "device_configuration"
            ],
            "sensors": [
                "temperature",
                "humidity",
                "pressure",
                "battery_level"
            ],
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "mqtt_integration"],
        validation_function=lambda r: {
            "valid": (
                ("timescale" in r.get("database_schema", "").lower() or "hypertable" in r.get("database_schema", "").lower()) and
                len(r.get("mqtt_integration", "")) > 0 and
                len(r.get("frontend_code", "")) > 0
            ),
            "details": "Should use TimescaleDB and include MQTT integration"
        }
    )

    return suite


# ============================================================================
# SOCIAL PLATFORM TESTS
# ============================================================================

def create_social_platform_tests() -> AgentTestSuite:
    """
    Build social networking features.
    """
    suite = AgentTestSuite("social_orchestrator")

    # Test 1: Build Social Network Feed
    suite.add_test(
        test_id="social_001",
        test_name="Social Network Feed Application",
        description="Build social network with posts, comments, likes, and follows",
        input_prompt="Build a social networking platform with feed, posts, and user interactions",
        input_data={
            "project_name": "social_network",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True,
                    "styling": "tailwind",
                    "infinite_scroll": "react-window"
                },
                "backend": {
                    "language": "typescript",
                    "framework": "express",
                    "orm": "prisma"
                },
                "database": {
                    "type": "postgresql"
                },
                "file_storage": "cloudinary",
                "cache": "redis"
            },
            "features": [
                "user_profiles",
                "create_posts (text, images, videos)",
                "like_posts",
                "comment_on_posts",
                "share_posts",
                "follow_users",
                "personalized_feed",
                "notifications",
                "hashtags",
                "mentions",
                "direct_messages"
            ],
            "feed_algorithm": "chronological_with_relevance",
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer",
                "react_specialist"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "feed_algorithm"],
        validation_function=lambda r: {
            "valid": (
                "users" in r.get("database_schema", "").lower() and
                "posts" in r.get("database_schema", "").lower() and
                "follows" in r.get("database_schema", "").lower() and
                len(r.get("feed_algorithm", "")) > 0
            ),
            "details": "Should include users, posts, follows tables and feed algorithm"
        }
    )

    return suite


# ============================================================================
# AUTHENTICATION AND AUTHORIZATION TESTS
# ============================================================================

def create_auth_system_tests() -> AgentTestSuite:
    """
    Build complete authentication and authorization systems.
    """
    suite = AgentTestSuite("auth_orchestrator")

    # Test 1: Build Multi-Tenant SaaS Auth System
    suite.add_test(
        test_id="auth_001",
        test_name="Multi-Tenant SaaS Authentication System",
        description="Build complete auth system with organizations, teams, and RBAC",
        input_prompt="Build a multi-tenant authentication system with role-based access control",
        input_data={
            "project_name": "saas_auth",
            "tech_stack": {
                "frontend": {
                    "framework": "react",
                    "typescript": True
                },
                "backend": {
                    "language": "python",
                    "framework": "fastapi",
                    "auth_library": "python-jose"
                },
                "database": {
                    "type": "postgresql"
                }
            },
            "features": [
                "user_signup_login",
                "email_verification",
                "password_reset",
                "2fa_totp",
                "oauth_social_login",
                "organization_management",
                "team_management",
                "role_based_access_control",
                "permission_system",
                "audit_logs",
                "session_management",
                "api_key_management"
            ],
            "roles": ["owner", "admin", "member", "guest"],
            "oauth_providers": ["google", "github"],
            "agents_required": [
                "database_engineer",
                "api_developer",
                "ui_developer",
                "code_validator"
            ]
        },
        expected_status="success",
        expected_fields=["database_schema", "api_code", "frontend_code", "rbac_implementation"],
        validation_function=lambda r: {
            "valid": (
                "users" in r.get("database_schema", "").lower() and
                ("organizations" in r.get("database_schema", "").lower() or "tenants" in r.get("database_schema", "").lower()) and
                "roles" in r.get("database_schema", "").lower() and
                len(r.get("rbac_implementation", "")) > 0
            ),
            "details": "Should include users, organizations, roles tables and RBAC logic"
        }
    )

    return suite


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_fullstack_integration_tests(test_suite: str = "all", save_results: bool = True):
    """
    Run full-stack integration tests.

    Args:
        test_suite: Test suite to run (todo, realtime, dashboard, social, auth, all)
        save_results: Whether to save results to file
    """
    # Note: These tests would ideally be run with a mock orchestrator
    # that coordinates multiple agents. For now, we'll create a simple
    # orchestrator mock.

    class FullStackOrchestrator:
        """Mock orchestrator for coordinating multiple agents."""
        def __init__(self, name):
            self.name = name
            # In production, this would coordinate real agents
            # For testing, we return mock integrated results

        @property
        def tools(self):
            return [self.build_fullstack_app]

        def build_fullstack_app(self, **kwargs):
            """Mock method that simulates multi-agent coordination."""
            # This would normally:
            # 1. Send task to database_engineer
            # 2. Send task to api_developer with DB schema
            # 3. Send task to ui_developer with API spec
            # 4. Send everything to code_validator
            # 5. Aggregate results

            return {
                "status": "success",
                "database_schema": "CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255));",
                "api_code": "from fastapi import FastAPI\napp = FastAPI()",
                "frontend_code": "import React from 'react';\nconst App = () => { return <div>App</div>; };",
                "integration_tests": ["test_user_creation", "test_api_endpoints"],
                "deployment_config": "docker-compose.yml with all services",
                "components": ["database", "api", "frontend"],
                "agents_used": kwargs.get("agents_required", [])
            }

    test_suites_map = {
        "todo": ("fullstack_orchestrator", create_fullstack_todo_app_tests),
        "realtime": ("realtime_orchestrator", create_realtime_app_tests),
        "dashboard": ("dashboard_orchestrator", create_dashboard_app_tests),
        "social": ("social_orchestrator", create_social_platform_tests),
        "auth": ("auth_orchestrator", create_auth_system_tests),
    }

    if test_suite == "all":
        suites_to_run = list(test_suites_map.keys())
    elif test_suite in test_suites_map:
        suites_to_run = [test_suite]
    else:
        print(f"Error: Unknown test suite '{test_suite}'")
        print(f"Available suites: {', '.join(['all'] + list(test_suites_map.keys()))}")
        return

    all_summaries = []

    print("\n" + "="*80)
    print("FULL-STACK INTEGRATION TESTS (Multi-Agent Coordination)")
    print("="*80)

    for suite_name in suites_to_run:
        orchestrator_name, suite_creator = test_suites_map[suite_name]
        suite = suite_creator()

        # Create mock orchestrator
        orchestrator = FullStackOrchestrator(orchestrator_name)

        # Create test runner
        runner = AgentTestRunner(orchestrator, orchestrator_name)

        # Run tests
        summary = runner.run_test_suite(suite.get_test_cases())
        all_summaries.append(summary)

        # Save results
        if save_results:
            output_path = f"tests/agent_tests/results/{orchestrator_name}_integration_results.json"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            runner.save_results(output_path)

    # Print overall summary
    if len(all_summaries) > 1:
        print("\n" + "="*80)
        print("OVERALL TEST SUMMARY")
        print("="*80)

        total_tests = sum(s["total_tests"] for s in all_summaries)
        total_passed = sum(s["passed"] for s in all_summaries)
        total_failed = sum(s["failed"] for s in all_summaries)
        total_errors = sum(s["errors"] for s in all_summaries)

        print(f"Total Test Suites:   {len(all_summaries)}")
        print(f"Total Tests:         {total_tests}")
        print(f"✓ Passed:            {total_passed}")
        print(f"✗ Failed:            {total_failed}")
        print(f"⚠ Errors:            {total_errors}")
        print(f"Success Rate:        {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
        print("="*80)

    return all_summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test full-stack integration scenarios")
    parser.add_argument(
        "--suite",
        default="all",
        help="Test suite to run: todo, realtime, dashboard, social, auth, or all"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )

    args = parser.parse_args()
    run_fullstack_integration_tests(test_suite=args.suite, save_results=not args.no_save)
