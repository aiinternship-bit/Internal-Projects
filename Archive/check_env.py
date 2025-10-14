#!/usr/bin/env python3
"""
Environment Configuration Checker
Verifies .env setup and API key configuration
"""
import os
from pathlib import Path


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    print("\n" + "=" * 60)
    print("ENVIRONMENT FILE CHECK")
    print("=" * 60)

    if env_path.exists():
        print("✓ .env file exists")
        return True
    else:
        print("✗ .env file not found")
        if env_example_path.exists():
            print("\n  Create your .env file:")
            print("  $ cp .env.example .env")
            print("  $ nano .env  # Edit with your API keys")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n" + "=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)

    required = {
        "dotenv": "python-dotenv",
        "langsmith": "langsmith",
        "pymilvus": "pymilvus",
        "sentence_transformers": "sentence-transformers"
    }

    all_installed = True
    for module, package in required.items():
        try:
            __import__(module.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - Install with: pip install {package}")
            all_installed = False

    return all_installed


def check_api_keys():
    """Check API key configuration"""
    print("\n" + "=" * 60)
    print("API KEY CHECK (with validation)")
    print("=" * 60)
    print("ℹ  Checking API key validity (may take a few seconds)...\n")

    from src.config import get_api_key_status

    status = get_api_key_status()

    for service, value in status.items():
        print(f"{service.capitalize():12} {value}")

    # Check if at least one LLM is configured and valid
    has_valid_llm = (
        status["ollama"] == "✓ Configured" or
        status["openai"] == "✓ Valid" or
        status["anthropic"] == "✓ Valid"
    )

    if not has_valid_llm:
        print("\n⚠ Warning: No valid LLM backend configured")
        print("  Options:")
        print("    1. Use Ollama (free, local): ollama serve && ollama pull llama3.2")
        print("    2. Use mock mode: --llm mock")
        print("    3. Add valid API keys to .env:")
        print("       OPENAI_API_KEY=sk-...")
        print("       ANTHROPIC_API_KEY=sk-ant-...")

    # Show specific warnings for invalid keys
    if status["openai"] == "⚠ Set but invalid":
        print("\n⚠ OpenAI API key appears invalid")
        print("  - Check the key at: https://platform.openai.com/api-keys")
        print("  - Ensure it starts with 'sk-'")
        print("  - Verify it hasn't been revoked")

    if status["anthropic"] == "⚠ Set but invalid":
        print("\n⚠ Anthropic API key appears invalid")
        print("  - Check the key at: https://console.anthropic.com/settings/keys")
        print("  - Ensure it starts with 'sk-ant-'")
        print("  - Verify it hasn't been revoked")

    return True


def check_langsmith():
    """Check LangSmith configuration"""
    print("\n" + "=" * 60)
    print("LANGSMITH CONFIGURATION")
    print("=" * 60)

    from src.config import is_langsmith_enabled, LANGCHAIN_PROJECT, LANGCHAIN_API_KEY

    if is_langsmith_enabled():
        print("✓ LangSmith tracing enabled")
        print(f"  Project: {LANGCHAIN_PROJECT}")
        print(f"  API Key: {LANGCHAIN_API_KEY[:10]}..." if LANGCHAIN_API_KEY else "  API Key: Not set")
        print("\n  View traces at: https://smith.langchain.com/")

        # Try to verify connection
        try:
            from langsmith import Client
            client = Client()
            print("✓ LangSmith client initialized successfully")
        except Exception as e:
            print(f"⚠ LangSmith connection issue: {e}")
    else:
        print("ℹ LangSmith tracing disabled")
        print("\n  To enable:")
        print("  1. Sign up at https://smith.langchain.com/")
        print("  2. Get API key from Settings → API Keys")
        print("  3. Add to .env:")
        print("     LANGCHAIN_API_KEY=ls-...")
        print("     LANGCHAIN_TRACING_V2=true")
        print("     LANGCHAIN_PROJECT=excel-rag-system")


def check_database():
    """Check database configuration"""
    print("\n" + "=" * 60)
    print("DATABASE CHECK")
    print("=" * 60)

    from src import config

    db_path = Path(config.DB_PATH)
    excel_path = Path(config.EXCEL_FILE)

    print(f"Database path: {config.DB_PATH}")
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✓ Database exists ({size_mb:.1f} MB)")
    else:
        print("✗ Database not found - run 'python main.py build' first")

    print(f"\nExcel file: {config.EXCEL_FILE}")
    if excel_path.exists():
        size_mb = excel_path.stat().st_size / (1024 * 1024)
        print(f"✓ Excel file exists ({size_mb:.1f} MB)")
    else:
        print(f"✗ Excel file not found at: {excel_path}")


def test_query():
    """Test a simple query"""
    print("\n" + "=" * 60)
    print("QUERY TEST")
    print("=" * 60)

    try:
        from src.config import print_config_summary
        print_config_summary()

        print("\n✓ Configuration loaded successfully")
        print("\nTo test a query, run:")
        print("  python main.py query \"test\" --llm mock")

    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return False

    return True


def print_recommendations():
    """Print recommendations based on configuration"""
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    from src.config import get_api_key_status, is_langsmith_enabled

    status = get_api_key_status()

    recommendations = []

    # Check LLM configuration
    if status["openai"] != "✓ Set" and status["anthropic"] != "✓ Set":
        recommendations.append({
            "priority": "HIGH",
            "message": "Add an LLM API key (OpenAI or Anthropic) to .env",
            "action": "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
        })

    # Check LangSmith
    if not is_langsmith_enabled():
        recommendations.append({
            "priority": "MEDIUM",
            "message": "Enable LangSmith for tracing and diagnostics",
            "action": "Set LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2=true in .env"
        })

    # Check database
    from src import config
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        recommendations.append({
            "priority": "HIGH",
            "message": "Build vector database from Excel file",
            "action": "Run: python main.py build --excel your_file.xlsx"
        })

    if not recommendations:
        print("\n✓ Configuration looks good! You're ready to go.")
        print("\nNext steps:")
        print("  1. Run test query: python main.py query \"test\" --llm mock")
        print("  2. Build database: python main.py build --excel your_file.xlsx")
        print("  3. Start querying: python main.py interactive")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['message']}")
            print(f"   → {rec['action']}")


def main():
    """Run all checks"""
    print("\n" + "=" * 70)
    print(" " * 15 + "EXCEL-RAG ENVIRONMENT CHECKER")
    print("=" * 70)

    # Run checks
    env_ok = check_env_file()
    deps_ok = check_dependencies()

    if env_ok and deps_ok:
        check_api_keys()
        check_langsmith()
        check_database()
        test_query()
        print_recommendations()

    print("\n" + "=" * 70)
    print("For more help, see: ENV_SETUP_GUIDE.md")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
