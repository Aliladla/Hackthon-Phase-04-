# Data Model: Real-Time Collaboration (Phase 4)

**Feature**: Real-Time Collaboration
**Date**: 2025-02-17
**Status**: Design Phase

---

## Overview

This document defines the database schema and data structures for Phase 4 real-time collaboration features.

---

## Database Schema

### New Tables

#### 1. Workspaces Table

Stores shared workspace information.

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT workspace_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_created ON workspaces(created_at DESC);
```

**Fields**:
- `id`: Unique workspace identifier
- `name`: Workspace display name (e.g., "Team Tasks", "Family Chores")
- `description`: Optional workspace description
- `owner_id`: User who created the workspace
- `settings`: JSON configuration (permissions, features, etc.)
- `created_at`: Workspace creation timestamp
- `updated_at`: Last modification timestamp

#### 2. Workspace Members Table

Tracks workspace membership and roles.

```sql
CREATE TYPE workspace_role AS ENUM ('owner', 'admin', 'member', 'viewer');

CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role workspace_role NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_last_seen ON workspace_members(last_seen_at DESC);
```

**Fields**:
- `id`: Unique membership identifier
- `workspace_id`: Reference to workspace
- `user_id`: Reference to user
- `role`: User's role in workspace (owner, admin, member, viewer)
- `joined_at`: When user joined workspace
- `last_seen_at`: Last activity timestamp (for presence)

**Roles**:
- `owner`: Full control, can delete workspace
- `admin`: Manage members, edit settings
- `member`: Create, edit, delete own tasks
- `viewer`: Read-only access

#### 3. Workspace Invites Table

Manages workspace invitation links.

```sql
CREATE TABLE workspace_invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    token VARCHAR(64) UNIQUE NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    max_uses INTEGER,
    uses_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_max_uses CHECK (max_uses IS NULL OR max_uses > 0),
    CONSTRAINT valid_uses_count CHECK (uses_count >= 0)
);

CREATE INDEX idx_workspace_invites_token ON workspace_invites(token);
CREATE INDEX idx_workspace_invites_workspace ON workspace_invites(workspace_id);
CREATE INDEX idx_workspace_invites_expires ON workspace_invites(expires_at);
```

**Fields**:
- `id`: Unique invite identifier
- `workspace_id`: Reference to workspace
- `token`: Unique invite token (used in URL)
- `created_by`: User who created the invite
- `max_uses`: Maximum number of uses (NULL = unlimited)
- `uses_count`: Current number of uses
- `expires_at`: Expiration timestamp (NULL = never expires)
- `created_at`: Invite creation timestamp

#### 4. Notifications Table

Stores user notifications.

```sql
CREATE TYPE notification_type AS ENUM (
    'task_assigned',
    'task_completed',
    'task_mentioned',
    'workspace_invite',
    'member_joined',
    'member_left'
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    read BOOLEAN DEFAULT FALSE,
    delivered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read) WHERE read = FALSE;
CREATE INDEX idx_notifications_workspace ON notifications(workspace_id);
```

**Fields**:
- `id`: Unique notification identifier
- `user_id`: Recipient user
- `workspace_id`: Related workspace (if applicable)
- `type`: Notification type
- `title`: Notification title
- `message`: Notification message
- `data`: Additional JSON data (task_id, etc.)
- `read`: Whether user has read notification
- `delivered`: Whether notification was delivered via WebSocket
- `created_at`: Notification creation timestamp
- `read_at`: When user read notification

#### 5. Workspace Activity Log

Tracks all workspace activities for audit trail.

```sql
CREATE TYPE activity_type AS ENUM (
    'task_created',
    'task_updated',
    'task_deleted',
    'task_completed',
    'member_joined',
    'member_left',
    'member_role_changed',
    'workspace_updated'
);

CREATE TABLE workspace_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    type activity_type NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workspace_activity_workspace ON workspace_activity(workspace_id, created_at DESC);
CREATE INDEX idx_workspace_activity_user ON workspace_activity(user_id);
CREATE INDEX idx_workspace_activity_entity ON workspace_activity(entity_type, entity_id);
```

**Fields**:
- `id`: Unique activity identifier
- `workspace_id`: Reference to workspace
- `user_id`: User who performed action
- `type`: Activity type
- `entity_type`: Type of entity affected (task, member, etc.)
- `entity_id`: ID of affected entity
- `data`: Additional JSON data (before/after values, etc.)
- `created_at`: Activity timestamp

### Modified Tables

#### Tasks Table Updates

Add workspace support to existing tasks table.

```sql
-- Add new columns
ALTER TABLE tasks ADD COLUMN workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE tasks ADD COLUMN assigned_to UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE tasks ADD COLUMN last_edited_by UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE tasks ADD COLUMN last_edited_at TIMESTAMP WITH TIME ZONE;

-- Add indexes
CREATE INDEX idx_tasks_workspace ON tasks(workspace_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);

-- Add constraint: task must belong to user OR workspace (not both)
ALTER TABLE tasks ADD CONSTRAINT task_ownership_check
    CHECK (
        (user_id IS NOT NULL AND workspace_id IS NULL) OR
        (user_id IS NULL AND workspace_id IS NOT NULL)
    );
```

**New Fields**:
- `workspace_id`: Reference to workspace (NULL for personal tasks)
- `assigned_to`: User assigned to task (NULL for unassigned)
- `last_edited_by`: Last user to edit task
- `last_edited_at`: Last edit timestamp

---

## SQLModel Models

### Workspace Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None
    owner_id: UUID = Field(foreign_key="users.id")
    settings: dict = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: "User" = Relationship(back_populates="owned_workspaces")
    members: List["WorkspaceMember"] = Relationship(back_populates="workspace")
    tasks: List["Task"] = Relationship(back_populates="workspace")
    invites: List["WorkspaceInvite"] = Relationship(back_populates="workspace")
```

### WorkspaceMember Model

```python
from enum import Enum

class WorkspaceRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class WorkspaceMember(SQLModel, table=True):
    __tablename__ = "workspace_members"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspaces.id")
    user_id: UUID = Field(foreign_key="users.id")
    role: WorkspaceRole = Field(default=WorkspaceRole.MEMBER)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: Optional[datetime] = None

    # Relationships
    workspace: Workspace = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="workspace_memberships")
```

### Notification Model

```python
class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_MENTIONED = "task_mentioned"
    WORKSPACE_INVITE = "workspace_invite"
    MEMBER_JOINED = "member_joined"
    MEMBER_LEFT = "member_left"

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    workspace_id: Optional[UUID] = Field(foreign_key="workspaces.id", default=None)
    type: NotificationType
    title: str = Field(max_length=255)
    message: str
    data: dict = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    read: bool = Field(default=False)
    delivered: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

    # Relationships
    user: "User" = Relationship(back_populates="notifications")
    workspace: Optional[Workspace] = Relationship()
```

---

## WebSocket Message Schemas

### Base Message

```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class WebSocketMessage(BaseModel):
    type: str
    workspace_id: UUID
    user_id: UUID
    timestamp: datetime
    data: dict
```

### Task Event Messages

```python
class TaskCreatedMessage(WebSocketMessage):
    type: str = "task.created"
    data: dict  # Contains full task object

class TaskUpdatedMessage(WebSocketMessage):
    type: str = "task.updated"
    data: dict  # Contains updated task object

class TaskDeletedMessage(WebSocketMessage):
    type: str = "task.deleted"
    data: dict  # Contains task_id

class TaskCompletedMessage(WebSocketMessage):
    type: str = "task.completed"
    data: dict  # Contains task_id and completed status
```

### Presence Messages

```python
class PresenceUpdateMessage(WebSocketMessage):
    type: str = "presence.update"
    data: dict  # Contains list of online users

class UserJoinedMessage(WebSocketMessage):
    type: str = "presence.joined"
    data: dict  # Contains user info

class UserLeftMessage(WebSocketMessage):
    type: str = "presence.left"
    data: dict  # Contains user_id
```

---

## Redis Data Structures

### Presence Tracking

```python
# Redis key: workspace:{workspace_id}:presence
# Redis type: Hash
# Structure:
{
    "user_id_1": "2025-02-17T10:30:00Z",  # Last heartbeat
    "user_id_2": "2025-02-17T10:29:55Z",
    ...
}

# TTL: 60 seconds (auto-expire if no heartbeat)
```

### Message History

```python
# Redis key: workspace:{workspace_id}:messages
# Redis type: List (capped at 100 messages)
# Structure: JSON strings of WebSocketMessage
```

### Active Connections

```python
# Redis key: user:{user_id}:connections
# Redis type: Set
# Structure: Set of connection_ids
```

---

## Migration Scripts

### Migration 001: Create Workspace Tables

```sql
-- Create workspace tables
-- (SQL from above)

-- Migrate existing tasks to support workspaces
ALTER TABLE tasks ADD COLUMN workspace_id UUID;
ALTER TABLE tasks ADD COLUMN assigned_to UUID;
ALTER TABLE tasks ADD COLUMN last_edited_by UUID;
ALTER TABLE tasks ADD COLUMN last_edited_at TIMESTAMP WITH TIME ZONE;

-- All existing tasks remain personal (workspace_id = NULL)
-- No data migration needed
```

---

## Data Validation Rules

### Workspace
- Name: 1-255 characters, not empty
- Description: Optional, max 1000 characters
- Owner: Must be valid user

### WorkspaceMember
- Unique (workspace_id, user_id) combination
- Role: Must be valid enum value
- Owner role: Only one per workspace

### Notification
- User must exist
- Type must be valid enum value
- Title: 1-255 characters
- Message: Not empty

### Task (Updated)
- Must belong to user OR workspace (not both)
- If workspace task, workspace must exist
- If assigned, assignee must be workspace member

---

## Indexes Strategy

### Performance Indexes
- Workspace lookups by owner
- Member lookups by workspace and user
- Task lookups by workspace
- Notification lookups by user (unread first)
- Activity log by workspace (recent first)

### Composite Indexes
- (workspace_id, user_id) for membership checks
- (user_id, read) for unread notifications
- (workspace_id, created_at) for activity timeline

---

## Data Retention

### Notifications
- Keep for 90 days
- Archive read notifications after 30 days
- Delete after 90 days

### Activity Log
- Keep for 1 year
- Archive after 6 months
- Summarize for analytics

### Workspace Invites
- Delete expired invites daily
- Delete used single-use invites immediately

---

## Backup Strategy

### Critical Data
- Workspaces: Full backup
- Members: Full backup
- Tasks: Full backup (includes workspace tasks)

### Non-Critical Data
- Notifications: Backup last 30 days
- Activity log: Backup last 90 days
- Invites: No backup needed (regenerate if needed)

---

**Status**: Schema design complete, ready for implementation
**Next**: Create Alembic migration scripts
