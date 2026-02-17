"""Unit tests for MCP tool executor."""
import pytest
from unittest.mock import AsyncMock
from chatbot.mcp.executor import MCPToolExecutor
from chatbot.api.client import APIError, AuthenticationError, NotFoundError


@pytest.mark.asyncio
async def test_create_task_success(mcp_executor, mock_api_client, sample_task):
    """Test successful task creation."""
    mock_api_client.post.return_value = sample_task

    result = await mcp_executor.execute(
        "create_task",
        {"title": "Buy groceries", "description": "Milk, eggs, bread"}
    )

    assert result.success is True
    assert result.tool_name == "create_task"
    assert result.result == sample_task
    assert result.error is None
    assert result.execution_time > 0

    mock_api_client.post.assert_called_once_with(
        "/api/tasks",
        {"title": "Buy groceries", "description": "Milk, eggs, bread"}
    )


@pytest.mark.asyncio
async def test_list_tasks_success(mcp_executor, mock_api_client, sample_task_list):
    """Test successful task listing."""
    mock_api_client.get.return_value = sample_task_list

    result = await mcp_executor.execute(
        "list_tasks",
        {"completed": False, "limit": 100, "offset": 0}
    )

    assert result.success is True
    assert result.tool_name == "list_tasks"
    assert result.result == sample_task_list
    assert result.error is None

    mock_api_client.get.assert_called_once_with(
        "/api/tasks",
        params={"limit": 100, "offset": 0, "completed": False}
    )


@pytest.mark.asyncio
async def test_get_task_success(mcp_executor, mock_api_client, sample_task):
    """Test successful task retrieval."""
    mock_api_client.get.return_value = sample_task

    result = await mcp_executor.execute("get_task", {"task_id": 1})

    assert result.success is True
    assert result.tool_name == "get_task"
    assert result.result == sample_task
    assert result.error is None

    mock_api_client.get.assert_called_once_with("/api/tasks/1")


@pytest.mark.asyncio
async def test_update_task_success(mcp_executor, mock_api_client, sample_task):
    """Test successful task update."""
    updated_task = {**sample_task, "title": "Buy groceries and snacks"}
    mock_api_client.patch.return_value = updated_task

    result = await mcp_executor.execute(
        "update_task",
        {"task_id": 1, "title": "Buy groceries and snacks"}
    )

    assert result.success is True
    assert result.tool_name == "update_task"
    assert result.result == updated_task
    assert result.error is None

    mock_api_client.patch.assert_called_once_with(
        "/api/tasks/1",
        {"title": "Buy groceries and snacks"}
    )


@pytest.mark.asyncio
async def test_delete_task_success(mcp_executor, mock_api_client):
    """Test successful task deletion."""
    mock_api_client.delete.return_value = None

    result = await mcp_executor.execute("delete_task", {"task_id": 1})

    assert result.success is True
    assert result.tool_name == "delete_task"
    assert result.result == {"success": True, "message": "Task 1 deleted"}
    assert result.error is None

    mock_api_client.delete.assert_called_once_with("/api/tasks/1")


@pytest.mark.asyncio
async def test_toggle_complete_success(mcp_executor, mock_api_client, sample_task):
    """Test successful task completion toggle."""
    completed_task = {**sample_task, "completed": True}
    mock_api_client.patch.return_value = completed_task

    result = await mcp_executor.execute("toggle_complete", {"task_id": 1})

    assert result.success is True
    assert result.tool_name == "toggle_complete"
    assert result.result == completed_task
    assert result.error is None

    mock_api_client.patch.assert_called_once_with("/api/tasks/1/complete")


@pytest.mark.asyncio
async def test_authentication_error_handling(mcp_executor, mock_api_client):
    """Test authentication error handling."""
    mock_api_client.post.side_effect = AuthenticationError("Token expired")

    result = await mcp_executor.execute(
        "create_task",
        {"title": "Test task"}
    )

    assert result.success is False
    assert result.tool_name == "create_task"
    assert result.result is None
    assert "session has expired" in result.error.lower()


@pytest.mark.asyncio
async def test_not_found_error_handling(mcp_executor, mock_api_client):
    """Test not found error handling."""
    mock_api_client.get.side_effect = NotFoundError("Task not found")

    result = await mcp_executor.execute("get_task", {"task_id": 999})

    assert result.success is False
    assert result.tool_name == "get_task"
    assert result.result is None
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_api_error_handling(mcp_executor, mock_api_client):
    """Test general API error handling."""
    mock_api_client.post.side_effect = APIError("Server error")

    result = await mcp_executor.execute(
        "create_task",
        {"title": "Test task"}
    )

    assert result.success is False
    assert result.tool_name == "create_task"
    assert result.result is None
    assert "Server error" in result.error


@pytest.mark.asyncio
async def test_unexpected_error_handling(mcp_executor, mock_api_client):
    """Test unexpected error handling."""
    mock_api_client.post.side_effect = ValueError("Unexpected error")

    result = await mcp_executor.execute(
        "create_task",
        {"title": "Test task"}
    )

    assert result.success is False
    assert result.tool_name == "create_task"
    assert result.result is None
    assert "Unexpected error" in result.error


@pytest.mark.asyncio
async def test_unknown_tool_error(mcp_executor):
    """Test unknown tool error handling."""
    result = await mcp_executor.execute("unknown_tool", {})

    assert result.success is False
    assert result.tool_name == "unknown_tool"
    assert result.result is None
    assert "Unknown tool" in result.error


@pytest.mark.asyncio
async def test_list_tasks_with_optional_params(mcp_executor, mock_api_client, sample_task_list):
    """Test list tasks with optional parameters."""
    mock_api_client.get.return_value = sample_task_list

    result = await mcp_executor.execute("list_tasks", {})

    assert result.success is True
    mock_api_client.get.assert_called_once_with(
        "/api/tasks",
        params={"limit": 100, "offset": 0}
    )


@pytest.mark.asyncio
async def test_update_task_partial_update(mcp_executor, mock_api_client, sample_task):
    """Test partial task update."""
    updated_task = {**sample_task, "completed": True}
    mock_api_client.patch.return_value = updated_task

    result = await mcp_executor.execute(
        "update_task",
        {"task_id": 1, "completed": True}
    )

    assert result.success is True
    mock_api_client.patch.assert_called_once_with(
        "/api/tasks/1",
        {"completed": True}
    )
