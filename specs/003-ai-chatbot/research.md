# Research & Technical Decisions: AI-Powered Todo Chatbot (Phase 3)

**Date**: 2025-02-15
**Feature**: 003-ai-chatbot
**Purpose**: Document technical decisions, rationale, and alternatives for Phase 3

## Overview

Phase 3 adds conversational AI capabilities to the todo application using OpenAI Agents SDK and MCP SDK. Key decisions involve AI framework selection, MCP tool design, conversation context management, and integration with Phase 2 backend.

## Technical Decisions

### 1. AI Framework: OpenAI Agents SDK vs. LangChain

**Decision**: Use OpenAI Python library with function calling (OpenAI Agents SDK pattern)

**Rationale**:
- OpenAI function calling provides structured tool execution
- Direct integration with GPT-4/GPT-3.5-turbo models
- Simpler than LangChain for our focused use case
- Better control over prompts and responses
- Official OpenAI support and documentation
- Lower learning curve for team

**Implementation**:
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define tools (MCP tools)
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        }
    }
]

# Chat completion with function calling
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

**Alternatives Considered**:
- LangChain - Rejected: Too complex for our needs, adds unnecessary abstraction
- Custom NLP - Rejected: Requires training data, lower accuracy than GPT-4
- Rasa - Rejected: Overkill for task management, requires extensive training

---

### 2. MCP SDK Integration Pattern

**Decision**: Implement MCP tools as Python functions that wrap Phase 2 API calls

**Rationale**:
- MCP (Model Context Protocol) provides structured tool definitions
- Tools are discoverable by the AI agent
- Clear separation between AI logic and API calls
- Easy to test and maintain
- Follows OpenAI function calling conventions

**Implementation**:
```python
# MCP Tool Definition
class MCPTool:
    name: str
    description: str
    parameters: dict

    async def execute(self, **kwargs):
        """Execute the tool and return result"""
        pass

class CreateTaskTool(MCPTool):
    name = "create_task"
    description = "Create a new task with title and optional description"
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Task description"}
        },
        "required": ["title"]
    }

    async def execute(self, title: str, description: str = ""):
        # Call Phase 2 API
        response = await api_client.post("/api/tasks", {
            "title": title,
            "description": description
        })
        return response.json()
```

**Alternatives Considered**:
- Direct API calls in agent - Rejected: Mixes concerns, harder to test
- GraphQL - Rejected: Phase 2 uses REST, no need to change
- gRPC - Rejected: Adds complexity, REST is sufficient

---

### 3. Conversation Context Management

**Decision**: In-memory session-based context with recent message history

**Rationale**:
- Stateless chatbot service (context stored per session)
- Recent messages provide context for ambiguous references
- Lightweight and fast (no database required)
- Sufficient for Phase 3 (persistent history is Phase 4+)
- Easy to implement and test

**Implementation**:
```python
class ConversationContext:
    session_id: str
    user_id: str
    messages: List[ChatMessage]  # Recent 10 messages
    last_task_id: Optional[int] = None
    last_operation: Optional[str] = None
    created_at: datetime

    def add_message(self, role: str, content: str):
        self.messages.append(ChatMessage(role=role, content=content))
        # Keep only last 10 messages
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]

    def get_context_for_prompt(self) -> str:
        """Format context for system prompt"""
        context = []
        if self.last_task_id:
            context.append(f"Last mentioned task ID: {self.last_task_id}")
        if self.last_operation:
            context.append(f"Last operation: {self.last_operation}")
        return "\n".join(context)
```

**Alternatives Considered**:
- Database-backed history - Rejected: Overkill for Phase 3, adds complexity
- Redis cache - Rejected: Not needed for single-instance deployment
- No context - Rejected: Poor user experience, can't handle "it" or "that task"

---

### 4. Natural Language Intent Recognition

**Decision**: Use GPT-4 with structured prompts and function calling

**Rationale**:
- GPT-4 excels at intent recognition without training
- Function calling provides structured output
- System prompts guide the model's behavior
- No need for custom NLP models or training data
- High accuracy out of the box

**System Prompt**:
```
You are a helpful task management assistant. You help users manage their todo list through natural conversation.

Available operations:
- Create tasks: "Add a task to buy milk"
- View tasks: "Show me my tasks"
- Mark complete: "Mark task 5 as complete"
- Update tasks: "Change task 3 title to 'Buy groceries'"
- Delete tasks: "Delete task 7"

When users mention "it", "that task", or "the task", refer to the last mentioned task ID from context.

Always confirm destructive operations (delete) before executing.

Provide conversational, friendly responses. Don't just dump data - explain what you did.
```

**Alternatives Considered**:
- Custom intent classifier - Rejected: Requires training, lower accuracy
- Rule-based NLP - Rejected: Brittle, can't handle variations
- BERT/RoBERTa - Rejected: Requires fine-tuning, more complex

---

### 5. Authentication Strategy

**Decision**: Pass JWT token from Phase 2 to chatbot, use for all API calls

**Rationale**:
- Reuses Phase 2 authentication (no duplicate auth system)
- Chatbot acts as authenticated client on behalf of user
- Token validates user identity for API calls
- Consistent security model across web UI and chatbot

**Implementation**:
```python
class APIClient:
    def __init__(self, base_url: str, jwt_token: str):
        self.base_url = base_url
        self.jwt_token = jwt_token
        self.headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

    async def post(self, endpoint: str, data: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=self.headers
            )
            if response.status_code == 401:
                raise AuthenticationError("Token expired")
            return response
```

**Alternatives Considered**:
- Separate chatbot authentication - Rejected: Duplicates auth logic
- API key per user - Rejected: More complex, less secure
- No authentication - Rejected: Security risk, can't identify users

---

### 6. Error Handling Strategy

**Decision**: Multi-layer error handling with user-friendly messages

**Rationale**:
- OpenAI API errors (rate limits, timeouts)
- Backend API errors (404, 401, 500)
- Network errors (connection failures)
- User needs clear, actionable error messages

**Implementation**:
```python
class ErrorHandler:
    @staticmethod
    def handle_openai_error(error: Exception) -> str:
        if isinstance(error, RateLimitError):
            return "I'm receiving too many requests. Please try again in a moment."
        elif isinstance(error, APITimeoutError):
            return "I'm taking too long to respond. Please try again."
        else:
            return "I'm having trouble understanding. Could you rephrase that?"

    @staticmethod
    def handle_api_error(status_code: int, detail: str) -> str:
        if status_code == 404:
            return "I couldn't find that task. Could you check the task ID?"
        elif status_code == 401:
            return "Your session has expired. Please sign in again."
        elif status_code >= 500:
            return "The task service is temporarily unavailable. Please try again later."
        else:
            return f"Something went wrong: {detail}"
```

**Alternatives Considered**:
- Expose raw errors - Rejected: Poor user experience, security risk
- Generic error message - Rejected: Not actionable for users
- Retry without informing user - Rejected: User doesn't know what's happening

---

### 7. Deployment Architecture

**Decision**: Standalone Python service with FastAPI endpoint

**Rationale**:
- Independent deployment and scaling
- Can run alongside Phase 2 backend
- FastAPI provides async support for OpenAI/API calls
- WebSocket support for real-time chat (optional)
- Easy to containerize for Phase 4

**Implementation**:
```python
from fastapi import FastAPI, WebSocket
from chatbot.agent import ChatAgent

app = FastAPI()

@app.post("/chat")
async def chat(message: str, jwt_token: str):
    agent = ChatAgent(jwt_token=jwt_token)
    response = await agent.process_message(message)
    return {"response": response}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    # Handle WebSocket chat
    pass
```

**Alternatives Considered**:
- Embed in Phase 2 backend - Rejected: Couples services, harder to scale
- Serverless function - Rejected: Cold start issues, state management complex
- Frontend-only - Rejected: Exposes API keys, limited control

---

### 8. Model Selection: GPT-4 vs. GPT-3.5-turbo

**Decision**: Use GPT-4-turbo-preview for better intent recognition, fallback to GPT-3.5-turbo for cost

**Rationale**:
- GPT-4 has better reasoning and function calling
- GPT-3.5-turbo is faster and cheaper
- Start with GPT-4 for accuracy, optimize later
- Configurable via environment variable

**Cost Comparison**:
| Model | Input (per 1K tokens) | Output (per 1K tokens) | Speed |
|-------|----------------------|------------------------|-------|
| GPT-4-turbo | $0.01 | $0.03 | Slower |
| GPT-3.5-turbo | $0.0005 | $0.0015 | Faster |

**Implementation**:
```python
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# For production, can switch to GPT-3.5-turbo
# MODEL = "gpt-3.5-turbo"
```

**Alternatives Considered**:
- GPT-4 only - Rejected: Higher cost, may be overkill
- GPT-3.5-turbo only - Rejected: Lower accuracy for complex intents
- Claude or other models - Rejected: Stick with OpenAI for consistency

---

### 9. Conversation Flow Design

**Decision**: Agent-driven conversation with proactive clarification

**Rationale**:
- Agent asks clarifying questions when intent is unclear
- Agent confirms destructive operations
- Agent provides helpful suggestions
- Natural conversation flow

**Example Flows**:

**Ambiguous Intent**:
```
User: "Do something"
Agent: "I can help you manage your tasks. Would you like to:
        - Add a new task
        - View your tasks
        - Mark a task as complete
        - Update or delete a task?"
```

**Ambiguous Reference**:
```
User: "Mark it as complete"
Agent: "Which task would you like to mark as complete?
        (You can say the task ID or describe the task)"
```

**Confirmation**:
```
User: "Delete task 5"
Agent: "Are you sure you want to delete 'Buy groceries'?
        This cannot be undone. (yes/no)"
User: "yes"
Agent: "Done! I've deleted 'Buy groceries' from your list."
```

**Alternatives Considered**:
- Assume intent - Rejected: Leads to errors, poor UX
- Always ask for confirmation - Rejected: Slows down workflow
- No suggestions - Rejected: Users may not know what to do

---

### 10. Testing Strategy

**Decision**: Multi-layer testing with mocked OpenAI and API responses

**Rationale**:
- Unit tests don't call real OpenAI API (expensive, slow)
- Integration tests use test backend API
- E2E tests validate complete flows
- Mocking allows testing edge cases

**Implementation**:
```python
# Unit test with mocked OpenAI
@pytest.fixture
def mock_openai(mocker):
    mock_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "function": {
                        "name": "create_task",
                        "arguments": '{"title": "Buy milk"}'
                    }
                }]
            }
        }]
    }
    mocker.patch("openai.ChatCompletion.create", return_value=mock_response)

def test_create_task_intent(mock_openai):
    agent = ChatAgent()
    response = agent.process_message("Add a task to buy milk")
    assert "created" in response.lower()
```

**Alternatives Considered**:
- Only E2E tests - Rejected: Slow, expensive, hard to test edge cases
- No mocking - Rejected: Tests would be slow and costly
- Manual testing only - Rejected: Not repeatable, error-prone

---

## Dependencies Summary

### Core Dependencies
```toml
[project.dependencies]
openai = "^1.0.0"              # OpenAI API client
httpx = "^0.28.0"              # Async HTTP client
fastapi = "^0.115.0"           # Chat server (optional)
uvicorn = "^0.32.0"            # ASGI server
pydantic = "^2.10.0"           # Data validation
python-dotenv = "^1.0.0"       # Environment variables

[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "pytest-asyncio>=0.24.0",
    "pytest-mock>=3.14.0",
    "httpx>=0.28.0",  # For testing
]
```

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| OpenAI API rate limits | Implement exponential backoff, cache responses, use GPT-3.5-turbo for high volume |
| High OpenAI costs | Monitor usage, set spending limits, optimize prompts, use cheaper model when possible |
| Intent recognition failures | Provide clear examples, ask clarifying questions, log failures for improvement |
| Backend API unavailability | Implement retry logic, graceful degradation, clear error messages |
| Token expiration during chat | Detect 401 errors, prompt re-authentication, maintain session |
| Context loss in long conversations | Limit context window, summarize old messages, focus on recent context |
| Ambiguous user input | Ask clarifying questions, provide suggestions, show examples |

---

## Performance Considerations

**Response Time Breakdown**:
- OpenAI API call: 1-2 seconds (GPT-4), 0.5-1 second (GPT-3.5-turbo)
- Backend API call: 100-500ms
- Processing overhead: 50-100ms
- **Total**: 1.5-3 seconds target

**Optimization Strategies**:
- Use streaming responses for long outputs
- Cache common queries (list tasks)
- Optimize system prompts (shorter = faster)
- Use async operations for parallel API calls
- Consider GPT-3.5-turbo for simple intents

---

## Security Considerations

**API Key Protection**:
- Store in environment variables only
- Never log or expose in errors
- Rotate keys regularly
- Use separate keys for dev/prod

**Input Validation**:
- Sanitize user input before OpenAI
- Validate MCP tool inputs
- Prevent prompt injection
- Limit message length

**Authentication**:
- Validate JWT tokens
- Handle expiration gracefully
- Never log tokens
- Use HTTPS only

---

## Conclusion

All technical decisions align with hackathon requirements and Phase 2 architecture. The chatbot service uses OpenAI function calling for intent recognition and MCP tools for structured API communication. This architecture provides a solid foundation for Phase 3 while preparing for Phase 4 Kubernetes deployment.

**Ready for Phase 1 Design**: Proceed to data-model.md and MCP tool contracts generation.
