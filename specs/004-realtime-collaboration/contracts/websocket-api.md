# WebSocket API Contracts (Phase 4)

**Feature**: Real-Time Collaboration
**Date**: 2025-02-17
**Status**: Design Phase

---

## Overview

This document defines the WebSocket API contracts for real-time collaboration features, including message formats, event types, and communication protocols.

---

## Connection

### WebSocket Endpoint

```
ws://localhost:8000/ws/workspace/{workspace_id}?token={jwt_token}
```

**Parameters**:
- `workspace_id`: UUID of the workspace to connect to
- `token`: JWT authentication token (query parameter)

**Example**:
```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws/workspace/123e4567-e89b-12d3-a456-426614174000?token=eyJhbGc...'
);
```

### Connection Lifecycle

```
Client                          Server
  |                               |
  |--- Connect (with JWT) ------->|
  |<-- Connection Accepted -------|
  |<-- Welcome Message ---------- |
  |                               |
  |--- Heartbeat (every 30s) ---->|
  |<-- Heartbeat ACK -------------|
  |                               |
  |--- Subscribe to Events ------>|
  |<-- Subscription Confirmed ----|
  |                               |
  |<-- Real-time Events ----------|
  |--- Send Events -------------->|
  |                               |
  |--- Disconnect --------------->|
  |<-- Goodbye Message -----------|
```

---

## Message Format

### Base Message Structure

All WebSocket messages follow this structure:

```typescript
interface WebSocketMessage {
  type: string;                    // Message type
  workspace_id: string;            // UUID of workspace
  user_id: string;                 // UUID of sender
  timestamp: string;               // ISO 8601 timestamp
  data: Record<string, any>;       // Message-specific data
  message_id?: string;             // Optional unique message ID
}
```

**Example**:
```json
{
  "type": "task.created",
  "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
  "timestamp": "2025-02-17T10:30:00.000Z",
  "message_id": "msg_abc123",
  "data": {
    "task": {
      "id": "456e7890-e12b-34d5-a678-901234567890",
      "title": "Review PR #123",
      "completed": false
    }
  }
}
```

---

## Event Types

### 1. Connection Events

#### `connection.welcome`

Sent by server immediately after successful connection.

**Direction**: Server → Client

**Data**:
```typescript
{
  type: "connection.welcome",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    workspace: {
      id: string,
      name: string,
      member_count: number
    },
    user: {
      id: string,
      email: string,
      role: "owner" | "admin" | "member" | "viewer"
    },
    online_members: Array<{
      id: string,
      email: string,
      last_seen: string
    }>
  }
}
```

**Example**:
```json
{
  "type": "connection.welcome",
  "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
  "timestamp": "2025-02-17T10:30:00.000Z",
  "data": {
    "workspace": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Team Tasks",
      "member_count": 5
    },
    "user": {
      "id": "987fcdeb-51a2-43d7-9876-543210fedcba",
      "email": "alice@example.com",
      "role": "member"
    },
    "online_members": [
      {
        "id": "111e1111-e11b-11d1-a111-111111111111",
        "email": "bob@example.com",
        "last_seen": "2025-02-17T10:29:55.000Z"
      }
    ]
  }
}
```

#### `connection.heartbeat`

Sent by client every 30 seconds to maintain connection.

**Direction**: Client → Server

**Data**:
```typescript
{
  type: "connection.heartbeat",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {}
}
```

#### `connection.heartbeat_ack`

Sent by server in response to heartbeat.

**Direction**: Server → Client

**Data**:
```typescript
{
  type: "connection.heartbeat_ack",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    server_time: string
  }
}
```

---

### 2. Task Events

#### `task.created`

Broadcast when a new task is created.

**Direction**: Bidirectional (Client → Server → All Clients)

**Data**:
```typescript
{
  type: "task.created",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    task: {
      id: string,
      title: string,
      description: string | null,
      completed: boolean,
      assigned_to: string | null,
      created_by: string,
      created_at: string,
      updated_at: string
    }
  }
}
```

**Example**:
```json
{
  "type": "task.created",
  "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
  "timestamp": "2025-02-17T10:30:00.000Z",
  "data": {
    "task": {
      "id": "456e7890-e12b-34d5-a678-901234567890",
      "title": "Review PR #123",
      "description": "Review the authentication changes",
      "completed": false,
      "assigned_to": "111e1111-e11b-11d1-a111-111111111111",
      "created_by": "987fcdeb-51a2-43d7-9876-543210fedcba",
      "created_at": "2025-02-17T10:30:00.000Z",
      "updated_at": "2025-02-17T10:30:00.000Z"
    }
  }
}
```

#### `task.updated`

Broadcast when a task is updated.

**Direction**: Bidirectional

**Data**:
```typescript
{
  type: "task.updated",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    task: {
      id: string,
      title: string,
      description: string | null,
      completed: boolean,
      assigned_to: string | null,
      last_edited_by: string,
      updated_at: string
    },
    changes: {
      field: string,
      old_value: any,
      new_value: any
    }[]
  }
}
```

#### `task.deleted`

Broadcast when a task is deleted.

**Direction**: Bidirectional

**Data**:
```typescript
{
  type: "task.deleted",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    task_id: string,
    deleted_by: string
  }
}
```

#### `task.completed`

Broadcast when a task completion status changes.

**Direction**: Bidirectional

**Data**:
```typescript
{
  type: "task.completed",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    task_id: string,
    completed: boolean,
    completed_by: string,
    completed_at: string | null
  }
}
```

---

### 3. Presence Events

#### `presence.update`

Broadcast when user presence changes (join/leave/status).

**Direction**: Server → All Clients

**Data**:
```typescript
{
  type: "presence.update",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    online_members: Array<{
      id: string,
      email: string,
      status: "online" | "away" | "offline",
      last_seen: string
    }>
  }
}
```

#### `presence.user_joined`

Broadcast when a user joins the workspace.

**Direction**: Server → All Clients

**Data**:
```typescript
{
  type: "presence.user_joined",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    user: {
      id: string,
      email: string,
      role: string
    }
  }
}
```

#### `presence.user_left`

Broadcast when a user leaves the workspace.

**Direction**: Server → All Clients

**Data**:
```typescript
{
  type: "presence.user_left",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    user_id: string,
    left_at: string
  }
}
```

#### `presence.typing`

Sent when a user is typing (optional feature).

**Direction**: Client → Server → Other Clients

**Data**:
```typescript
{
  type: "presence.typing",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    task_id: string | null,
    is_typing: boolean
  }
}
```

---

### 4. Notification Events

#### `notification.new`

Sent when a new notification is created for the user.

**Direction**: Server → Client

**Data**:
```typescript
{
  type: "notification.new",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    notification: {
      id: string,
      type: "task_assigned" | "task_completed" | "task_mentioned" | "workspace_invite" | "member_joined" | "member_left",
      title: string,
      message: string,
      data: Record<string, any>,
      created_at: string
    }
  }
}
```

**Example**:
```json
{
  "type": "notification.new",
  "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
  "timestamp": "2025-02-17T10:30:00.000Z",
  "data": {
    "notification": {
      "id": "notif_abc123",
      "type": "task_assigned",
      "title": "Task Assigned",
      "message": "Bob assigned you to 'Review PR #123'",
      "data": {
        "task_id": "456e7890-e12b-34d5-a678-901234567890",
        "assigned_by": "111e1111-e11b-11d1-a111-111111111111"
      },
      "created_at": "2025-02-17T10:30:00.000Z"
    }
  }
}
```

---

### 5. Error Events

#### `error.message`

Sent when an error occurs processing a message.

**Direction**: Server → Client

**Data**:
```typescript
{
  type: "error.message",
  workspace_id: string,
  user_id: string,
  timestamp: string,
  data: {
    error_code: string,
    error_message: string,
    original_message_id?: string
  }
}
```

**Error Codes**:
- `AUTH_FAILED`: Authentication failed
- `PERMISSION_DENIED`: User lacks permission
- `INVALID_MESSAGE`: Message format invalid
- `RATE_LIMIT_EXCEEDED`: Too many messages
- `WORKSPACE_NOT_FOUND`: Workspace doesn't exist
- `TASK_NOT_FOUND`: Task doesn't exist

**Example**:
```json
{
  "type": "error.message",
  "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
  "timestamp": "2025-02-17T10:30:00.000Z",
  "data": {
    "error_code": "PERMISSION_DENIED",
    "error_message": "You don't have permission to delete this task",
    "original_message_id": "msg_xyz789"
  }
}
```

---

## Client Implementation Example

### JavaScript/TypeScript

```typescript
class WorkspaceWebSocket {
  private ws: WebSocket;
  private heartbeatInterval: NodeJS.Timeout;

  constructor(workspaceId: string, token: string) {
    this.ws = new WebSocket(
      `ws://localhost:8000/ws/workspace/${workspaceId}?token=${token}`
    );

    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
  }

  private handleOpen() {
    console.log('WebSocket connected');

    // Start heartbeat
    this.heartbeatInterval = setInterval(() => {
      this.send({
        type: 'connection.heartbeat',
        data: {}
      });
    }, 30000);
  }

  private handleMessage(event: MessageEvent) {
    const message = JSON.parse(event.data);

    switch (message.type) {
      case 'connection.welcome':
        this.handleWelcome(message);
        break;
      case 'task.created':
        this.handleTaskCreated(message);
        break;
      case 'task.updated':
        this.handleTaskUpdated(message);
        break;
      case 'presence.update':
        this.handlePresenceUpdate(message);
        break;
      case 'notification.new':
        this.handleNotification(message);
        break;
      case 'error.message':
        this.handleError(message);
        break;
    }
  }

  private send(message: Partial<WebSocketMessage>) {
    this.ws.send(JSON.stringify({
      ...message,
      timestamp: new Date().toISOString()
    }));
  }

  public createTask(task: { title: string; description?: string }) {
    this.send({
      type: 'task.created',
      data: { task }
    });
  }

  public disconnect() {
    clearInterval(this.heartbeatInterval);
    this.ws.close();
  }
}
```

---

## Rate Limiting

### Limits

- **Connection attempts**: 10 per minute per user
- **Messages**: 100 per minute per user
- **Heartbeats**: 1 per 30 seconds (required)

### Rate Limit Response

```json
{
  "type": "error.message",
  "data": {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "error_message": "Too many messages. Please slow down.",
    "retry_after": 60
  }
}
```

---

## Authentication

### JWT Token Requirements

- Valid JWT token from Phase 2 authentication
- Token must not be expired
- User must be a member of the workspace
- Token passed as query parameter: `?token=<jwt>`

### Authentication Failure

```json
{
  "type": "error.message",
  "data": {
    "error_code": "AUTH_FAILED",
    "error_message": "Invalid or expired token"
  }
}
```

Connection will be closed immediately after authentication failure.

---

## Reconnection Strategy

### Client-Side Reconnection

```typescript
class ReconnectingWebSocket {
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
      this.connect();
    }, delay);
  }
}
```

### Exponential Backoff

- Attempt 1: 1 second
- Attempt 2: 2 seconds
- Attempt 3: 4 seconds
- Attempt 4: 8 seconds
- Attempt 5: 16 seconds

---

## Testing

### WebSocket Testing Tools

**wscat** (Command line):
```bash
wscat -c "ws://localhost:8000/ws/workspace/123?token=abc"
```

**Postman** (GUI):
- Supports WebSocket connections
- Can send/receive messages
- Good for manual testing

**Automated Testing**:
```python
import pytest
import websockets

@pytest.mark.asyncio
async def test_websocket_connection():
    uri = "ws://localhost:8000/ws/workspace/123?token=valid_token"
    async with websockets.connect(uri) as ws:
        # Receive welcome message
        welcome = await ws.recv()
        assert json.loads(welcome)["type"] == "connection.welcome"

        # Send heartbeat
        await ws.send(json.dumps({
            "type": "connection.heartbeat",
            "data": {}
        }))

        # Receive heartbeat ack
        ack = await ws.recv()
        assert json.loads(ack)["type"] == "connection.heartbeat_ack"
```

---

## Security Considerations

1. **Authentication**: Always validate JWT on connection
2. **Authorization**: Check workspace membership for all operations
3. **Input Validation**: Validate all incoming messages
4. **Rate Limiting**: Prevent abuse and DoS attacks
5. **Message Size**: Limit message size to 64KB
6. **Connection Limits**: Max 5 connections per user per workspace

---

**Status**: Contract design complete, ready for implementation
**Next**: Implement WebSocket server and client
