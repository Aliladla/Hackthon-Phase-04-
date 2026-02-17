# Implementation Tasks: AI-Powered Todo Chatbot (Phase 3)

**Branch**: `003-ai-chatbot` | **Date**: 2025-02-15
**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Summary

This document breaks down Phase 3 implementation into actionable tasks organized by user story. Each phase represents a complete, independently testable increment of functionality.

**Total Tasks**: 65 tasks across 8 phases
**Estimated Effort**: 2-3 days for full implementation
**MVP Scope**: Phases 1-4 (Setup + US1 + US2 + US3) = 38 tasks

---

## Task Organization

Tasks are organized by user story to enable independent implementation and testing:

- **Phase 1**: Setup (10 tasks) - Project initialization and configuration
- **Phase 2**: Foundational (12 tasks) - API client, MCP tools, conversation context
- **Phase 3**: US1 - Natural Language Task Creation (8 tasks) - Create tasks via chat
- **Phase 4**: US2 - View Tasks via Conversation (8 tasks) - List and view tasks
- **Phase 5**: US3 - Mark Tasks Complete (7 tasks) - Toggle completion status
- **Phase 6**: US4 - Update Tasks (7 tasks) - Modify task details
- **Phase 7**: US5 - Delete Tasks (7 tasks) - Remove tasks with confirmation
- **Phase 8**: US6 - Contextual Conversation (6 tasks) - Context awareness and multi-turn

**Parallel Execution**: Tasks marked with [P] can run in parallel with other [P] tasks in the same phase.

---

## Phase 1: Setup (Project Initialization)

**Goal**: Initialize chatbot service structure with dependencies and configuration

**Independent Test**: Chatbot service starts without errors, environment variables load correctly

### Project Structure

- [ ] T001 Create chatbot directory structure per plan.md (chatbot/src/chatbot/, chatbot/tests/)
- [ ] T002 Initialize UV project in chatbot/ with pyproject.toml
- [ ] T003 Add chatbot dependencies to pyproject.toml (openai, httpx, fastapi, uvicorn, pydantic, python-dotenv)
- [ ] T004 Add chatbot dev dependencies (pytest, pytest-asyncio, pytest-mock)
- [ ] T005 Create chatbot/.env.example with OPENAI_API_KEY, OPENAI_MODEL, BACKEND_API_URL, CHATBOT_PORT, MAX_CONTEXT_MESSAGES, SESSION_TIMEOUT_MINUTES
- [ ] T006 Create chatbot/.gitignore with __pycache__/, *.pyc, .venv/, venv/, .env, .DS_Store
- [ ] T007 Create chatbot/README.md with Phase 3 overview and setup instructions
- [ ] T008 Create chatbot/src/chatbot/__init__.py with version info
- [ ] T009 Create chatbot/src/chatbot/config.py with environment variable loading
- [ ] T010 Create chatbot/tests/conftest.py with pytest fixtures

---

## Phase 2: Foundational (Core Infrastructure)

**Goal**: Build API client, MCP tools, and conversation context management (blocking for all user stories)

**Independent Test**: API client connects to Phase 2 backend, MCP tools execute successfully, conversation context tracks state

### API Client

- [ ] T011 [P] Create chatbot/src/chatbot/api/__init__.py
- [ ] T012 [P] Create chatbot/src/chatbot/api/client.py with APIClient class (async HTTP client using httpx)
- [ ] T013 [P] Create chatbot/src/chatbot/api/auth.py with JWT token management
- [ ] T014 [P] Implement API client methods (get, post, put, patch, delete) with JWT authentication
- [ ] T015 Add API client error handling (401, 404, 500, network errors)

### MCP Tools Layer

- [ ] T016 [P] Create chatbot/src/chatbot/mcp/__init__.py
- [ ] T017 [P] Create chatbot/src/chatbot/mcp/schemas.py with MCPToolDefinition and MCPToolResult classes
- [ ] T018 Create chatbot/src/chatbot/mcp/tools.py with base MCPTool class
- [ ] T019 Implement create_task MCP tool in chatbot/src/chatbot/mcp/tools.py
- [ ] T020 Implement list_tasks MCP tool in chatbot/src/chatbot/mcp/tools.py
- [ ] T021 Implement get_task, update_task, delete_task, toggle_complete MCP tools
- [ ] T022 Create chatbot/src/chatbot/mcp/executor.py with tool execution logic and error handling

---

## Phase 3: US1 - Natural Language Task Creation (P1 - MVP)

**Goal**: Users can create tasks using natural language

**User Story**: As a user, I want to create tasks using natural language so I can quickly add todos without filling forms.

**Independent Test**: User can say "Add a task to buy milk" and task is created via API

### OpenAI Agent Setup

- [ ] T023 [US1] Create chatbot/src/chatbot/agent/__init__.py
- [ ] T024 [US1] Create chatbot/src/chatbot/agent/prompts.py with system prompt for task management
- [ ] T025 [US1] Create chatbot/src/chatbot/agent/agent.py with ChatAgent class (OpenAI client initialization)
- [ ] T026 [US1] Implement agent.process_message() method with OpenAI function calling
- [ ] T027 [US1] Add create_task tool to agent's available functions

### Conversation Context

- [ ] T028 [P] [US1] Create chatbot/src/chatbot/conversation/__init__.py
- [ ] T029 [P] [US1] Create chatbot/src/chatbot/conversation/context.py with ConversationContext class
- [ ] T030 [US1] Implement context.add_message() and context.get_context_summary() methods

### Integration & Testing

- [ ] T031 [US1] Test create task intent: "Add a task to buy milk" → creates task with title "Buy milk"
- [ ] T032 [US1] Test create task with description: "Create a task: Finish report by Friday" → creates task with description
- [ ] T033 [US1] Test error handling: empty title, title too long, API errors

---

## Phase 4: US2 - View Tasks via Conversation (P1 - MVP)

**Goal**: Users can view their tasks through natural language queries

**User Story**: As a user, I want to view my tasks through natural language queries so I can check my todo list conversationally.

**Independent Test**: User can say "Show me my tasks" and see all tasks, or "Show incomplete tasks" and see filtered list

### Agent Enhancement

- [ ] T034 [US2] Add list_tasks tool to agent's available functions
- [ ] T035 [US2] Add get_task tool to agent's available functions
- [ ] T036 [US2] Implement response formatting for task lists (conversational, not just JSON dump)
- [ ] T037 [US2] Handle empty task list with helpful message

### Context Updates

- [ ] T038 [US2] Update context to track last viewed task list
- [ ] T039 [US2] Implement task reference resolution ("the first one", "task 5")

### Integration & Testing

- [ ] T040 [US2] Test view all tasks: "Show me my tasks" → displays all tasks
- [ ] T041 [US2] Test view incomplete tasks: "What's on my todo list?" → displays incomplete tasks
- [ ] T042 [US2] Test view completed tasks: "What have I completed?" → displays completed tasks
- [ ] T043 [US2] Test empty list: "Show my tasks" when no tasks → helpful message

---

## Phase 5: US3 - Mark Tasks Complete (P1 - MVP)

**Goal**: Users can mark tasks as complete using natural language

**User Story**: As a user, I want to mark tasks as complete using natural language so I can update task status conversationally.

**Independent Test**: User can say "Mark task 5 as complete" and task status updates

### Agent Enhancement

- [ ] T044 [US3] Add toggle_complete tool to agent's available functions
- [ ] T045 [US3] Implement intent recognition for completion commands ("mark as complete", "I finished", "done")
- [ ] T046 [US3] Handle ambiguous task references with context ("mark it as complete" → uses last mentioned task)

### Context Updates

- [ ] T047 [US3] Update context to track last operation (create, view, complete)
- [ ] T048 [US3] Update context to track last mentioned task ID

### Integration & Testing

- [ ] T049 [US3] Test mark complete by ID: "Mark task 5 as complete" → task 5 marked complete
- [ ] T050 [US3] Test mark complete by title: "I finished buying groceries" → finds and completes task
- [ ] T051 [US3] Test mark incomplete: "Mark task 3 as incomplete" → task 3 marked incomplete
- [ ] T052 [US3] Test context-aware completion: "Mark it as complete" after viewing task → completes correct task

---

## Phase 6: US4 - Update Tasks (P2)

**Goal**: Users can update task details using natural language

**User Story**: As a user, I want to update task details using natural language so I can modify tasks without using forms.

**Independent Test**: User can say "Change task 5 title to 'Buy organic groceries'" and task is updated

### Agent Enhancement

- [ ] T053 [US4] Add update_task tool to agent's available functions
- [ ] T054 [US4] Implement intent recognition for update commands ("change", "update", "modify", "rename")
- [ ] T055 [US4] Extract update details from natural language (title, description)

### Context Updates

- [ ] T056 [US4] Track last updated task in context

### Integration & Testing

- [ ] T057 [US4] Test update title: "Change task 5 title to 'Buy organic groceries'" → title updated
- [ ] T058 [US4] Test update description: "Add a note to task 3: Remember whole milk" → description updated
- [ ] T059 [US4] Test update with context: "Update its description" after discussing task → updates correct task
- [ ] T060 [US4] Test error handling: empty title, title too long, task not found

---

## Phase 7: US5 - Delete Tasks (P2)

**Goal**: Users can delete tasks using natural language with confirmation

**User Story**: As a user, I want to delete tasks using natural language so I can remove unwanted tasks conversationally.

**Independent Test**: User can say "Delete task 5", confirm deletion, and task is removed

### Agent Enhancement

- [ ] T061 [US5] Add delete_task tool to agent's available functions
- [ ] T062 [US5] Implement confirmation prompt before deletion ("Are you sure?")
- [ ] T063 [US5] Handle confirmation responses (yes/no)

### Context Updates

- [ ] T064 [US5] Track pending deletion in context (waiting for confirmation)

### Integration & Testing

- [ ] T065 [US5] Test delete with confirmation: "Delete task 5" → asks confirmation → "yes" → deletes task
- [ ] T066 [US5] Test delete cancellation: "Delete task 5" → "no" → task not deleted
- [ ] T067 [US5] Test delete by title: "Remove the milk task" → finds and deletes task

---

## Phase 8: US6 - Contextual Conversation (P2)

**Goal**: Chatbot maintains context across multiple messages

**User Story**: As a user, I want the chatbot to remember context within a conversation so I can have natural multi-turn interactions.

**Independent Test**: Chatbot correctly resolves ambiguous references using conversation context

### Context Enhancement

- [ ] T068 [US6] Implement session management with expiration (30 minutes)
- [ ] T069 [US6] Implement context summarization for long conversations
- [ ] T070 [US6] Add context to system prompt for each message

### Agent Enhancement

- [ ] T071 [US6] Implement ambiguous reference resolution ("it", "that task", "the first one")
- [ ] T072 [US6] Add clarifying questions when intent is unclear

### Integration & Testing

- [ ] T073 [US6] Test context across messages: "Add task" → "Mark it complete" → completes correct task
- [ ] T074 [US6] Test multi-turn conversation: "Show tasks" → "Delete the first one" → deletes correct task
- [ ] T075 [US6] Test clarifying questions: "Do something" → agent asks what user wants to do

---

## Optional: Chat Server & CLI

### Interactive Console (Optional but Recommended)

- [ ] T076 [P] Create chatbot/src/chatbot/__main__.py with interactive console
- [ ] T077 [P] Implement console loop (read user input, process, display response)
- [ ] T078 [P] Add exit commands ("exit", "quit", "bye")

### Chat Server (Optional for Frontend Integration)

- [ ] T079 [P] Create chatbot/src/chatbot/server/__init__.py
- [ ] T080 [P] Create chatbot/src/chatbot/server/app.py with FastAPI application
- [ ] T081 [P] Implement POST /chat endpoint (accepts message and JWT token)
- [ ] T082 [P] Implement WebSocket /ws/chat endpoint for real-time chat
- [ ] T083 [P] Add health check endpoint GET /health

---

## Dependencies & Execution Order

### Critical Path (Must Complete in Order)

1. **Phase 1 (Setup)** → Blocks all other phases
2. **Phase 2 (Foundational)** → Blocks all user story phases
3. **Phase 3 (US1 - Create)** → Recommended first for testing
4. **Phase 4 (US2 - View)** → Recommended second (need to see tasks)
5. **Phases 5-7 (US3-US5)** → Can be done in any order after US1-US2
6. **Phase 8 (US6 - Context)** → Can be done anytime, enhances all features

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T011-T015 (API client) can run in parallel with T016-T022 (MCP tools)
- T028-T029 (conversation context) can run in parallel with API client and MCP tools

**Within Phase 3 (US1)**:
- T028-T029 (context classes) can run in parallel with T023-T025 (agent setup)

**Within Phase 4 (US2)**:
- T034-T037 (agent enhancements) can run in parallel

**Optional Components**:
- T076-T078 (console) can run in parallel with T079-T083 (server)

---

## Implementation Strategy

### MVP First (Phases 1-5)

Focus on core conversational capabilities:
1. Setup project structure (Phase 1)
2. Build foundational components (Phase 2)
3. Enable task creation via chat (Phase 3)
4. Enable viewing tasks via chat (Phase 4)
5. Enable marking complete via chat (Phase 5)

**MVP Deliverable**: Users can create, view, and complete tasks via natural language (38 tasks)

### Full Feature Set (Phases 6-7)

Add remaining task operations:
1. Update tasks via chat (Phase 6) - 7 tasks
2. Delete tasks via chat (Phase 7) - 7 tasks

**Full Basic Level**: All 5 Basic Level operations via chat (52 tasks)

### Enhanced Experience (Phase 8)

Improve conversation quality:
1. Context awareness (Phase 8) - 6 tasks
2. Multi-turn conversations
3. Ambiguous reference resolution

**Production Ready**: Polished chatbot with natural conversations (58 tasks)

### Optional Interfaces (Console & Server)

Add user interfaces:
1. Interactive console for testing (3 tasks)
2. Chat server for frontend integration (5 tasks)

**Complete Implementation**: All features with multiple interfaces (66 tasks)

---

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

---

## Validation Checklist

After completing all tasks, verify:

- [ ] All 6 user stories are implemented and testable
- [ ] All 23 functional requirements from spec.md are met
- [ ] All 10 success criteria from spec.md are achieved
- [ ] All MCP tools successfully integrate with Phase 2 backend API
- [ ] Chatbot correctly interprets user intent for Basic Level operations 80%+ of the time
- [ ] Chatbot maintains conversation context across 5+ message turns
- [ ] Chatbot responds to user messages within 3 seconds (including API calls)
- [ ] Users can complete all Basic Level operations without using the web UI
- [ ] Chatbot provides helpful clarification when intent is unclear
- [ ] All errors are handled gracefully with user-friendly messages

---

## Notes

- All tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- Tasks marked [P] can run in parallel with other [P] tasks in the same phase
- Tasks marked [US1]-[US6] belong to specific user stories
- Setup and Foundational phases have no story labels (shared infrastructure)
- Each phase is independently testable with clear acceptance criteria
- MVP scope (Phases 1-5) delivers core value in 38 tasks
- Full implementation (Phases 1-8 + Optional) completes all features in 66 tasks

**Ready for Implementation**: Run implementation to execute tasks with TDD workflow

---

## Cost Considerations

### OpenAI API Costs

**Estimated Costs per 1000 Messages**:
- GPT-4-turbo: ~$0.50-$1.00 (higher accuracy)
- GPT-3.5-turbo: ~$0.02-$0.05 (lower cost)

**Optimization Strategies**:
- Use GPT-3.5-turbo for development and testing
- Switch to GPT-4 for production if needed
- Implement response caching for common queries
- Optimize system prompts (shorter = cheaper)
- Monitor usage via OpenAI dashboard

### Development Budget

For hackathon development (estimated 100-200 test messages):
- GPT-4-turbo: ~$0.10-$0.20
- GPT-3.5-turbo: ~$0.01-$0.02

**Recommendation**: Start with GPT-3.5-turbo, upgrade to GPT-4 if accuracy is insufficient.
