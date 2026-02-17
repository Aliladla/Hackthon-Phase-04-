# Technical Research: Real-Time Collaboration (Phase 4)

**Feature**: Real-Time Collaboration
**Date**: 2025-02-17
**Status**: Research & Planning

---

## Overview

This document captures technical decisions and research for implementing real-time collaboration features in Phase 4.

---

## Decision 1: WebSocket vs Server-Sent Events (SSE)

### Options Considered

**Option A: WebSockets**
- Bidirectional communication
- Full-duplex connection
- Lower latency
- More complex to implement
- Better for real-time collaboration

**Option B: Server-Sent Events (SSE)**
- Unidirectional (server to client)
- Simpler to implement
- HTTP-based
- Limited to text data
- Not suitable for bidirectional needs

**Option C: Long Polling**
- HTTP-based
- Simple fallback
- Higher latency
- More server resources
- Not suitable for real-time

### Decision: WebSockets ✅

**Rationale**:
- Need bidirectional communication for collaborative editing
- Lower latency critical for real-time updates
- FastAPI has excellent WebSocket support
- Industry standard for real-time apps

**Trade-offs**:
- More complex than SSE
- Requires connection management
- Need fallback for older browsers (rare now)

---

## Decision 2: Message Broadcasting Strategy

### Options Considered

**Option A: In-Memory Broadcasting**
- Simple implementation
- No external dependencies
- Single server only
- Not horizontally scalable

**Option B: Redis Pub/Sub**
- Horizontal scaling support
- Reliable message delivery
- Industry standard
- Requires Redis infrastructure

**Option C: RabbitMQ/Kafka**
- Enterprise-grade messaging
- Complex setup
- Overkill for our use case
- Higher operational overhead

### Decision: Redis Pub/Sub ✅

**Rationale**:
- Enables horizontal scaling
- Simple to set up and operate
- Fast and reliable
- Already common in production stacks
- Good balance of simplicity and scalability

**Trade-offs**:
- Adds Redis dependency
- Need to manage Redis in production
- Slightly more complex than in-memory

---

## Decision 3: State Management Approach

### Options Considered

**Option A: Server as Source of Truth**
- All state changes go through server
- Server broadcasts to clients
- Consistent state guaranteed
- Higher latency for updates

**Option B: Optimistic Updates**
- Client updates UI immediately
- Send to server in background
- Reconcile on server response
- Lower perceived latency

**Option C: CRDT (Conflict-free Replicated Data Types)**
- Automatic conflict resolution
- Complex to implement
- Overkill for task management
- Better for collaborative text editing

### Decision: Optimistic Updates with Server Authority ✅

**Rationale**:
- Best user experience (instant feedback)
- Server maintains authoritative state
- Simple conflict resolution (last-write-wins)
- Suitable for task management use case

**Trade-offs**:
- Need to handle rollback on errors
- Potential for temporary inconsistency
- More complex client logic

---

## Decision 4: Conflict Resolution Strategy

### Options Considered

**Option A: Last-Write-Wins (LWW)**
- Simple to implement
- Uses timestamps
- May lose some updates
- Good for most cases

**Option B: Operational Transformation (OT)**
- Complex algorithm
- Preserves all changes
- Overkill for tasks
- Better for text editing

**Option C: Manual Conflict Resolution**
- Show conflicts to user
- User chooses resolution
- Poor UX for simple tasks
- Interrupts workflow

### Decision: Last-Write-Wins with Timestamps ✅

**Rationale**:
- Simple and predictable
- Sufficient for task management
- Rare conflicts in practice
- Can add activity log for audit trail

**Trade-offs**:
- May lose concurrent updates
- Need accurate server timestamps
- Not suitable for collaborative text editing

---

## Decision 5: Presence System Implementation

### Options Considered

**Option A: Heartbeat-Based**
- Client sends periodic heartbeats
- Server tracks last heartbeat
- Mark offline after timeout
- Simple and reliable

**Option B: Connection-Based**
- Online when WebSocket connected
- Offline when disconnected
- Immediate status updates
- May have false positives

**Option C: Hybrid Approach**
- Connection status + heartbeats
- Most accurate
- More complex
- Better reliability

### Decision: Hybrid Approach ✅

**Rationale**:
- Most accurate presence tracking
- Handles network issues gracefully
- Industry best practice
- Worth the extra complexity

**Implementation**:
- Mark online on WebSocket connect
- Send heartbeat every 30 seconds
- Mark offline after 60 seconds without heartbeat
- Immediate offline on disconnect

---

## Decision 6: Database Schema for Workspaces

### Options Considered

**Option A: Separate Workspace Tasks**
- New `workspace_tasks` table
- Duplicate task structure
- Clear separation
- More complex queries

**Option B: Extend Existing Tasks**
- Add `workspace_id` to tasks table
- Reuse existing structure
- Simpler implementation
- Nullable workspace_id for personal tasks

**Option C: Polymorphic Association**
- Tasks belong to "taskable" (user or workspace)
- Flexible but complex
- Harder to query
- Overkill for our needs

### Decision: Extend Existing Tasks Table ✅

**Rationale**:
- Reuse existing task logic
- Simple queries with workspace_id filter
- Easy migration path
- Personal tasks have NULL workspace_id

**Schema Changes**:
```sql
ALTER TABLE tasks ADD COLUMN workspace_id UUID NULL;
ALTER TABLE tasks ADD COLUMN assigned_to UUID NULL;
ALTER TABLE tasks ADD CONSTRAINT fk_workspace
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id);
```

---

## Decision 7: WebSocket Authentication

### Options Considered

**Option A: JWT in Query Parameter**
- Simple to implement
- Token visible in logs
- Security concern
- Common practice

**Option B: JWT in WebSocket Headers**
- More secure
- Not all clients support
- Browser WebSocket API limitations
- Better for native apps

**Option C: Initial HTTP Handshake**
- Authenticate via HTTP first
- Get session token
- Use session for WebSocket
- Extra round trip

### Decision: JWT in Query Parameter with Short TTL ✅

**Rationale**:
- Works with browser WebSocket API
- Simple client implementation
- Mitigate security with short-lived tokens
- Industry standard approach

**Security Measures**:
- Use short-lived tokens (5 minutes)
- Validate on every connection
- Rate limit connection attempts
- Use WSS (secure WebSocket) in production

---

## Decision 8: Message Protocol Format

### Options Considered

**Option A: JSON**
- Human-readable
- Easy to debug
- Larger payload size
- Universal support

**Option B: Protocol Buffers**
- Compact binary format
- Faster serialization
- Requires schema
- Harder to debug

**Option C: MessagePack**
- Binary JSON
- Smaller than JSON
- Less common
- Good middle ground

### Decision: JSON ✅

**Rationale**:
- Easy to debug and inspect
- Universal support
- Payload size acceptable for our use case
- Can optimize later if needed

**Message Format**:
```json
{
  "type": "task.created",
  "workspace_id": "uuid",
  "user_id": "uuid",
  "timestamp": "2025-02-17T10:30:00Z",
  "data": {
    "task": { ... }
  }
}
```

---

## Decision 9: Notification Delivery

### Options Considered

**Option A: WebSocket Only**
- Real-time delivery
- Requires active connection
- Miss notifications when offline
- Simple implementation

**Option B: WebSocket + Database**
- Store notifications in DB
- Deliver via WebSocket when online
- Fetch missed on reconnect
- More reliable

**Option C: WebSocket + Push Notifications**
- Real-time + mobile push
- Complex setup
- Requires mobile apps
- Future enhancement

### Decision: WebSocket + Database ✅

**Rationale**:
- Reliable delivery
- Support offline users
- Can add push later
- Good user experience

**Implementation**:
- Store all notifications in DB
- Mark as delivered when sent via WebSocket
- Fetch undelivered on connect
- Mark as read when user views

---

## Decision 10: Scaling Strategy

### Options Considered

**Option A: Vertical Scaling**
- Single powerful server
- Simple deployment
- Limited scalability
- Single point of failure

**Option B: Horizontal Scaling with Redis**
- Multiple WebSocket servers
- Redis pub/sub for broadcasting
- Load balancer with sticky sessions
- Better scalability

**Option C: Microservices Architecture**
- Separate WebSocket service
- Complex deployment
- Overkill for current scale
- Future consideration

### Decision: Horizontal Scaling with Redis ✅

**Rationale**:
- Supports growth to 1000+ concurrent users
- Reasonable complexity
- Industry standard pattern
- Can evolve to microservices later

**Architecture**:
```
Load Balancer (Sticky Sessions)
    ↓
WebSocket Server 1 ←→ Redis Pub/Sub ←→ WebSocket Server 2
    ↓                                        ↓
PostgreSQL Database
```

---

## Technology Stack Summary

### Backend
- **FastAPI**: WebSocket server
- **Redis**: Pub/sub message broker
- **PostgreSQL**: Persistent storage
- **SQLModel**: ORM
- **Pydantic**: Message validation

### Frontend
- **Native WebSocket API**: Browser WebSocket client
- **Zustand**: Real-time state management
- **React Query**: Server state synchronization
- **TypeScript**: Type-safe messages

### Infrastructure
- **Redis**: Message broker and presence cache
- **PostgreSQL**: Workspace and notification storage
- **Load Balancer**: Sticky session routing
- **WSS**: Secure WebSocket in production

---

## Performance Targets

- **Message Latency**: <100ms (p95)
- **Connection Stability**: >99.9% uptime
- **Concurrent Users**: 50+ per workspace
- **Messages/Second**: 1000+ system-wide
- **Reconnection Time**: <2 seconds

---

## Security Considerations

1. **Authentication**: JWT tokens with 5-minute TTL
2. **Authorization**: Workspace membership validation
3. **Rate Limiting**: 100 messages/minute per user
4. **Input Validation**: Pydantic schemas for all messages
5. **XSS Prevention**: Sanitize user content
6. **WSS**: Encrypted WebSocket in production

---

## Testing Strategy

### Unit Tests
- WebSocket connection manager
- Message serialization
- Presence tracking
- Notification system

### Integration Tests
- Redis pub/sub
- Database operations
- Authentication flow
- Message broadcasting

### Load Tests
- 50+ concurrent connections
- 1000+ messages/minute
- Connection stability
- Memory usage

---

## Migration Path

### Phase 4.1: Foundation
1. Add Redis to infrastructure
2. Implement WebSocket server
3. Create workspace models
4. Basic connection management

### Phase 4.2: Real-Time Sync
1. Implement message broadcasting
2. Add optimistic updates
3. Conflict resolution
4. Activity logging

### Phase 4.3: Presence & Notifications
1. Presence tracking system
2. Notification storage
3. Toast UI components
4. Notification center

### Phase 4.4: Polish
1. Performance optimization
2. Error handling
3. Comprehensive testing
4. Documentation

---

## Open Questions

1. **Q**: Should we support workspace-level permissions (owner, admin, member)?
   **A**: Yes, implement in Phase 4.1

2. **Q**: How to handle very large workspaces (100+ members)?
   **A**: Start with 50 member limit, optimize later

3. **Q**: Should notifications be email-enabled?
   **A**: Not in Phase 4, add in Phase 5

4. **Q**: How to handle message history/replay?
   **A**: Store last 100 messages per workspace in Redis

5. **Q**: Should we support workspace-level task templates?
   **A**: Not in Phase 4, future enhancement

---

## References

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Redis Pub/Sub](https://redis.io/topics/pubsub)
- [WebSocket Protocol RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [Real-Time Collaboration Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)

---

**Status**: Research complete, ready for implementation planning
**Next**: Create detailed implementation plan (plan.md)
