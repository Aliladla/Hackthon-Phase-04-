# Implementation Plan: Real-Time Collaboration (Phase 4)

**Feature**: Real-Time Collaboration with WebSockets
**Date**: 2025-02-17
**Status**: Planning Complete, Ready for Implementation

---

## Executive Summary

Phase 4 adds real-time collaboration capabilities to the todo application using WebSocket technology, Redis pub/sub for message broadcasting, and optimistic UI updates for instant feedback. This enables teams to work together on shared task lists with sub-second latency.

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Browser A   │  │  Browser B   │  │  Browser C   │     │
│  │  (React)     │  │  (React)     │  │  (React)     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │ WebSocket        │ WebSocket        │             │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                  Application Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         FastAPI WebSocket Server                      │   │
│  │  ┌────────────────┐  ┌────────────────┐             │   │
│  │  │ Connection Mgr │  │ Message Router │             │   │
│  │  └────────┬───────┘  └────────┬───────┘             │   │
│  │           │                    │                      │   │
│  │  ┌────────▼────────────────────▼───────┐            │   │
│  │  │      Event Handlers                 │            │   │
│  │  │  - Task Events                      │            │   │
│  │  │  - Presence Events                  │            │   │
│  │  │  - Notification Events              │            │   │
│  │  └─────────────────────────────────────┘            │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                                │
│  ┌──────────────────────────▼─────────────────────────┐    │
│  │              Business Logic Layer                   │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │ Workspace   │  │ Task        │  │ Presence   │ │    │
│  │  │ Service     │  │ Service     │  │ Service    │ │    │
│  │  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                    Data Layer                                 │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Redis Pub/Sub   │◄───────►│  PostgreSQL DB   │          │
│  │  - Broadcasting  │         │  - Persistent    │          │
│  │  - Presence      │         │    Storage       │          │
│  │  - Message Queue │         │  - Workspaces    │          │
│  └──────────────────┘         │  - Tasks         │          │
│                                │  - Notifications │          │
│                                └──────────────────┘          │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. WebSocket Connection Manager

**Responsibility**: Manage WebSocket connections, authentication, and lifecycle.

**Location**: `backend/websocket/manager.py`

**Key Classes**:

```python
class ConnectionManager:
    """Manages WebSocket connections for workspaces."""

    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}
        self.user_connections: Dict[UUID, Set[UUID]] = {}  # user_id -> connection_ids

    async def connect(
        self,
        websocket: WebSocket,
        workspace_id: UUID,
        user_id: UUID
    ) -> UUID:
        """Accept and register a new WebSocket connection."""

    async def disconnect(self, connection_id: UUID):
        """Remove a WebSocket connection."""

    async def broadcast_to_workspace(
        self,
        workspace_id: UUID,
        message: dict,
        exclude_user: Optional[UUID] = None
    ):
        """Broadcast message to all connections in a workspace."""

    async def send_to_user(self, user_id: UUID, message: dict):
        """Send message to specific user's connections."""
```

**Features**:
- Connection pooling per workspace
- Automatic cleanup on disconnect
- Heartbeat monitoring
- Connection limits per user

---

### 2. Redis Pub/Sub Integration

**Responsibility**: Enable message broadcasting across multiple server instances.

**Location**: `backend/websocket/redis_client.py`

**Key Classes**:

```python
class RedisClient:
    """Redis client for pub/sub messaging."""

    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()

    async def publish(self, channel: str, message: dict):
        """Publish message to Redis channel."""

    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to Redis channel and handle messages."""

    async def set_presence(
        self,
        workspace_id: UUID,
        user_id: UUID,
        status: str
    ):
        """Update user presence in Redis."""

    async def get_presence(self, workspace_id: UUID) -> List[dict]:
        """Get all online users in workspace."""
```

**Redis Data Structures**:
- **Pub/Sub Channels**: `workspace:{workspace_id}:events`
- **Presence Hash**: `workspace:{workspace_id}:presence`
- **Message History**: `workspace:{workspace_id}:messages` (List, capped at 100)

---

### 3. WebSocket Event Handlers

**Responsibility**: Process incoming WebSocket messages and trigger appropriate actions.

**Location**: `backend/websocket/handlers.py`

**Key Functions**:

```python
async def handle_task_created(
    workspace_id: UUID,
    user_id: UUID,
    data: dict,
    manager: ConnectionManager,
    redis: RedisClient
):
    """Handle task creation event."""
    # 1. Validate data
    # 2. Create task in database
    # 3. Publish to Redis
    # 4. Broadcast to workspace members

async def handle_task_updated(
    workspace_id: UUID,
    user_id: UUID,
    data: dict,
    manager: ConnectionManager,
    redis: RedisClient
):
    """Handle task update event."""

async def handle_presence_update(
    workspace_id: UUID,
    user_id: UUID,
    status: str,
    manager: ConnectionManager,
    redis: RedisClient
):
    """Handle presence status change."""
```

**Event Flow**:
1. Client sends message via WebSocket
2. Server validates message format
3. Handler processes business logic
4. Changes persisted to database
5. Event published to Redis
6. Redis broadcasts to all servers
7. Servers send to connected clients

---

### 4. Workspace Service

**Responsibility**: Business logic for workspace management.

**Location**: `backend/services/workspace_service.py`

**Key Methods**:

```python
class WorkspaceService:
    """Service for workspace operations."""

    async def create_workspace(
        self,
        name: str,
        description: str,
        owner_id: UUID
    ) -> Workspace:
        """Create a new workspace."""

    async def add_member(
        self,
        workspace_id: UUID,
        user_id: UUID,
        role: WorkspaceRole
    ) -> WorkspaceMember:
        """Add member to workspace."""

    async def generate_invite(
        self,
        workspace_id: UUID,
        created_by: UUID,
        max_uses: Optional[int] = None,
        expires_in_hours: Optional[int] = None
    ) -> WorkspaceInvite:
        """Generate invite link for workspace."""

    async def join_workspace(
        self,
        invite_token: str,
        user_id: UUID
    ) -> WorkspaceMember:
        """Join workspace using invite token."""

    async def check_permission(
        self,
        workspace_id: UUID,
        user_id: UUID,
        action: str
    ) -> bool:
        """Check if user has permission for action."""
```

---

### 5. Presence Service

**Responsibility**: Track and manage user presence.

**Location**: `backend/services/presence_service.py`

**Key Methods**:

```python
class PresenceService:
    """Service for presence tracking."""

    async def mark_online(
        self,
        workspace_id: UUID,
        user_id: UUID
    ):
        """Mark user as online in workspace."""

    async def mark_offline(
        self,
        workspace_id: UUID,
        user_id: UUID
    ):
        """Mark user as offline in workspace."""

    async def update_heartbeat(
        self,
        workspace_id: UUID,
        user_id: UUID
    ):
        """Update user's last heartbeat timestamp."""

    async def get_online_users(
        self,
        workspace_id: UUID
    ) -> List[dict]:
        """Get list of online users in workspace."""

    async def cleanup_stale_presence(self):
        """Remove stale presence entries (no heartbeat for 60s)."""
```

**Presence Logic**:
- User marked online on WebSocket connect
- Heartbeat every 30 seconds updates timestamp
- User marked offline after 60 seconds without heartbeat
- Immediate offline on WebSocket disconnect

---

### 6. Notification Service

**Responsibility**: Create and deliver notifications.

**Location**: `backend/services/notification_service.py`

**Key Methods**:

```python
class NotificationService:
    """Service for notifications."""

    async def create_notification(
        self,
        user_id: UUID,
        type: NotificationType,
        title: str,
        message: str,
        data: dict,
        workspace_id: Optional[UUID] = None
    ) -> Notification:
        """Create a new notification."""

    async def deliver_notification(
        self,
        notification: Notification,
        manager: ConnectionManager
    ):
        """Deliver notification via WebSocket if user online."""

    async def get_unread_notifications(
        self,
        user_id: UUID
    ) -> List[Notification]:
        """Get unread notifications for user."""

    async def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID
    ):
        """Mark notification as read."""
```

---

### 7. Frontend WebSocket Hook

**Responsibility**: Manage WebSocket connection from React.

**Location**: `frontend/hooks/useWebSocket.ts`

**Implementation**:

```typescript
export function useWebSocket(workspaceId: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = getAuthToken();
    const ws = new WebSocket(
      `ws://localhost:8000/ws/workspace/${workspaceId}?token=${token}`
    );

    ws.onopen = () => {
      setIsConnected(true);
      startHeartbeat(ws);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleMessage(message);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      setIsConnected(false);
      attemptReconnect();
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [workspaceId]);

  const sendMessage = useCallback((message: Partial<WebSocketMessage>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString()
      }));
    }
  }, []);

  return { isConnected, messages, sendMessage };
}
```

---

### 8. Real-Time State Management

**Responsibility**: Manage real-time state updates in frontend.

**Location**: `frontend/stores/realtimeStore.ts`

**Implementation**:

```typescript
interface RealtimeState {
  tasks: Task[];
  onlineUsers: User[];
  notifications: Notification[];

  // Actions
  addTask: (task: Task) => void;
  updateTask: (task: Task) => void;
  deleteTask: (taskId: string) => void;
  setOnlineUsers: (users: User[]) => void;
  addNotification: (notification: Notification) => void;
}

export const useRealtimeStore = create<RealtimeState>((set) => ({
  tasks: [],
  onlineUsers: [],
  notifications: [],

  addTask: (task) => set((state) => ({
    tasks: [...state.tasks, task]
  })),

  updateTask: (task) => set((state) => ({
    tasks: state.tasks.map(t => t.id === task.id ? task : t)
  })),

  deleteTask: (taskId) => set((state) => ({
    tasks: state.tasks.filter(t => t.id !== taskId)
  })),

  setOnlineUsers: (users) => set({ onlineUsers: users }),

  addNotification: (notification) => set((state) => ({
    notifications: [notification, ...state.notifications]
  }))
}));
```

---

## Database Migrations

### Migration 001: Create Workspace Tables

**File**: `backend/alembic/versions/001_create_workspace_tables.py`

```python
def upgrade():
    # Create workspace_role enum
    op.execute("CREATE TYPE workspace_role AS ENUM ('owner', 'admin', 'member', 'viewer')")

    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(), nullable=False),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create workspace_members table
    # ... (similar structure)

    # Update tasks table
    op.add_column('tasks', sa.Column('workspace_id', postgresql.UUID(), nullable=True))
    op.add_column('tasks', sa.Column('assigned_to', postgresql.UUID(), nullable=True))
    op.create_foreign_key('fk_tasks_workspace', 'tasks', 'workspaces', ['workspace_id'], ['id'])
```

---

## API Endpoints

### Workspace Endpoints

```python
# GET /api/workspaces
# List all workspaces for current user

# POST /api/workspaces
# Create new workspace

# GET /api/workspaces/{workspace_id}
# Get workspace details

# PUT /api/workspaces/{workspace_id}
# Update workspace

# DELETE /api/workspaces/{workspace_id}
# Delete workspace (owner only)

# POST /api/workspaces/{workspace_id}/invites
# Generate invite link

# POST /api/workspaces/join
# Join workspace via invite token

# GET /api/workspaces/{workspace_id}/members
# List workspace members

# DELETE /api/workspaces/{workspace_id}/members/{user_id}
# Remove member (admin/owner only)
```

---

## Security Considerations

### Authentication
- JWT token validation on WebSocket connect
- Token expiration check
- Workspace membership verification

### Authorization
- Role-based permissions (owner, admin, member, viewer)
- Action-level permission checks
- Workspace isolation

### Rate Limiting
- 10 connection attempts per minute per user
- 100 messages per minute per user
- Heartbeat required every 30 seconds

### Input Validation
- Pydantic schemas for all messages
- SQL injection prevention (SQLModel ORM)
- XSS prevention (sanitize user content)

---

## Performance Optimization

### Backend
- Connection pooling (PostgreSQL, Redis)
- Message batching for broadcasts
- Efficient Redis data structures
- Database query optimization

### Frontend
- Debounce rapid updates (100ms)
- Virtual scrolling for large lists
- Memoization of expensive computations
- Lazy loading of workspace data

### Redis
- Connection pooling
- Pipeline commands
- Appropriate TTLs
- Memory optimization

---

## Monitoring & Observability

### Metrics to Track
- Active WebSocket connections
- Message latency (p50, p95, p99)
- Redis pub/sub throughput
- Database query performance
- Error rates

### Logging
- Connection events (connect, disconnect)
- Message events (sent, received, failed)
- Error events with stack traces
- Performance metrics

### Alerting
- High error rate (>1%)
- High latency (>500ms p95)
- Connection failures
- Redis unavailability

---

## Testing Strategy

### Unit Tests
- Connection manager logic
- Message serialization
- Presence tracking
- Permission checks

### Integration Tests
- WebSocket connection flow
- Redis pub/sub
- Database operations
- Authentication

### E2E Tests
- Multi-client collaboration
- Real-time task updates
- Presence indicators
- Notification delivery

### Load Tests
- 50 concurrent connections per workspace
- 1000 messages per minute
- Connection stability (1+ hour)
- Memory usage under load

---

## Deployment Strategy

### Development
- Local Redis instance
- Single WebSocket server
- SQLite or local PostgreSQL

### Staging
- Redis cluster (3 nodes)
- 2 WebSocket servers
- Load balancer with sticky sessions
- Neon PostgreSQL

### Production
- Redis cluster (5+ nodes)
- Auto-scaling WebSocket servers (3-10)
- Load balancer (AWS ALB or similar)
- Neon PostgreSQL with read replicas

---

## Rollout Plan

### Phase 1: Foundation (Week 1)
- Backend WebSocket infrastructure
- Redis integration
- Database migrations
- Basic workspace management

### Phase 2: Real-Time Features (Week 2)
- Task synchronization
- Presence system
- Frontend WebSocket client
- Optimistic updates

### Phase 3: Enhanced Features (Week 3)
- Notifications
- Task assignment
- Activity logging
- Performance optimization

### Phase 4: Production Ready (Week 4)
- Comprehensive testing
- Load testing
- Documentation
- Deployment

---

## Risk Mitigation

### Risk 1: WebSocket Scaling
**Mitigation**: Use Redis pub/sub, implement connection limits, load test early

### Risk 2: Message Ordering
**Mitigation**: Use timestamps, implement sequence numbers, test concurrent updates

### Risk 3: Connection Stability
**Mitigation**: Auto-reconnect, message queuing, graceful degradation

### Risk 4: Data Consistency
**Mitigation**: Optimistic locking, last-write-wins, activity logging

---

## Success Criteria

Phase 4 complete when:
- ✅ All 6 user stories implemented
- ✅ WebSocket connections stable (>99.9% uptime)
- ✅ Message latency <100ms (p95)
- ✅ 50+ concurrent users per workspace
- ✅ Test coverage >80%
- ✅ Documentation complete
- ✅ Production deployment successful

---

**Status**: Plan complete, ready for implementation
**Next**: Begin implementation with Phase 1 (Foundation)
