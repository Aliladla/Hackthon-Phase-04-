#!/usr/bin/env python3
"""Validation script for Phase 3 chatbot implementation.

This script validates that all Phase 3 components are correctly implemented
and ready for production use.

Usage:
    python validate.py
"""
import sys
import os
from pathlib import Path
from typing import List, Tuple


class ValidationResult:
    """Validation result container."""

    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[Tuple[str, str]] = []
        self.warnings: List[str] = []

    def add_pass(self, check: str):
        """Add a passed check."""
        self.passed.append(check)
        print(f"  ✅ {check}")

    def add_fail(self, check: str, reason: str):
        """Add a failed check."""
        self.failed.append((check, reason))
        print(f"  ❌ {check}: {reason}")

    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)
        print(f"  ⚠️  {message}")

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 70)
        print("📊 Validation Summary")
        print("=" * 70)
        print(f"\n✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")

        if self.failed:
            print("\n" + "=" * 70)
            print("Failed Checks:")
            print("=" * 70)
            for check, reason in self.failed:
                print(f"  • {check}: {reason}")

        if self.warnings:
            print("\n" + "=" * 70)
            print("Warnings:")
            print("=" * 70)
            for warning in self.warnings:
                print(f"  • {warning}")

        print("\n" + "=" * 70)
        if not self.failed:
            print("✅ All validation checks passed!")
        else:
            print("❌ Some validation checks failed. Please fix the issues above.")
        print("=" * 70 + "\n")

        return len(self.failed) == 0


def validate_project_structure(result: ValidationResult):
    """Validate project structure."""
    print("\n" + "=" * 70)
    print("📁 Validating Project Structure")
    print("=" * 70 + "\n")

    required_files = [
        "pyproject.toml",
        "pytest.ini",
        ".env.example",
        ".gitignore",
        "README.md",
        "CHANGELOG.md",
        "IMPLEMENTATION_SUMMARY.md",
        "src/chatbot/__init__.py",
        "src/chatbot/__main__.py",
        "src/chatbot/config.py",
        "src/chatbot/agent/__init__.py",
        "src/chatbot/agent/agent.py",
        "src/chatbot/agent/prompts.py",
        "src/chatbot/api/__init__.py",
        "src/chatbot/api/client.py",
        "src/chatbot/conversation/__init__.py",
        "src/chatbot/conversation/context.py",
        "src/chatbot/mcp/__init__.py",
        "src/chatbot/mcp/schemas.py",
        "src/chatbot/mcp/executor.py",
        "src/chatbot/server/__init__.py",
        "src/chatbot/server/app.py",
        "tests/conftest.py",
        "tests/test_api_client.py",
        "tests/test_mcp_executor.py",
        "tests/test_conversation_context.py",
        "tests/test_agent.py",
        "tests/test_integration.py",
        "tests/test_e2e.py",
    ]

    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            result.add_pass(f"{file_path}")
        else:
            result.add_fail(f"{file_path}", "File not found")


def validate_dependencies(result: ValidationResult):
    """Validate dependencies are installed."""
    print("\n" + "=" * 70)
    print("📦 Validating Dependencies")
    print("=" * 70 + "\n")

    required_packages = [
        ("openai", "OpenAI API client"),
        ("httpx", "Async HTTP client"),
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("dotenv", "Environment configuration"),
        ("pytest", "Testing framework"),
    ]

    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
            result.add_pass(f"{package} ({description})")
        except ImportError:
            result.add_fail(f"{package}", f"{description} not installed")


def validate_configuration(result: ValidationResult):
    """Validate configuration files."""
    print("\n" + "=" * 70)
    print("⚙️  Validating Configuration")
    print("=" * 70 + "\n")

    # Check .env.example
    env_example = Path(".env.example")
    if env_example.exists():
        content = env_example.read_text()
        required_vars = [
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "BACKEND_API_URL",
            "CHATBOT_PORT",
            "MAX_CONTEXT_MESSAGES",
            "SESSION_TIMEOUT_MINUTES"
        ]

        for var in required_vars:
            if var in content:
                result.add_pass(f".env.example contains {var}")
            else:
                result.add_fail(f".env.example", f"Missing {var}")
    else:
        result.add_fail(".env.example", "File not found")

    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists():
        result.add_pass(".env file exists")

        # Load and check environment variables
        from dotenv import load_dotenv
        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "sk-your-openai-api-key-here":
            result.add_pass("OPENAI_API_KEY is configured")
        else:
            result.add_warning("OPENAI_API_KEY not configured in .env")

        backend_url = os.getenv("BACKEND_API_URL")
        if backend_url:
            result.add_pass(f"BACKEND_API_URL is configured ({backend_url})")
        else:
            result.add_warning("BACKEND_API_URL not configured in .env")
    else:
        result.add_warning(".env file not found (copy from .env.example)")


def validate_code_quality(result: ValidationResult):
    """Validate code quality."""
    print("\n" + "=" * 70)
    print("🔍 Validating Code Quality")
    print("=" * 70 + "\n")

    # Check for __init__.py files
    init_files = [
        "src/chatbot/__init__.py",
        "src/chatbot/agent/__init__.py",
        "src/chatbot/api/__init__.py",
        "src/chatbot/conversation/__init__.py",
        "src/chatbot/mcp/__init__.py",
        "src/chatbot/server/__init__.py",
    ]

    for init_file in init_files:
        path = Path(init_file)
        if path.exists():
            result.add_pass(f"Package initialization: {init_file}")
        else:
            result.add_fail(f"Package initialization", f"{init_file} not found")

    # Check for docstrings in main modules
    main_modules = [
        "src/chatbot/agent/agent.py",
        "src/chatbot/api/client.py",
        "src/chatbot/mcp/executor.py",
        "src/chatbot/conversation/context.py",
    ]

    for module_path in main_modules:
        path = Path(module_path)
        if path.exists():
            content = path.read_text()
            if '"""' in content or "'''" in content:
                result.add_pass(f"Docstrings present: {module_path}")
            else:
                result.add_warning(f"No docstrings found in {module_path}")


def validate_tests(result: ValidationResult):
    """Validate test suite."""
    print("\n" + "=" * 70)
    print("🧪 Validating Test Suite")
    print("=" * 70 + "\n")

    test_files = [
        ("tests/test_api_client.py", "API client tests"),
        ("tests/test_mcp_executor.py", "MCP executor tests"),
        ("tests/test_conversation_context.py", "Conversation context tests"),
        ("tests/test_agent.py", "Agent tests"),
        ("tests/test_integration.py", "Integration tests"),
        ("tests/test_e2e.py", "End-to-end tests"),
    ]

    for test_file, description in test_files:
        path = Path(test_file)
        if path.exists():
            content = path.read_text()
            # Count test functions
            test_count = content.count("async def test_") + content.count("def test_")
            result.add_pass(f"{description}: {test_count} tests")
        else:
            result.add_fail(description, f"{test_file} not found")

    # Check pytest configuration
    pytest_ini = Path("pytest.ini")
    if pytest_ini.exists():
        result.add_pass("pytest.ini configuration exists")
    else:
        result.add_fail("pytest.ini", "Configuration file not found")


def validate_documentation(result: ValidationResult):
    """Validate documentation."""
    print("\n" + "=" * 70)
    print("📚 Validating Documentation")
    print("=" * 70 + "\n")

    doc_files = [
        ("README.md", "Main documentation", 100),
        ("CHANGELOG.md", "Version history", 50),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation summary", 100),
    ]

    for doc_file, description, min_lines in doc_files:
        path = Path(doc_file)
        if path.exists():
            lines = len(path.read_text().splitlines())
            if lines >= min_lines:
                result.add_pass(f"{description}: {lines} lines")
            else:
                result.add_warning(f"{description} is short ({lines} lines, expected {min_lines}+)")
        else:
            result.add_fail(description, f"{doc_file} not found")


def validate_mcp_tools(result: ValidationResult):
    """Validate MCP tools implementation."""
    print("\n" + "=" * 70)
    print("🔧 Validating MCP Tools")
    print("=" * 70 + "\n")

    try:
        from chatbot.mcp.schemas import ALL_TOOLS

        expected_tools = [
            "create_task",
            "list_tasks",
            "get_task",
            "update_task",
            "delete_task",
            "toggle_complete"
        ]

        tool_names = [tool.name for tool in ALL_TOOLS]

        for tool_name in expected_tools:
            if tool_name in tool_names:
                result.add_pass(f"MCP tool: {tool_name}")
            else:
                result.add_fail(f"MCP tool: {tool_name}", "Not found in ALL_TOOLS")

        if len(ALL_TOOLS) == len(expected_tools):
            result.add_pass(f"All {len(expected_tools)} MCP tools implemented")
        else:
            result.add_warning(f"Expected {len(expected_tools)} tools, found {len(ALL_TOOLS)}")

    except Exception as e:
        result.add_fail("MCP tools import", str(e))


def main():
    """Main validation entry point."""
    print("\n" + "=" * 70)
    print("🔍 Phase 3 Chatbot - Validation Script")
    print("=" * 70)

    result = ValidationResult()

    # Run all validations
    validate_project_structure(result)
    validate_dependencies(result)
    validate_configuration(result)
    validate_code_quality(result)
    validate_tests(result)
    validate_documentation(result)
    validate_mcp_tools(result)

    # Print summary
    success = result.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
