# Quickstart Guide: AI-Powered Todo Chatbot (Phase 3)

**Date**: 2025-02-15
**Feature**: 003-ai-chatbot
**Purpose**: Setup and usage instructions for the AI chatbot service

## Overview

This guide walks you through setting up the Phase 3 AI-powered chatbot service and integrating it with Phase 2 backend. The chatbot enables natural language task management using OpenAI GPT-4 and MCP tools.

**Estimated Setup Time**: 10-15 minutes

---

## Prerequisites

### Required Software

- **Python**: 3.13 or higher
- **UV**: Latest version (Python package manager)
- **Phase 2 Backend**: Must be running and accessible
- **OpenAI API Key**: Required for AI functionality

### Required Accounts

- **OpenAI Account**: Get API key from https://platform.openai.com/api-keys
- **Phase 2 User Account**: Valid JWT token from Phase 2

### Verify Prerequisites

```bash
# Check Python version
python --version  # Should be 3.13+

# Check UV installation
uv --version

# Verify Phase 2 backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

---

## Project Structure

```
hackathon2phase1/
├── backend/             # Phase 2 FastAPI backend (running)
├── frontend/            # Phase 2 Next.js frontend (running)
└── chatbot/             # Phase 3 AI chatbot service (NEW)
    ├── src/chatbot/
    ├── tests/
    ├── pyproject.toml
    └── .env
```

---

## Chatbot Setup

### 1. Navigate to Chatbot Directory

```bash
cd chatbot
```

### 2. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Save it securely (you won't see it again)

### 3. Configure Environment Variables

Create `.env` file in `chatbot/` directory:

```bash
cp .env.example .env
```

Update `.env` with your values:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo for lower cost

# Phase 2 Backend Configuration
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30

# Chatbot Configuration
CHATBOT_PORT=8001
CHATBOT_DEBUG=True
MAX_CONTEXT_MESSAGES=10
SESSION_TIMEOUT_MINUTES=30
```

**IMPORTANT**:
- Replace `OPENAI_API_KEY` with your actual API key
- Ensure `BACKEND_API_URL` points to your Phase 2 backend
- Use `gpt-3.5-turbo` if you want lower costs (slightly less accurate)

### 4. Install Dependencies

```bash
# Using UV (recommended)
uv sync

# This will:
# - Create virtual environment
# - Install all dependencies from pyproject.toml
# - Install dev dependencies (pytest, etc.)
```

### 5. Verify Installation

```bash
# Check that dependencies are installed
uv run python -c "import openai; print('OpenAI SDK installed')"
uv run python -c "import httpx; print('HTTPX installed')"
```

---

## Running the Chatbot

### Option 1: Interactive Console (Recommended for Testing)

```bash
# Run chatbot in interactive mode
uv run python -m chatbot

# You'll see:
# === Todo Chatbot ===
# Type 'exit' or 'quit' to end the conversation
#
# You: _
```

**Example Conversation**:
```
You: Add a task to buy groceries
Chatbot: I've added 'Buy groceries' to your list. It's task #42.

You: Show me my tasks
Chatbot: You have 1 task:
1. ○ Task #42: Buy groceries

You: Mark task 42 as complete
Chatbot: Done! I've marked task #42 ('Buy groceries') as complete. Great job!

You: exit
Chatbot: Goodbye! Have a productive day!
```

### Option 2: Chat Server (For Frontend Integration)

```bash
# Start chatbot server
uv run uvicorn chatbot.server.app:app --reload --host 0.0.0.0 --port 8001

# Server will be available at:
# - Chat endpoint: http://localhost:8001/chat
# - WebSocket: ws://localhost:8001/ws/chat
# - Health check: http://localhost:8001/health
```

**Test with cURL**:
```bash
# Get JWT token from Phase 2 first
TOKEN="your-jwt-token-here"

# Send chat message
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy milk",
    "jwt_token": "'$TOKEN'"
  }'
```

---

## Authentication Setup

### Get JWT Token from Phase 2

**Option 1: Via Web UI**
1. Sign in to Phase 2 frontend (http://localhost:3000/signin)
2. Open browser DevTools (F12)
3. Go to Application → Local Storage
4. Copy the `auth_token` value

**Option 2: Via API**
```bash
# Sign in via API
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'

# Response includes token:
# {
#   "user": {...},
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "expires_at": "2025-02-22T10:30:00Z"
# }
```

### Use Token with Chatbot

**Interactive Console**:
```bash
# Set token as environment variable
export JWT_TOKEN="your-token-here"

# Run chatbot
uv run python -m chatbot --token $JWT_TOKEN
```

**Chat Server**:
```bash
# Include token in API request
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks",
    "jwt_token": "your-token-here"
  }'
```

---

## Usage Guide

### Natural Language Commands

The chatbot understands various phrasings for each operation:

**Create Tasks**:
- "Add a task to buy milk"
- "Create a task: Finish project report"
- "Remind me to call mom"
- "I need to buy groceries"

**View Tasks**:
- "Show me my tasks"
- "What's on my todo list?"
- "List my tasks"
- "What do I need to do?"

**Mark Complete**:
- "Mark task 5 as complete"
- "I finished buying groceries"
- "Complete the grocery task"
- "Task 3 is done"

**Update Tasks**:
- "Change task 5 title to 'Buy organic groceries'"
- "Update the milk task to include eggs"
- "Add a note to task 3: Remember whole milk"

**Delete Tasks**:
- "Delete task 5"
- "Remove the milk task"
- "Get rid of task 7"

### Context-Aware Conversations

The chatbot remembers recent context:

```
You: Add a task to buy milk
Chatbot: I've added 'Buy milk' to your list. It's task #42.

You: Mark it as complete
Chatbot: Done! I've marked task #42 ('Buy milk') as complete.
```

### Handling Ambiguity

The chatbot asks for clarification when needed:

```
You: Do something
Chatbot: I can help you manage your tasks. Would you like to:
- Add a new task
- View your tasks
- Mark a task as complete
- Update or delete a task?

You: Show my tasks
Chatbot: You have 2 tasks:
1. ○ Task #42: Buy groceries
2. ○ Task #43: Finish report
```

---

## Testing

### Run Unit Tests

```bash
cd chatbot

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=chatbot --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_agent.py -v
```

### Run Integration Tests

```bash
# Ensure Phase 2 backend is running first
cd backend
uv run uvicorn backend.main:app --reload &

# Run integration tests
cd ../chatbot
uv run pytest tests/integration/ -v
```

### Run End-to-End Tests

```bash
# Run complete conversation flows
uv run pytest tests/e2e/ -v
```

---

## Troubleshooting

### OpenAI API Issues

**Problem**: "OpenAI API key not found"
```
Solution:
1. Check .env file has OPENAI_API_KEY set
2. Verify key starts with 'sk-'
3. Ensure .env is in chatbot/ directory
4. Restart chatbot after changing .env
```

**Problem**: "Rate limit exceeded"
```
Solution:
1. Wait a few seconds and try again
2. Check OpenAI usage limits at platform.openai.com
3. Consider using gpt-3.5-turbo (lower rate limits)
4. Implement exponential backoff in code
```

**Problem**: "Invalid API key"
```
Solution:
1. Verify key is correct (copy-paste from OpenAI)
2. Check key hasn't been revoked
3. Generate new key if needed
```

### Backend Connection Issues

**Problem**: "Cannot connect to backend API"
```
Solution:
1. Verify Phase 2 backend is running: curl http://localhost:8000/health
2. Check BACKEND_API_URL in .env
3. Ensure no firewall blocking port 8000
4. Check backend logs for errors
```

**Problem**: "Authentication failed (401)"
```
Solution:
1. Get fresh JWT token from Phase 2
2. Check token hasn't expired (7 days default)
3. Verify token format: "Bearer <token>"
4. Sign in again to get new token
```

### Chatbot Behavior Issues

**Problem**: "Chatbot doesn't understand my command"
```
Solution:
1. Try rephrasing more explicitly (e.g., "Add a task to...")
2. Use task IDs for specific operations
3. Check chatbot logs for intent recognition
4. Verify OpenAI model is gpt-4-turbo-preview
```

**Problem**: "Chatbot creates wrong task"
```
Solution:
1. Be more specific in your request
2. Include details in one message
3. Review and correct after creation
4. Check system prompt in agent/prompts.py
```

**Problem**: "Context not maintained"
```
Solution:
1. Check MAX_CONTEXT_MESSAGES in .env (default 10)
2. Verify session hasn't expired (30 min default)
3. Use explicit task IDs for clarity
4. Check conversation/context.py logic
```

---

## Development Tips

### Debugging

**Enable Debug Logging**:
```bash
# In .env
CHATBOT_DEBUG=True

# Run with verbose output
uv run python -m chatbot --debug
```

**View OpenAI API Calls**:
```python
# In chatbot/agent/agent.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Test Individual MCP Tools**:
```bash
# Run tool tests
uv run pytest tests/unit/test_mcp_tools.py -v -s
```

### Cost Optimization

**Use GPT-3.5-turbo for Development**:
```env
# In .env
OPENAI_MODEL=gpt-3.5-turbo  # ~20x cheaper than GPT-4
```

**Monitor Usage**:
- Check usage at https://platform.openai.com/usage
- Set spending limits in OpenAI dashboard
- Cache common responses (future enhancement)

**Optimize Prompts**:
- Shorter system prompts = lower costs
- Fewer context messages = lower costs
- Use function calling efficiently

### Performance Tuning

**Reduce Response Time**:
- Use `gpt-3.5-turbo` (faster than GPT-4)
- Enable streaming responses
- Cache task list queries
- Use async operations

**Handle High Load**:
- Implement rate limiting
- Use connection pooling
- Scale horizontally (multiple instances)
- Consider Redis for session storage

---

## Integration with Phase 2 Frontend

### Embed Chat UI (Optional)

Add chat component to Phase 2 frontend:

```typescript
// frontend/src/components/chat/ChatWidget.tsx
'use client';

import { useState } from 'react';

export const ChatWidget = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('http://localhost:8001/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input, jwt_token: token })
    });
    const data = await response.json();
    setMessages([...messages, { role: 'user', content: input }, { role: 'assistant', content: data.response }]);
    setInput('');
  };

  return (
    <div className="chat-widget">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>{msg.content}</div>
        ))}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} />
    </div>
  );
};
```

---

## Next Steps

After completing Phase 3 setup:

1. **Test all features**: Try all Basic Level operations via chat
2. **Optimize prompts**: Improve intent recognition accuracy
3. **Monitor costs**: Track OpenAI API usage
4. **Prepare for Phase 4**: Containerize chatbot for Kubernetes

---

## API Reference

### Chat Endpoint

**POST /chat**

Send a message to the chatbot.

**Request**:
```json
{
  "message": "Add a task to buy milk",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "response": "I've added 'Buy milk' to your list. It's task #42.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_calls": [
    {
      "tool": "create_task",
      "arguments": {"title": "Buy milk"},
      "result": {"id": 42, "title": "Buy milk", "completed": false}
    }
  ]
}
```

### WebSocket Chat

**WS /ws/chat**

Real-time chat via WebSocket.

**Connect**:
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/chat?token=your-jwt-token');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Chatbot:', data.response);
};

ws.send(JSON.stringify({ message: 'Show my tasks' }));
```

---

## Conclusion

You now have a fully functional AI-powered chatbot for task management:
- ✅ Natural language understanding (OpenAI GPT-4)
- ✅ MCP tools for structured API calls
- ✅ Context-aware conversations
- ✅ Integration with Phase 2 backend
- ✅ Interactive console and chat server

**Ready for Task Generation**: Run task generation to break down implementation into actionable steps.
