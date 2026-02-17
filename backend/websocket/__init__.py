"""WebSocket package for Phase 4 real-time collaboration.

This package provides WebSocket infrastructure for real-time collaboration features.

Status: 🚧 Initial implementation
"""
from backend.websocket.manager import ConnectionManager, connection_manager

__all__ = ["ConnectionManager", "connection_manager"]

__version__ = "0.1.0"
