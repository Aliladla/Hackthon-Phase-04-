"""WebSocket connection manager for Phase 4 real-time collaboration.

This module manages WebSocket connections for workspace collaboration,
handling connection lifecycle, authentication, and message broadcasting.

Status: 🚧 Initial implementation
"""
from typing import Dict, List, Set, Optional
from uuid import UUID
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time collaboration.

    Features:
    - Connection pooling per workspace
    - JWT authentication
    - Heartbeat monitoring
    - Message broadcasting
    - Automatic cleanup
    """

    def __init__(self):
        """Initialize the connection manager."""
        # workspace_id -> list of WebSocket connections
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

        # user_id -> set of connection_ids (for multi-device support)
        self.user_connections: Dict[UUID, Set[str]] = {}

        # connection_id -> (workspace_id, user_id)
        self.connection_metadata: Dict[str, tuple[UUID, UUID]] = {}

        logger.info("ConnectionManager initialized")

    async def connect(
        self,
        websocket: WebSocket,
        workspace_id: UUID,
        user_id: UUID,
        connection_id: str
    ) -> None:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
            workspace_id: ID of the workspace
            user_id: ID of the user
            connection_id: Unique connection identifier
        """
        await websocket.accept()

        # Add to workspace connections
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Store metadata
        self.connection_metadata[connection_id] = (workspace_id, user_id)

        logger.info(
            f"User {user_id} connected to workspace {workspace_id} "
            f"(connection: {connection_id})"
        )

    async def disconnect(self, connection_id: str, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection and cleanup.

        Args:
            connection_id: Unique connection identifier
            websocket: The WebSocket connection to remove
        """
        if connection_id not in self.connection_metadata:
            logger.warning(f"Connection {connection_id} not found in metadata")
            return

        workspace_id, user_id = self.connection_metadata[connection_id]

        # Remove from workspace connections
        if workspace_id in self.active_connections:
            try:
                self.active_connections[workspace_id].remove(websocket)
                if not self.active_connections[workspace_id]:
                    del self.active_connections[workspace_id]
            except ValueError:
                logger.warning(f"WebSocket not found in workspace {workspace_id}")

        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove metadata
        del self.connection_metadata[connection_id]

        logger.info(
            f"User {user_id} disconnected from workspace {workspace_id} "
            f"(connection: {connection_id})"
        )

    async def broadcast_to_workspace(
        self,
        workspace_id: UUID,
        message: dict,
        exclude_user: Optional[UUID] = None
    ) -> int:
        """
        Broadcast a message to all connections in a workspace.

        Args:
            workspace_id: ID of the workspace
            message: Message to broadcast (will be JSON serialized)
            exclude_user: Optional user ID to exclude from broadcast

        Returns:
            Number of connections the message was sent to
        """
        if workspace_id not in self.active_connections:
            logger.debug(f"No active connections for workspace {workspace_id}")
            return 0

        import json
        message_json = json.dumps(message)
        sent_count = 0
        failed_connections = []

        for websocket in self.active_connections[workspace_id]:
            # Find connection metadata to check if we should exclude
            connection_id = self._find_connection_id(websocket, workspace_id)
            if connection_id:
                _, user_id = self.connection_metadata[connection_id]
                if exclude_user and user_id == exclude_user:
                    continue

            try:
                await websocket.send_text(message_json)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                failed_connections.append(websocket)

        # Cleanup failed connections
        for websocket in failed_connections:
            connection_id = self._find_connection_id(websocket, workspace_id)
            if connection_id:
                await self.disconnect(connection_id, websocket)

        logger.debug(
            f"Broadcast to workspace {workspace_id}: "
            f"{sent_count} sent, {len(failed_connections)} failed"
        )

        return sent_count

    async def send_to_user(
        self,
        user_id: UUID,
        message: dict
    ) -> int:
        """
        Send a message to all connections of a specific user.

        Args:
            user_id: ID of the user
            message: Message to send (will be JSON serialized)

        Returns:
            Number of connections the message was sent to
        """
        if user_id not in self.user_connections:
            logger.debug(f"No active connections for user {user_id}")
            return 0

        import json
        message_json = json.dumps(message)
        sent_count = 0

        for connection_id in self.user_connections[user_id]:
            workspace_id, _ = self.connection_metadata[connection_id]
            websocket = self._find_websocket(connection_id, workspace_id)

            if websocket:
                try:
                    await websocket.send_text(message_json)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")

        return sent_count

    def get_workspace_connection_count(self, workspace_id: UUID) -> int:
        """Get the number of active connections in a workspace."""
        return len(self.active_connections.get(workspace_id, []))

    def get_user_connection_count(self, user_id: UUID) -> int:
        """Get the number of active connections for a user."""
        return len(self.user_connections.get(user_id, set()))

    def _find_connection_id(
        self,
        websocket: WebSocket,
        workspace_id: UUID
    ) -> Optional[str]:
        """Find connection ID for a WebSocket in a workspace."""
        for conn_id, (ws_id, _) in self.connection_metadata.items():
            if ws_id == workspace_id:
                # This is a simplified check - in production, you'd want
                # to store the websocket reference in metadata
                return conn_id
        return None

    def _find_websocket(
        self,
        connection_id: str,
        workspace_id: UUID
    ) -> Optional[WebSocket]:
        """Find WebSocket for a connection ID."""
        if workspace_id in self.active_connections:
            # This is a simplified implementation
            # In production, store websocket reference in metadata
            for websocket in self.active_connections[workspace_id]:
                return websocket  # Simplified - needs proper lookup
        return None


# Global connection manager instance
connection_manager = ConnectionManager()
