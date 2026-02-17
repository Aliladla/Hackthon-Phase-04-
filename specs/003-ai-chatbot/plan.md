# Implementation Plan: AI-Powered Todo Chatbot (Phase 3)

**Branch**: `003-ai-chatbot` | **Date**: 2025-02-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

## Summary

Build an AI-powered conversational interface for todo management using OpenAI Agents SDK and Official MCP SDK. The chatbot integrates with Phase 2 backend API and supports natural language task management. Users can create, view, update, delete, and mark tasks complete using conversational commands.

**Technical Approach**: Implement a Python-based chatbot service using OpenAI Agents SDK for natural language understanding and MCP SDK for structured API communication. The chatbot acts as an intelligent middleware between users and the Phase 2 backend, translating natural language into API calls.

## Technical Context

**Chatbot Service:**
- **Language/Version**: Python 3.13+
- **Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK, FastAPI (for chat endpoint), python-dotenv
- **AI Model**: OpenAI GPT-4 or GPT-3.5-turbo
- **Target Platform**: Python server (can run alongside Phase 2 backend)
- **Performance Goals**: Response time < 3s including API calls, 90%+ intent recognition accuracy
- **Constraints**: Stateless conversations (context maintained in session), English language only (Urdu is bonus)

**MCP Tools Layer:**
- **Purpose**: Bridge between chatbot and Phase 2 backend API
- **Tools**: create_task, list_tasks, get_task, update_task, delete_task, toggle_complete
- **Communication**: HTTP requests to Phase 2 backend with JWT authentication
- **Error Handling**: Graceful degradation, user-friendly error messages

**Integration Points:**
- Phase 2 backend API (existing endpoints)
- Phase 2 authentication (JWT tokens)
- Optional: Phase 2 frontend (embed chat UI)

**Project Type**: AI chatbot service (Python backend)
**Scale/Scope**: Single-user conversations, 6 user stories, 23 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **I. Spec-Driven Development** | Follow Specify → Plan → Tasks → Implement workflow | ✅ PASS | Currently in Plan phase after Specify |
| **II. Test-First Development** | TDD with pytest for chatbot logic and MCP tools | ✅ PASS | Tests before implementation |
| **III. Modular Architecture** | Separate concerns: NLU, MCP tools, API client, conversation manager | ✅ PASS | Clear separation of chatbot components |
| **IV. Simple CLI Interface** | N/A for Phase 3 (conversational interface) | ✅ PASS | Chat interface replaces CLI |
| **V. Minimal Viable Implementation** | Only Basic Level operations via chat | ✅ PASS | No advanced features, focus on core chat functionality |
| **VI. Fast Iteration with UV** | Use UV for Python dependencies | ✅ PASS | UV for chatbot service |

**Gate Result**: ✅ ALL CHECKS PASSED - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technical decisions for AI/MCP integration
├── data-model.md        # Phase 1: Conversation context and MCP tool schemas
├── quickstart.md        # Phase 1: Setup and usage instructions
├── contracts/           # Phase 1: MCP tool specifications
│   └── mcp-tools.md     # MCP tool definitions and schemas
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
hackathon2phase1/        # Project root (monorepo)
├── backend/             # Phase 2 FastAPI backend (unchanged)
├── frontend/            # Phase 2 Next.js frontend (unchanged)
│
└── chatbot/             # Phase 3 AI chatbot service (NEW)
    ├── pyproject.toml   # UV project configuration
    ├── .python-version  # Python 3.13
    ├── .env.example     # Environment variables template
    │
    ├── src/
    │   └── chatbot/
    │       ├── __init__.py
    │       ├── main.py          # Chatbot service entry point
    │       ├── config.py        # Environment configuration
    │       │
    │       ├── agent/           # OpenAI Agents SDK integration
    │       │   ├── __init__.py
    │       │   ├── agent.py     # Agent initialization and configuration
    │       │   ├── prompts.py   # System prompts and instructions
    │       │   └── handlers.py  # Message handling logic
    │       │
    │       ├── mcp/             # MCP SDK integration
    │       │   ├── __init__.py
    │       │   ├── tools.py     # MCP tool definitions
    │       │   ├── schemas.py   # Tool input/output schemas
    │       │   └── executor.py  # Tool execution logic
    │       │
    │       ├── api/             # API client for Phase 2 backend
    │       │   ├── __init__.py
    │       │   ├── client.py    # HTTP client for backend API
    │       │   └── auth.py      # JWT token management
    │       │
    │       ├── conversation/    # Conversation state management
    │       │   ├── __init__.py
    │       │   ├── context.py   # Conversation context tracking
    │       │   └── session.py   # Session management
    │       │
    │       └── server/          # Chat server (optional)
    │           ├── __init__.py
    │           └── app.py       # FastAPI server for chat endpoint
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py          # Pytest fixtures
        ├── unit/                # Unit tests
        │   ├── test_agent.py
        │   ├── test_mcp_tools.py
        │   └── test_context.py
        ├── integration/         # Integration tests
        │   ├── test_api_client.py
        │   └── test_conversation.py
        └── e2e/                 # End-to-end tests
            └── test_chatbot.py
```

**Structure Decision**: Separate chatbot service in `chatbot/` directory selected because:
- Clear separation from Phase 2 backend and frontend
- Independent deployment and scaling
- Can be developed and tested independently
- Reuses Phase 2 API without modifying it
- Follows microservices architecture pattern

## Complexity Tracking

> **No violations detected** - All constitution principles satisfied without exceptions.

---

## Phase 0: Research & Technical Decisions

See [research.md](./research.md) for detailed technical decisions and rationale.

**Key Research Areas:**
1. OpenAI Agents SDK vs. custom LangChain implementation
2. MCP SDK integration patterns
3. Conversation context management strategies
4. Natural language intent recognition approaches
5. Error handling and fallback mechanisms
6. Authentication token passing from Phase 2
7. Deployment options (standalone vs. embedded)

## Phase 1: Design Artifacts

- **Data Model**: [data-model.md](./data-model.md) - Conversation context, MCP tool schemas
- **Contracts**: [contracts/](./contracts/) - MCP tool specifications
- **Quickstart**: [quickstart.md](./quickstart.md) - Setup and usage guide

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ Natural Language
                     │ "Add a task to buy milk"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Chatbot Service                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           OpenAI Agents SDK                          │  │
│  │  - Natural Language Understanding                    │  │
│  │  - Intent Recognition                                │  │
│  │  - Response Generation                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │ Structured Intent                     │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           MCP Tools Layer                            │  │
│  │  - create_task(title, description)                   │  │
│  │  - list_tasks(completed)                             │  │
│  │  - update_task(id, title, description, completed)    │  │
│  │  - delete_task(id)                                   │  │
│  │  - toggle_complete(id)                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │ API Calls                             │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           API Client                                 │  │
│  │  - HTTP requests to Phase 2 backend                  │  │
│  │  - JWT authentication                                │  │
│  │  - Error handling                                    │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │ HTTP + JWT
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Phase 2 Backend API (FastAPI)                   │
│  - POST /api/tasks                                           │
│  - GET /api/tasks                                            │
│  - PUT /api/tasks/{id}                                       │
│  - DELETE /api/tasks/{id}                                    │
│  - PATCH /api/tasks/{id}/complete                            │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**OpenAI Agents SDK:**
- Understand natural language user input
- Recognize user intent (create, view, update, delete, complete)
- Extract task details from natural language
- Generate conversational responses
- Maintain conversation context
- Handle ambiguity and ask clarifying questions

**MCP Tools Layer:**
- Define structured tools for task operations
- Validate tool inputs
- Execute API calls via API client
- Handle tool errors
- Format tool outputs for agent

**API Client:**
- Make HTTP requests to Phase 2 backend
- Attach JWT authentication tokens
- Handle network errors and retries
- Parse API responses
- Map API errors to user-friendly messages

**Conversation Manager:**
- Track conversation context (last mentioned task, operation)
- Maintain session state
- Store recent message history
- Resolve ambiguous references ("that task", "the first one")

### Data Flow Example

**User**: "Add a task to buy groceries"

1. **Agent receives message** → Analyzes intent: CREATE_TASK
2. **Agent extracts details** → title: "Buy groceries"
3. **Agent calls MCP tool** → create_task(title="Buy groceries", description="")
4. **MCP tool validates** → Input is valid
5. **API client makes request** → POST /api/tasks with JWT token
6. **Backend creates task** → Returns task object with ID
7. **MCP tool formats response** → "Task created with ID 42"
8. **Agent generates response** → "I've added 'Buy groceries' to your list. It's task #42."
9. **Context updated** → Last task ID: 42, Last operation: CREATE

**User**: "Mark it as complete"

1. **Agent receives message** → Analyzes intent: MARK_COMPLETE
2. **Agent checks context** → Last task ID: 42
3. **Agent calls MCP tool** → toggle_complete(id=42)
4. **MCP tool executes** → PATCH /api/tasks/42/complete
5. **Backend updates task** → Returns updated task
6. **Agent generates response** → "Done! I've marked 'Buy groceries' as complete."

## Integration Strategy

### Phase 2 Backend Integration

**No Changes Required to Phase 2:**
- Backend API endpoints remain unchanged
- Authentication mechanism stays the same
- Database schema is not modified
- Web UI continues to work independently

**Chatbot Integration Points:**
- Uses existing Phase 2 API endpoints
- Authenticates with JWT tokens from Phase 2
- Respects user isolation (same as web UI)
- Can coexist with web UI (users choose interface)

### Authentication Flow

1. User signs in via Phase 2 web UI → Receives JWT token
2. User opens chatbot interface → Provides JWT token
3. Chatbot stores token for session → Uses for all API calls
4. Token expires → Chatbot detects 401 error → Prompts re-authentication

**Alternative**: Chatbot can have its own authentication endpoint that calls Phase 2 signin API.

### Deployment Options

**Option 1: Standalone Service (Recommended)**
- Chatbot runs as separate Python service
- Exposes chat endpoint (HTTP or WebSocket)
- Frontend embeds chat UI that calls chatbot service
- Pros: Independent scaling, clear separation
- Cons: Additional service to deploy

**Option 2: Embedded in Frontend**
- Chatbot logic runs in frontend (JavaScript)
- Uses OpenAI API directly from browser
- Pros: No additional backend service
- Cons: API key exposure, limited control

**Option 3: Embedded in Backend**
- Chatbot endpoint added to Phase 2 backend
- Shares FastAPI server with existing API
- Pros: Single deployment, shared authentication
- Cons: Couples chatbot to backend, harder to scale independently

**Selected**: Option 1 (Standalone Service) for Phase 3, can be containerized for Phase 4.

## Technology Stack

### Core Dependencies

**AI/ML:**
- `openai` - OpenAI API client
- `openai-agents-sdk` - OpenAI Agents SDK (if available, else use openai library)
- `mcp-sdk` - Official MCP SDK for tool definitions

**Backend:**
- `fastapi` - Optional chat server endpoint
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client for API calls
- `pydantic` - Data validation
- `python-dotenv` - Environment variables

**Development:**
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking support

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo

# Phase 2 Backend Configuration
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30

# Chatbot Configuration
CHATBOT_PORT=8001
CHATBOT_DEBUG=True
MAX_CONTEXT_MESSAGES=10
SESSION_TIMEOUT_MINUTES=30
```

## Testing Strategy

### Unit Tests
- Agent prompt generation
- MCP tool input validation
- API client request formatting
- Context management logic
- Intent recognition (mocked OpenAI responses)

### Integration Tests
- MCP tools calling Phase 2 API
- Authentication token handling
- Error handling and retries
- Context persistence across messages

### End-to-End Tests
- Complete conversation flows
- Multi-turn conversations with context
- All Basic Level operations via chat
- Error scenarios and recovery

### Test Coverage Goals
- Unit tests: 80%+ coverage
- Integration tests: All MCP tools and API client
- E2E tests: All 6 user stories

## Performance Considerations

**Response Time:**
- OpenAI API call: 1-2 seconds
- Backend API call: 100-500ms
- Total response time: < 3 seconds target

**Optimization Strategies:**
- Use streaming responses for long outputs
- Cache common queries (e.g., list tasks)
- Optimize prompts for faster inference
- Use async operations for API calls

**Scalability:**
- Stateless design (context in session, not memory)
- Horizontal scaling possible
- Rate limiting for OpenAI API
- Connection pooling for backend API

## Security Considerations

**API Key Protection:**
- Store OpenAI API key in environment variables
- Never expose in logs or error messages
- Rotate keys regularly

**Authentication:**
- Validate JWT tokens before processing
- Handle token expiration gracefully
- Never log or expose user tokens

**Input Validation:**
- Sanitize user input before sending to OpenAI
- Validate MCP tool inputs
- Prevent prompt injection attacks

**Error Handling:**
- Don't expose internal errors to users
- Log errors securely
- Provide generic error messages

## Next Steps

After completing Phase 3 setup:

1. **Test all features**: Follow the testing checklist
2. **Optimize prompts**: Improve intent recognition accuracy
3. **Deploy chatbot**: Run alongside Phase 2 backend
4. **Prepare for Phase 4**: Containerize for Kubernetes deployment

---

## Conclusion

Phase 3 adds conversational AI capabilities to the todo application without modifying Phase 2. The chatbot acts as an intelligent interface layer, translating natural language into structured API calls. This architecture enables users to manage tasks conversationally while maintaining all Phase 2 functionality.

**Ready for Research**: Proceed to research.md for technical decisions and rationale.
