"""
tests/agent_tests/test_backend_realworld.py

Real-world backend development test scenarios WITHOUT knowledge base dependency.
Tests standalone development capabilities for API, database, and microservices agents.
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
# API DEVELOPMENT TESTS - Real-World Scenarios
# ============================================================================

def create_api_developer_tests() -> AgentTestSuite:
    """
    Real-world API development tests.
    Tests standalone API generation without legacy context.
    """
    suite = AgentTestSuite("api_developer_agent")

    # Test 1: Build E-commerce REST API from scratch
    suite.add_test(
        test_id="api_001",
        test_name="E-commerce REST API - From Scratch",
        description="Generate complete REST API for e-commerce product catalog",
        input_prompt="Build a REST API for e-commerce product catalog with CRUD operations",
        input_data={
            "language": "python",
            "framework": "fastapi",
            "endpoints": [
                {
                    "path": "/products",
                    "methods": ["GET", "POST"],
                    "description": "List all products and create new products"
                },
                {
                    "path": "/products/{product_id}",
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update, or delete a specific product"
                },
                {
                    "path": "/products/search",
                    "methods": ["GET"],
                    "description": "Search products by name, category, or price range"
                },
                {
                    "path": "/categories",
                    "methods": ["GET"],
                    "description": "List all product categories"
                }
            ],
            "database": "postgresql",
            "authentication": "JWT",
            "include_openapi": True
        },
        expected_status="success",
        expected_fields=["code", "openapi_spec", "database_schema", "documentation"],
        validation_function=lambda r: {
            "valid": (
                "from fastapi import" in r.get("code", "") and
                "@app.get" in r.get("code", "") and
                "@app.post" in r.get("code", "") and
                "openapi" in r.get("openapi_spec", {}) and
                len(r.get("database_schema", {}).get("tables", [])) > 0
            ),
            "details": "Code should contain FastAPI imports, routes, OpenAPI spec, and database schema"
        }
    )

    # Test 2: Build GraphQL API for Social Media
    suite.add_test(
        test_id="api_002",
        test_name="Social Media GraphQL API - Greenfield",
        description="Generate GraphQL API for social media platform with posts, comments, likes",
        input_prompt="Create a GraphQL API for social media with posts, comments, and user interactions",
        input_data={
            "language": "typescript",
            "framework": "apollo",
            "schema": {
                "types": [
                    {
                        "name": "User",
                        "fields": ["id", "username", "email", "bio", "avatar_url", "created_at"]
                    },
                    {
                        "name": "Post",
                        "fields": ["id", "author_id", "content", "image_url", "likes_count", "created_at"]
                    },
                    {
                        "name": "Comment",
                        "fields": ["id", "post_id", "author_id", "content", "created_at"]
                    }
                ],
                "queries": [
                    "getUser(id: ID!): User",
                    "getPost(id: ID!): Post",
                    "getFeed(limit: Int, offset: Int): [Post]",
                    "getComments(postId: ID!): [Comment]"
                ],
                "mutations": [
                    "createPost(content: String!, imageUrl: String): Post",
                    "likePost(postId: ID!): Post",
                    "addComment(postId: ID!, content: String!): Comment",
                    "followUser(userId: ID!): User"
                ]
            },
            "database": "postgresql",
            "realtime": True  # Include subscriptions
        },
        expected_status="success",
        expected_fields=["code", "schema_definition", "resolvers", "documentation"],
        validation_function=lambda r: {
            "valid": (
                "type User" in r.get("schema_definition", "") and
                "type Post" in r.get("schema_definition", "") and
                "type Mutation" in r.get("schema_definition", "") and
                "Query" in r.get("resolvers", {})
            ),
            "details": "Should contain GraphQL type definitions, queries, mutations, and resolvers"
        }
    )

    # Test 3: Build gRPC Microservice
    suite.add_test(
        test_id="api_003",
        test_name="Payment Processing gRPC Service",
        description="Generate gRPC service for payment processing with Stripe integration",
        input_prompt="Build a gRPC microservice for payment processing",
        input_data={
            "language": "go",
            "service_name": "PaymentService",
            "methods": [
                {
                    "name": "ProcessPayment",
                    "request": {
                        "amount": "float",
                        "currency": "string",
                        "payment_method_id": "string",
                        "customer_id": "string"
                    },
                    "response": {
                        "transaction_id": "string",
                        "status": "PaymentStatus",
                        "created_at": "timestamp"
                    }
                },
                {
                    "name": "RefundPayment",
                    "request": {
                        "transaction_id": "string",
                        "amount": "float",
                        "reason": "string"
                    },
                    "response": {
                        "refund_id": "string",
                        "status": "RefundStatus",
                        "created_at": "timestamp"
                    }
                },
                {
                    "name": "GetPaymentStatus",
                    "request": {
                        "transaction_id": "string"
                    },
                    "response": {
                        "status": "PaymentStatus",
                        "transaction": "Transaction"
                    },
                    "streaming": "server"  # Server-side streaming
                }
            ],
            "include_interceptors": True,  # Auth, logging, error handling
            "include_tests": True
        },
        expected_status="success",
        expected_fields=["proto_file", "server_code", "client_code", "tests"],
        validation_function=lambda r: {
            "valid": (
                "service PaymentService" in r.get("proto_file", "") and
                "rpc ProcessPayment" in r.get("proto_file", "") and
                "func main()" in r.get("server_code", "") and
                "grpc.NewServer" in r.get("server_code", "")
            ),
            "details": "Should contain .proto file, gRPC server implementation, and client code"
        }
    )

    # Test 4: Build Webhook Handler API
    suite.add_test(
        test_id="api_004",
        test_name="Webhook Handler for Third-Party Integrations",
        description="Generate webhook handler API for Stripe, GitHub, and Slack events",
        input_prompt="Create webhook handler API that processes events from Stripe, GitHub, and Slack",
        input_data={
            "language": "python",
            "framework": "flask",
            "webhooks": [
                {
                    "provider": "stripe",
                    "events": ["payment_intent.succeeded", "payment_intent.failed", "charge.refunded"],
                    "signature_verification": True
                },
                {
                    "provider": "github",
                    "events": ["push", "pull_request", "issues"],
                    "signature_verification": True
                },
                {
                    "provider": "slack",
                    "events": ["message", "app_mention", "reaction_added"],
                    "signature_verification": True
                }
            ],
            "include_retry_logic": True,
            "include_idempotency": True,
            "database": "postgresql"  # Store webhook events
        },
        expected_status="success",
        expected_fields=["code", "webhook_handlers", "signature_verification", "database_schema"],
        validation_function=lambda r: {
            "valid": (
                "@app.route" in r.get("code", "") and
                "stripe" in r.get("code", "").lower() and
                "github" in r.get("code", "").lower() and
                "verify" in r.get("code", "").lower()
            ),
            "details": "Should contain Flask routes, signature verification, and event handlers"
        }
    )

    # Test 5: Build Real-time Chat API with WebSockets
    suite.add_test(
        test_id="api_005",
        test_name="Real-time Chat API with WebSockets",
        description="Generate real-time chat API with WebSocket support and message persistence",
        input_prompt="Build a real-time chat API with WebSocket connections and message history",
        input_data={
            "language": "typescript",
            "framework": "express",
            "websocket_library": "socket.io",
            "features": [
                "one_to_one_chat",
                "group_chat",
                "typing_indicators",
                "read_receipts",
                "message_history",
                "file_uploads",
                "presence_status"
            ],
            "database": "mongodb",
            "redis": True,  # For presence and pub/sub
            "authentication": "JWT"
        },
        expected_status="success",
        expected_fields=["code", "websocket_handlers", "rest_endpoints", "database_schema"],
        validation_function=lambda r: {
            "valid": (
                "socket.io" in r.get("code", "") and
                "io.on" in r.get("code", "") and
                "emit" in r.get("code", "") and
                len(r.get("rest_endpoints", [])) > 0
            ),
            "details": "Should contain Socket.io setup, event handlers, and REST endpoints for message history"
        }
    )

    return suite


# ============================================================================
# DATABASE DEVELOPMENT TESTS - Real-World Scenarios
# ============================================================================

def create_database_engineer_tests() -> AgentTestSuite:
    """
    Real-world database design and development tests.
    Tests schema design, migrations, and optimization without legacy context.
    """
    suite = AgentTestSuite("database_engineer_agent")

    # Test 1: Design E-commerce Database Schema
    suite.add_test(
        test_id="db_001",
        test_name="E-commerce Database Schema - Greenfield",
        description="Design complete database schema for e-commerce platform",
        input_prompt="Design a scalable database schema for an e-commerce platform",
        input_data={
            "database_type": "postgresql",
            "requirements": {
                "entities": [
                    "users (customers, admins)",
                    "products (with variants, SKUs)",
                    "categories (hierarchical)",
                    "orders (with line items)",
                    "payments (multiple payment methods)",
                    "shipping_addresses",
                    "reviews_and_ratings",
                    "carts (persistent shopping carts)",
                    "wishlists",
                    "inventory (stock tracking)"
                ],
                "features": [
                    "multi-currency support",
                    "tax calculation",
                    "discount codes and promotions",
                    "order history",
                    "product recommendations"
                ],
                "scale": "10M users, 1M products, 100K orders/day"
            },
            "include_indexes": True,
            "include_constraints": True,
            "include_migrations": True
        },
        expected_status="success",
        expected_fields=["schema_sql", "erd_diagram", "indexes", "constraints", "migrations"],
        validation_function=lambda r: {
            "valid": (
                "CREATE TABLE users" in r.get("schema_sql", "") and
                "CREATE TABLE products" in r.get("schema_sql", "") and
                "CREATE TABLE orders" in r.get("schema_sql", "") and
                "CREATE INDEX" in r.get("schema_sql", "") and
                "FOREIGN KEY" in r.get("schema_sql", "")
            ),
            "details": "Schema should contain all required tables, indexes, and foreign keys"
        }
    )

    # Test 2: Design SaaS Multi-Tenant Database
    suite.add_test(
        test_id="db_002",
        test_name="SaaS Multi-Tenant Database Architecture",
        description="Design multi-tenant database with proper data isolation",
        input_prompt="Design a multi-tenant SaaS database with strong tenant isolation",
        input_data={
            "database_type": "postgresql",
            "tenancy_model": "schema_per_tenant",  # vs shared_schema or database_per_tenant
            "requirements": {
                "entities": [
                    "tenants (organizations)",
                    "users (per tenant)",
                    "projects (per tenant)",
                    "tasks (per project)",
                    "files (per project)",
                    "audit_logs (per tenant)"
                ],
                "features": [
                    "tenant_isolation",
                    "cross_tenant_analytics",
                    "tenant_quotas",
                    "data_migration_between_plans"
                ],
                "scale": "10K tenants, avg 50 users per tenant"
            },
            "include_row_level_security": True,
            "include_partitioning": True
        },
        expected_status="success",
        expected_fields=["schema_sql", "rls_policies", "partitioning_strategy", "tenant_management"],
        validation_function=lambda r: {
            "valid": (
                "tenant" in r.get("schema_sql", "").lower() and
                ("CREATE POLICY" in r.get("schema_sql", "") or len(r.get("rls_policies", [])) > 0) and
                len(r.get("partitioning_strategy", "")) > 0
            ),
            "details": "Should include tenant isolation, RLS policies, and partitioning strategy"
        }
    )

    # Test 3: Time-Series Data Schema for IoT
    suite.add_test(
        test_id="db_003",
        test_name="IoT Time-Series Database Schema",
        description="Design time-series database for IoT sensor data",
        input_prompt="Design a time-series database schema for IoT device telemetry",
        input_data={
            "database_type": "timescaledb",  # PostgreSQL extension
            "requirements": {
                "data_points": [
                    "device_id",
                    "timestamp",
                    "temperature",
                    "humidity",
                    "pressure",
                    "battery_level",
                    "latitude",
                    "longitude"
                ],
                "features": [
                    "1000 devices",
                    "data every 10 seconds",
                    "retention: 1 year hot, 5 years cold",
                    "aggregations: hourly, daily, monthly",
                    "alerting on thresholds"
                ],
                "queries": [
                    "recent data for device",
                    "time-range aggregations",
                    "multi-device comparisons",
                    "anomaly detection queries"
                ]
            },
            "include_hypertables": True,
            "include_continuous_aggregates": True,
            "include_retention_policy": True
        },
        expected_status="success",
        expected_fields=["schema_sql", "hypertables", "continuous_aggregates", "retention_policies"],
        validation_function=lambda r: {
            "valid": (
                "create_hypertable" in r.get("schema_sql", "").lower() or
                len(r.get("hypertables", [])) > 0
            ) and (
                "continuous aggregate" in r.get("schema_sql", "").lower() or
                len(r.get("continuous_aggregates", [])) > 0
            ),
            "details": "Should use TimescaleDB hypertables and continuous aggregates"
        }
    )

    # Test 4: NoSQL Schema for Social Network
    suite.add_test(
        test_id="db_004",
        test_name="Social Network NoSQL Schema (MongoDB)",
        description="Design MongoDB schema for social networking platform",
        input_prompt="Design a MongoDB schema for a social networking platform",
        input_data={
            "database_type": "mongodb",
            "requirements": {
                "collections": [
                    "users (profiles, followers, following)",
                    "posts (text, images, videos)",
                    "comments (nested threads)",
                    "likes",
                    "notifications",
                    "messages (DMs)",
                    "feeds (cached user feeds)"
                ],
                "features": [
                    "fast feed generation",
                    "efficient follower queries",
                    "real-time notifications",
                    "full-text search on posts"
                ],
                "scale": "100M users, 1B posts"
            },
            "embedding_strategy": True,  # Embed vs reference
            "include_indexes": True,
            "include_sharding_key": True
        },
        expected_status="success",
        expected_fields=["collections", "indexes", "sharding_strategy", "embedding_decisions"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("collections", {})) >= 5 and
                len(r.get("indexes", [])) > 0 and
                len(r.get("sharding_strategy", "")) > 0
            ),
            "details": "Should define collections, indexes, and sharding strategy for scale"
        }
    )

    # Test 5: Data Warehouse Schema (Star Schema)
    suite.add_test(
        test_id="db_005",
        test_name="Analytics Data Warehouse - Star Schema",
        description="Design star schema for business intelligence and analytics",
        input_prompt="Design a star schema data warehouse for e-commerce analytics",
        input_data={
            "database_type": "bigquery",
            "requirements": {
                "fact_tables": [
                    "fact_sales (orders, revenue, quantity)",
                    "fact_web_events (page views, clicks, sessions)"
                ],
                "dimension_tables": [
                    "dim_customer (demographics, segments)",
                    "dim_product (category, brand, price)",
                    "dim_date (date hierarchy)",
                    "dim_location (geography hierarchy)",
                    "dim_payment_method"
                ],
                "metrics": [
                    "total_revenue",
                    "avg_order_value",
                    "customer_lifetime_value",
                    "conversion_rate",
                    "cart_abandonment_rate"
                ]
            },
            "slowly_changing_dimensions": True,  # SCD Type 2
            "include_aggregates": True
        },
        expected_status="success",
        expected_fields=["schema_sql", "fact_tables", "dimension_tables", "scd_strategy"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("fact_tables", {})) >= 1 and
                len(r.get("dimension_tables", {})) >= 4 and
                "scd" in r.get("scd_strategy", "").lower()
            ),
            "details": "Should have fact tables, dimension tables, and SCD strategy"
        }
    )

    return suite


# ============================================================================
# MICROSERVICES ARCHITECTURE TESTS - Real-World Scenarios
# ============================================================================

def create_microservices_architect_tests() -> AgentTestSuite:
    """
    Real-world microservices architecture tests.
    Tests designing microservices from scratch without legacy context.
    """
    suite = AgentTestSuite("microservices_architect_agent")

    # Test 1: Design Food Delivery Platform Microservices
    suite.add_test(
        test_id="ms_001",
        test_name="Food Delivery Platform Microservices",
        description="Design complete microservices architecture for food delivery app",
        input_prompt="Design microservices architecture for a food delivery platform like Uber Eats",
        input_data={
            "business_domain": "food_delivery",
            "requirements": {
                "features": [
                    "restaurant listing and search",
                    "menu management",
                    "order placement and tracking",
                    "real-time delivery tracking",
                    "payment processing",
                    "ratings and reviews",
                    "notifications (push, SMS, email)",
                    "customer support chat"
                ],
                "users": [
                    "customers (mobile app)",
                    "restaurants (dashboard)",
                    "delivery drivers (mobile app)",
                    "admins (internal tools)"
                ],
                "scale": "1M users, 10K restaurants, 100K daily orders"
            },
            "decomposition_strategy": "domain_driven_design",
            "communication": ["sync_rest", "async_events", "websocket"],
            "include_api_gateway": True,
            "include_service_mesh": True
        },
        expected_status="success",
        expected_fields=["services", "api_contracts", "event_flows", "infrastructure"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("services", [])) >= 6 and
                any("order" in s.get("name", "").lower() for s in r.get("services", [])) and
                any("delivery" in s.get("name", "").lower() for s in r.get("services", []))
            ),
            "details": "Should have at least 6 microservices including order and delivery services"
        }
    )

    # Test 2: Design E-Learning Platform Microservices
    suite.add_test(
        test_id="ms_002",
        test_name="E-Learning Platform Microservices",
        description="Design microservices for online learning platform with video streaming",
        input_prompt="Design microservices for an online learning platform with courses, videos, and certifications",
        input_data={
            "business_domain": "e_learning",
            "requirements": {
                "features": [
                    "course catalog and enrollment",
                    "video streaming (VOD and live)",
                    "progress tracking and analytics",
                    "quizzes and assessments",
                    "certification generation",
                    "discussion forums",
                    "payment and subscriptions",
                    "content recommendations"
                ],
                "users": [
                    "students",
                    "instructors",
                    "content creators",
                    "admins"
                ],
                "scale": "5M students, 100K courses, 10M video views/day"
            },
            "decomposition_strategy": "business_capability",
            "data_storage": {
                "video": "cdn_and_object_storage",
                "user_data": "postgresql",
                "analytics": "clickstream_to_data_lake"
            },
            "include_cqrs": True,  # Command Query Responsibility Segregation
            "include_event_sourcing": True
        },
        expected_status="success",
        expected_fields=["services", "data_flow", "cqrs_implementation", "event_sourcing"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("services", [])) >= 5 and
                any("video" in s.get("name", "").lower() or "streaming" in s.get("name", "").lower()
                    for s in r.get("services", [])) and
                len(r.get("cqrs_implementation", "")) > 0
            ),
            "details": "Should include video service and CQRS pattern implementation"
        }
    )

    # Test 3: Design Banking Platform Microservices
    suite.add_test(
        test_id="ms_003",
        test_name="Digital Banking Platform Microservices",
        description="Design secure microservices for digital banking with regulatory compliance",
        input_prompt="Design microservices architecture for a digital banking platform",
        input_data={
            "business_domain": "financial_services",
            "requirements": {
                "features": [
                    "account management",
                    "transactions (transfers, payments)",
                    "cards (debit/credit management)",
                    "loans and credit",
                    "fraud detection",
                    "KYC and AML compliance",
                    "transaction history and statements",
                    "notifications and alerts"
                ],
                "compliance": [
                    "PCI-DSS",
                    "GDPR",
                    "SOC 2",
                    "regulatory reporting"
                ],
                "scale": "10M accounts, 100M transactions/month"
            },
            "security_requirements": {
                "encryption": "end_to_end",
                "authentication": "mfa_and_biometric",
                "authorization": "rbac_and_abac",
                "audit_logging": "immutable"
            },
            "transaction_consistency": "saga_pattern",
            "include_service_mesh": True
        },
        expected_status="success",
        expected_fields=["services", "security_architecture", "saga_implementations", "compliance_mapping"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("services", [])) >= 6 and
                any("fraud" in s.get("name", "").lower() for s in r.get("services", [])) and
                "saga" in r.get("saga_implementations", "").lower()
            ),
            "details": "Should include fraud detection service and Saga pattern for distributed transactions"
        }
    )

    # Test 4: Design Healthcare Platform Microservices
    suite.add_test(
        test_id="ms_004",
        test_name="Healthcare Platform Microservices (HIPAA)",
        description="Design HIPAA-compliant microservices for telemedicine platform",
        input_prompt="Design microservices for a telemedicine platform with HIPAA compliance",
        input_data={
            "business_domain": "healthcare",
            "requirements": {
                "features": [
                    "patient records (EHR)",
                    "appointment scheduling",
                    "video consultations",
                    "prescription management",
                    "lab results",
                    "billing and insurance",
                    "provider directory",
                    "secure messaging"
                ],
                "compliance": [
                    "HIPAA",
                    "HL7 FHIR standards",
                    "data encryption at rest and in transit",
                    "audit trails",
                    "data retention policies"
                ],
                "integrations": [
                    "insurance providers",
                    "pharmacy systems",
                    "lab systems",
                    "EHR systems"
                ]
            },
            "data_isolation": "strict_tenant_separation",
            "include_data_masking": True,
            "include_consent_management": True
        },
        expected_status="success",
        expected_fields=["services", "fhir_resources", "security_controls", "audit_architecture"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("services", [])) >= 6 and
                ("fhir" in str(r.get("fhir_resources", "")).lower() or
                 "hl7" in str(r.get("services", [])).lower()) and
                "hipaa" in str(r.get("security_controls", "")).lower()
            ),
            "details": "Should include FHIR-compliant services and HIPAA security controls"
        }
    )

    # Test 5: Design Gaming Platform Microservices
    suite.add_test(
        test_id="ms_005",
        test_name="Multiplayer Gaming Platform Microservices",
        description="Design microservices for real-time multiplayer gaming platform",
        input_prompt="Design microservices for a multiplayer online gaming platform",
        input_data={
            "business_domain": "gaming",
            "requirements": {
                "features": [
                    "player matchmaking",
                    "game session management",
                    "real-time game state synchronization",
                    "leaderboards and rankings",
                    "in-game chat and voice",
                    "in-app purchases and virtual currency",
                    "achievements and rewards",
                    "anti-cheat detection",
                    "player analytics"
                ],
                "performance": {
                    "latency": "< 50ms for game actions",
                    "concurrent_players": "1M simultaneous",
                    "matchmaking_time": "< 30s"
                }
            },
            "communication": ["websocket", "udp_for_game_state", "rest_for_metadata"],
            "include_caching": "redis_for_leaderboards",
            "include_cdn": True,
            "deployment": "multi_region"
        },
        expected_status="success",
        expected_fields=["services", "realtime_architecture", "scaling_strategy", "anti_cheat"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("services", [])) >= 6 and
                any("matchmaking" in s.get("name", "").lower() or "match" in s.get("name", "").lower()
                    for s in r.get("services", [])) and
                "websocket" in str(r.get("realtime_architecture", "")).lower()
            ),
            "details": "Should include matchmaking service and WebSocket-based real-time architecture"
        }
    )

    return suite


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_backend_realworld_tests(agent_name: str = "all", save_results: bool = True):
    """
    Run real-world backend development tests.

    Args:
        agent_name: Name of agent to test or "all"
        save_results: Whether to save results to file
    """
    # Import Phase 2 agents
    try:
        from agents.backend.api_developer.agent import APIDevAgent
        from agents.backend.database_engineer.agent import DatabaseEngineerAgent
        from agents.backend.microservices_architect.agent import MicroservicesArchitectAgent

        # Create standalone agent instances (no message bus for testing)
        api_agent = APIDevAgent(context={}, message_bus=None, orchestrator_id="test_orch")
        db_agent = DatabaseEngineerAgent(context={}, message_bus=None, orchestrator_id="test_orch")
        ms_agent = MicroservicesArchitectAgent(context={}, message_bus=None, orchestrator_id="test_orch")

        test_suites = {
            "api_developer_agent": (create_api_developer_tests, api_agent),
            "database_engineer_agent": (create_database_engineer_tests, db_agent),
            "microservices_architect_agent": (create_microservices_architect_tests, ms_agent),
        }

    except ImportError as e:
        print(f"Error importing Phase 2 backend agents: {e}")
        print("Make sure agents/backend/* agents are implemented.")
        return

    if agent_name == "all":
        agents_to_test = list(test_suites.keys())
    elif agent_name in test_suites:
        agents_to_test = [agent_name]
    else:
        print(f"Error: Unknown agent '{agent_name}'")
        print(f"Available agents: {', '.join(['all'] + list(test_suites.keys()))}")
        return

    all_summaries = []

    print("\n" + "="*80)
    print("REAL-WORLD BACKEND DEVELOPMENT TESTS (No Knowledge Base)")
    print("="*80)

    for agent in agents_to_test:
        suite_creator, agent_instance = test_suites[agent]
        suite = suite_creator()

        # Create test runner
        runner = AgentTestRunner(agent_instance, agent)

        # Run tests
        summary = runner.run_test_suite(suite.get_test_cases())
        all_summaries.append(summary)

        # Save results
        if save_results:
            output_path = f"tests/agent_tests/results/{agent}_realworld_results.json"
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

        print(f"Total Agents Tested: {len(all_summaries)}")
        print(f"Total Tests:         {total_tests}")
        print(f"✓ Passed:            {total_passed}")
        print(f"✗ Failed:            {total_failed}")
        print(f"⚠ Errors:            {total_errors}")
        print(f"Success Rate:        {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
        print("="*80)

    return all_summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test backend agents with real-world scenarios")
    parser.add_argument(
        "--agent",
        default="all",
        help="Agent to test: api_developer_agent, database_engineer_agent, microservices_architect_agent, or all"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )

    args = parser.parse_args()
    run_backend_realworld_tests(agent_name=args.agent, save_results=not args.no_save)
