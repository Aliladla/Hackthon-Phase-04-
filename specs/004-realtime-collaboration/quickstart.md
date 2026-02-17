# Phase 4 Quick Start Guide

**Feature**: Real-Time Collaboration
**Status**: 🚧 Early Development
**Last Updated**: 2025-02-17

---

## Overview

This guide helps you get started with Phase 4 real-time collaboration features. Phase 4 adds WebSocket-based real-time updates, shared workspaces, and collaborative task management.

---

## Prerequisites

Before starting Phase 4, ensure you have:

- ✅ **Phase 2 Backend**: Running at http://localhost:8000
- ✅ **Phase 2 Frontend**: Running at http://localhost:3000
- ✅ **Redis Server**: Required for pub/sub messaging
- ✅ **PostgreSQL**: With Phase 2 database
- ✅ **Node.js 20+**: For frontend development
- ✅ **Python 3.13+**: For backend development

---

## Installation

### 1. Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Windows:**
```bash
# Use WSL or Docker
docker run -d -p 6379:6379 redis:latest
```

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

### 2. Update Backend

**Add Redis dependency:**
```bash
cd backend
uv add redis aioredis
```

**Update .env file:**
```env
# Add to backend/.env
REDIS_URL=redis://localhost:6379
REDIS_DB=0
WEBSOCKET_HEARTBEAT_INTERVAL=30
WEBSOCKET_TIMEOUT=60
```

**Run new migrations:**
```bash
# Migrations for workspace tables (coming soon)
uv run alembic upgrade head
```

### 3. Update Frontend

**Add WebSocket dependencies:**
```bash
cd frontend
pnpm add socket.io-client zustand
```

**Update .env.local:**
```env
# Add to frontend/.env.local
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_REALTIME=true
```

---

## Running Phase 4

### Start All Services

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Backend:**
```bash
cd backend
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd frontend
pnpm dev
```

### Verify Setup

**Check Redis:**
```bash
redis-cli ping
# Expected: PONG
```

**Check Backend:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Check WebSocket (when implemented):**
```bash
# Install wscat: npm install -g wscat
wscat -c "ws://localhost:8000/ws/workspace/test?token=YOUR_JWT_TOKEN"
```

---

## Usage Examples

### Creating a Workspace (Coming Soon)

```typescript
// Frontend API call
const workspace = await api.post('/api/workspaces', {
  name: 'Team Tasks',
  description: 'Shared tasks for our team'
});

console.log('Workspace created:', workspace.id);
```

### Joining a Workspace (Coming Soon)

```typescript
// Join via invite link
const invite = await api.post('/api/workspaces/join', {
  invite_token: 'abc123xyz'
});

console.log('Joined workspace:', invite.workspace_id);
```

### Connecting to WebSocket (Coming Soon)

```typescript
// Establish WebSocket connection
import { io } from 'socket.io-client';

const socket = io('ws://localhost:8000', {
  auth: {
    token: jwtToken
  },
  query: {
    workspace_id: workspaceId
  }
});

// Listen for real-time updates
socket.on('task.created', (task) => {
  console.log('New task:', task);
  // Update UI
});

socket.on('task.updated', (task) => {
  console.log('Task updated:', task);
  // Update UI
});

socket.on('presence.update', (users) => {
  console.log('Online users:', users);
  // Update presence indicators
});
```

### Real-Time Task Updates (Coming Soon)

```typescript
// Create task - broadcasts to all workspace members
const task = await api.post('/api/tasks', {
  title: 'Review PR #123',
  workspace_id: workspaceId
});

// All connected clients receive:
// { type: 'task.created', data: task }
```

---

## Testing Real-Time Features

### Manual Testing

**Test 1: Basic Connection**
1. Open two browser windows
2. Sign in as different users in each
3. Join the same workspace
4. Verify both users appear in member list

**Test 2: Real-Time Updates**
1. User A creates a task
2. Verify User B sees it appear instantly
3. User B marks task complete
4. Verify User A sees completion instantly

**Test 3: Presence Indicators**
1. User A opens workspace
2. User B opens same workspace
3. Verify both see each other as online
4. User B closes browser
5. Verify User A sees User B go offline

### Automated Testing

```bash
# Backend tests
cd backend
uv run pytest tests/test_websocket.py -v

# Frontend tests
cd frontend
pnpm test:websocket

# Integration tests
pnpm test:e2e:realtime
```

---

## Architecture Overview

### WebSocket Flow

```
Client A                    Server                      Client B
   |                          |                            |
   |--- Connect WS ---------->|                            |
   |<-- Connected ------------|                            |
   |                          |<--- Connect WS ------------|
   |                          |---- Connected ------------>|
   |                          |                            |
   |--- Create Task --------->|                            |
   |                          |--- Broadcast ------------->|
   |<-- Task Created ---------|                            |
   |                          |---- Task Created --------->|
```

### Message Broadcasting

```
WebSocket Server 1          Redis Pub/Sub          WebSocket Server 2
       |                         |                         |
       |--- Publish Message ---->|                         |
       |                         |--- Broadcast ---------->|
       |                         |                         |
       |<-- Receive Message -----|                         |
       |                         |<-- Receive Message -----|
       |                         |                         |
   Broadcast to                                      Broadcast to
   Connected Clients                                 Connected Clients
```

---

## Configuration

### Backend Configuration

**config/websocket.py** (coming soon):
```python
class WebSocketSettings:
    REDIS_URL: str = "redis://localhost:6379"
    HEARTBEAT_INTERVAL: int = 30  # seconds
    CONNECTION_TIMEOUT: int = 60  # seconds
    MAX_CONNECTIONS_PER_USER: int = 5
    MESSAGE_RATE_LIMIT: int = 100  # per minute
```

### Frontend Configuration

**config/websocket.ts** (coming soon):
```typescript
export const websocketConfig = {
  url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  timeout: 20000,
  autoConnect: true
};
```

---

## Troubleshooting

### Redis Connection Issues

**Problem**: Cannot connect to Redis
```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs
tail -f /usr/local/var/log/redis.log  # macOS
tail -f /var/log/redis/redis-server.log  # Linux
```

**Solution**: Ensure Redis is running and accessible on port 6379

### WebSocket Connection Fails

**Problem**: WebSocket connection refused
```bash
# Check backend logs
cd backend
uv run uvicorn backend.main:app --reload --log-level debug
```

**Solution**:
- Verify JWT token is valid
- Check CORS settings
- Ensure WebSocket endpoint is implemented

### Messages Not Broadcasting

**Problem**: Updates not appearing in real-time

**Solution**:
- Check Redis pub/sub is working: `redis-cli MONITOR`
- Verify all servers connected to same Redis instance
- Check WebSocket connection status in browser DevTools

### High Latency

**Problem**: Slow message delivery (>1 second)

**Solution**:
- Check Redis performance: `redis-cli --latency`
- Monitor network latency
- Verify server resources (CPU, memory)
- Consider Redis clustering for scale

---

## Development Workflow

### Adding New Real-Time Features

1. **Define Message Type**
   ```typescript
   // types/websocket.ts
   type MessageType = 'task.created' | 'task.updated' | 'your.new.type';
   ```

2. **Backend Handler**
   ```python
   # backend/websocket/handlers.py
   async def handle_your_event(data: dict):
       # Process event
       await broadcast_to_workspace(workspace_id, {
           'type': 'your.new.type',
           'data': data
       })
   ```

3. **Frontend Listener**
   ```typescript
   // hooks/useWebSocket.ts
   socket.on('your.new.type', (data) => {
       // Handle event
   });
   ```

4. **Test**
   ```bash
   # Add tests
   pytest tests/test_your_feature.py
   ```

---

## Performance Optimization

### Backend
- Use Redis connection pooling
- Implement message batching
- Add rate limiting per user
- Monitor WebSocket connections

### Frontend
- Debounce rapid updates
- Use optimistic UI updates
- Implement virtual scrolling for large lists
- Cache presence data

### Redis
- Use Redis Cluster for horizontal scaling
- Enable persistence for message history
- Monitor memory usage
- Set appropriate TTLs

---

## Security Best Practices

1. **Authentication**: Always validate JWT tokens
2. **Authorization**: Check workspace membership
3. **Rate Limiting**: Prevent message flooding
4. **Input Validation**: Sanitize all messages
5. **Encryption**: Use WSS (WebSocket Secure) in production

---

## Monitoring

### Key Metrics

- WebSocket connections: Active count
- Message latency: p50, p95, p99
- Redis pub/sub: Messages per second
- Error rate: Failed connections, dropped messages
- Memory usage: Per connection, total

### Tools

```bash
# Monitor Redis
redis-cli --stat

# Monitor WebSocket connections
# (Add monitoring endpoint to backend)
curl http://localhost:8000/api/admin/websocket/stats
```

---

## Next Steps

1. ✅ Complete WebSocket server implementation
2. ✅ Build workspace management UI
3. ✅ Implement real-time task synchronization
4. ✅ Add presence indicators
5. ✅ Create notification system
6. ✅ Write comprehensive tests

---

## Resources

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Redis Pub/Sub](https://redis.io/topics/pubsub)
- [Socket.IO Documentation](https://socket.io/docs/v4/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

---

## Support

For issues or questions:
- Check `specs/004-realtime-collaboration/README.md`
- Review backend logs: `backend/logs/`
- Check Redis logs: `redis-cli MONITOR`
- Open an issue on GitHub

---

**Status**: Phase 4 is in early development. This guide will be updated as features are implemented.
