#!/usr/bin/env python3
"""
Real-time Admin Features Module
Jeseci Smart Learning Academy - Phase 4 Enterprise Intelligence

This module provides real-time capabilities including:
- WebSocket-based live dashboards
- Admin notifications and alerts
- Concurrent editing locks
- Live system monitoring
- Event broadcasting system

Author: Cavin Otieno
"""

import sys
import os
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from admin_auth import get_current_user_from_token, AdminRole

# Initialize router
realtime_router = APIRouter()

# =============================================================================
# Connection Manager
# =============================================================================

class ConnectionManager:
    """
    Manages WebSocket connections for real-time features.
    
    Handles:
    - Multiple concurrent connections
    - Connection grouping by admin role
    - Broadcast to specific groups or all connections
    - Connection lifecycle management
    """
    
    def __init__(self):
        # Active connections: websocket_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Admin associations: admin_id -> set of websocket_ids
        self.admin_connections: Dict[str, Set[str]] = {}
        
        # Group memberships: group_name -> set of websocket_ids
        self.groups: Dict[str, Set[str]] = {
            "all_admins": set(),
            "super_admins": set(),
            "content_admins": set(),
            "analytics_admins": set(),
            "system_alerts": set(),
            "content_updates": set(),
            "user_activity": set()
        }
        
        # Lock states: content_type + content_id -> admin_id
        self.content_locks: Dict[str, str] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, admin_id: str, admin_role: str):
        """Accept new WebSocket connection"""
        websocket_id = str(uuid.uuid4())
        
        await websocket.accept()
        
        self.active_connections[websocket_id] = websocket
        self.admin_connections.setdefault(admin_id, set()).add(websocket_id)
        
        # Add to appropriate groups
        self.groups["all_admins"].add(websocket_id)
        
        if admin_role == "SUPER_ADMIN":
            self.groups["super_admins"].add(websocket_id)
            self.groups["system_alerts"].add(websocket_id)
        elif admin_role == "CONTENT_ADMIN":
            self.groups["content_admins"].add(websocket_id)
            self.groups["content_updates"].add(websocket_id)
        elif admin_role == "ANALYTICS_ADMIN":
            self.groups["analytics_admins"].add(websocket_id)
        
        # Store metadata
        self.connection_metadata[websocket_id] = {
            "admin_id": admin_id,
            "admin_role": admin_role,
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Send connection confirmation
        await self.send_personal_message(
            {
                "type": "connection_established",
                "websocket_id": websocket_id,
                "message": "Connected to Jeseci Real-time Admin System",
                "groups": self._get_member_groups(websocket_id),
                "timestamp": datetime.now().isoformat()
            },
            websocket
        )
        
        return websocket_id
    
    def _get_member_groups(self, websocket_id: str) -> List[str]:
        """Get list of groups a connection belongs to"""
        return [
            group for group, members in self.groups.items()
            if websocket_id in members
        ]
    
    async def disconnect(self, websocket_id: str, admin_id: str):
        """Handle WebSocket disconnection"""
        if websocket_id in self.active_connections:
            del self.active_connections[websocket_id]
        
        if admin_id in self.admin_connections:
            self.admin_connections[admin_id].discard(websocket_id)
            if not self.admin_connections[admin_id]:
                del self.admin_connections[admin_id]
        
        # Remove from all groups
        for group in self.groups.values():
            group.discard(websocket_id)
        
        # Remove metadata
        if websocket_id in self.connection_metadata:
            del self.connection_metadata[websocket_id]
        
        # Release any locks held by this connection
        locks_to_release = [
            key for key, holder in self.content_locks.items()
            if holder == websocket_id
        ]
        for lock_key in locks_to_release:
            del self.content_locks[lock_key]
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to single connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast_to_group(self, group_name: str, message: Dict[str, Any]):
        """Broadcast message to all connections in a group"""
        if group_name not in self.groups:
            return
        
        disconnected = []
        
        for websocket_id in self.groups[group_name]:
            if websocket_id in self.active_connections:
                try:
                    await self.active_connections[websocket_id].send_json(message)
                    # Update last activity
                    if websocket_id in self.connection_metadata:
                        self.connection_metadata[websocket_id]["last_activity"] = (
                            datetime.now().isoformat()
                        )
                except Exception:
                    disconnected.append(websocket_id)
        
        # Clean up disconnected clients
        for ws_id in disconnected:
            if ws_id in self.active_connections:
                del self.active_connections[ws_id]
            self.groups[group_name].discard(ws_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected admins"""
        await self.broadcast_to_group("all_admins", message)
    
    def request_content_lock(
        self,
        content_type: str,
        content_id: str,
        admin_id: str,
        websocket_id: str
    ) -> Dict[str, Any]:
        """
        Request exclusive edit lock on content.
        
        Returns:
        - success: Whether lock was acquired
        - locked_by: Who holds the lock (if failed)
        - lock_id: Lock identifier for release
        """
        lock_key = f"{content_type}:{content_id}"
        
        if lock_key in self.content_locks:
            holder_id = self.content_locks[lock_key]
            return {
                "success": False,
                "locked_by": holder_id,
                "message": f"Content is being edited by another admin",
                "lock_id": None
            }
        
        # Acquire lock
        self.content_locks[lock_key] = websocket_id
        
        # Notify other admins about the lock
        asyncio.create_task(
            self.broadcast_to_group("content_updates", {
                "type": "content_lock_acquired",
                "content_type": content_type,
                "content_id": content_id,
                "locked_by": admin_id,
                "lock_id": websocket_id,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return {
            "success": True,
            "locked_by": admin_id,
            "lock_id": websocket_id,
            "message": "Lock acquired successfully",
            "expires_at": (datetime.now().isoformat())
        }
    
    def release_content_lock(
        self,
        content_type: str,
        content_id: str,
        websocket_id: str
    ) -> Dict[str, Any]:
        """Release content lock"""
        lock_key = f"{content_type}:{content_id}"
        
        if lock_key not in self.content_locks:
            return {
                "success": False,
                "message": "No lock found for this content"
            }
        
        # Verify lock ownership
        if self.content_locks[lock_key] != websocket_id:
            return {
                "success": False,
                "message": "You don't hold the lock for this content"
            }
        
        # Release lock
        del self.content_locks[lock_key]
        
        # Notify other admins
        asyncio.create_task(
            self.broadcast_to_group("content_updates", {
                "type": "content_lock_released",
                "content_type": content_type,
                "content_id": content_id,
                "released_by": websocket_id,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return {
            "success": True,
            "message": "Lock released successfully"
        }
    
    def get_active_locks(self) -> List[Dict[str, Any]]:
        """Get list of all active content locks"""
        locks = []
        for lock_key, holder_ws_id in self.content_locks.items():
            content_type, content_id = lock_key.split(":")
            
            # Find admin ID from connection metadata
            admin_id = None
            for admin, ws_ids in self.admin_connections.items():
                if holder_ws_id in ws_ids:
                    admin_id = admin
                    break
            
            locks.append({
                "content_type": content_type,
                "content_id": content_id,
                "locked_by": admin_id or "unknown",
                "lock_id": holder_ws_id,
                "locked_at": self.connection_metadata.get(holder_ws_id, {}).get(
                    "connected_at", datetime.now().isoformat()
                )
            })
        
        return locks
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_connections = len(self.active_connections)
        unique_admins = len(self.admin_connections)
        
        return {
            "total_connections": total_connections,
            "unique_admins": unique_admins,
            "groups": {
                group: len(members)
                for group, members in self.groups.items()
            },
            "active_locks": len(self.content_locks),
            "connections_by_role": {
                "super_admins": len(self.groups["super_admins"]),
                "content_admins": len(self.groups["content_admins"]),
                "analytics_admins": len(self.groups["analytics_admins"])
            }
        }

# Initialize connection manager
manager = ConnectionManager()

# =============================================================================
# Data Models
# =============================================================================

class NotificationType(str, Enum):
    """Types of admin notifications"""
    SYSTEM_ALERT = "system_alert"
    CONTENT_UPDATE = "content_update"
    USER_ACTIVITY = "user_activity"
    QUIZ_COMPLETION = "quiz_completion"
    HIGH_PRIORITY = "high_priority"
    BULK_OPERATION = "bulk_operation"

@dataclass
class Notification:
    """Admin notification"""
    notification_id: str
    notification_type: NotificationType
    title: str
    message: str
    priority: int  # 1-5, higher = more urgent
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_read: bool = False
    target_groups: List[str] = field(default_factory=list)

@dataclass
class LiveMetric:
    """Real-time system metric"""
    metric_name: str
    current_value: float
    unit: str
    change_percent: float
    trend: str  # "up", "down", "stable"
    timestamp: datetime

# =============================================================================
# In-Memory Data Store
# =============================================================================

# Notification storage
notifications: Dict[str, Notification] = {}

# Live metrics cache
live_metrics: Dict[str, LiveMetric] = {}

# System alerts
system_alerts: List[Dict[str, Any]] = []

# Initialize some mock data
def initialize_realtime_data():
    """Initialize sample real-time data"""
    # Mock live metrics
    metrics = [
        LiveMetric(
            metric_name="active_users",
            current_value=847.0,
            unit="users",
            change_percent=12.5,
            trend="up",
            timestamp=datetime.now()
        ),
        LiveMetric(
            metric_name="concurrent_quizzes",
            current_value=23.0,
            unit="quizzes",
            change_percent=-5.2,
            trend="down",
            timestamp=datetime.now()
        ),
        LiveMetric(
            metric_name="api_requests_per_minute",
            current_value=1250.0,
            unit="requests",
            change_percent=8.7,
            trend="up",
            timestamp=datetime.now()
        ),
        LiveMetric(
            metric_name="average_response_time",
            current_value=145.0,
            unit="ms",
            change_percent=-15.3,
            trend="down",
            timestamp=datetime.now()
        ),
        LiveMetric(
            metric_name="database_connections",
            current_value=45.0,
            unit="connections",
            change_percent=2.1,
            trend="stable",
            timestamp=datetime.now()
        ),
        LiveMetric(
            metric_name="cache_hit_rate",
            current_value=94.2,
            unit="percent",
            change_percent=1.5,
            trend="up",
            timestamp=datetime.now()
        )
    ]
    
    for metric in metrics:
        live_metrics[metric.metric_name] = metric
    
    # Mock system alerts
    alert_list = [
        {
            "alert_id": "alert_001",
            "type": "info",
            "title": "Scheduled Maintenance",
            "message": "System maintenance scheduled for Sunday 2 AM - 4 AM UTC",
            "created_at": datetime.now().isoformat()
        },
        {
            "alert_id": "alert_002",
            "type": "warning",
            "title": "High API Usage",
            "message": "API requests increased by 25% in the last hour",
            "created_at": datetime.now().isoformat()
        }
    ]
    system_alerts.extend(alert_list)

initialize_realtime_data()

# =============================================================================
# Request/Response Models
# =============================================================================

class NotificationCreateRequest(BaseModel):
    """Request model for creating notifications"""
    notification_type: NotificationType
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    priority: int = Field(default=3, ge=1, le=5)
    target_groups: List[str] = Field(
        default=["all_admins"],
        description="Target admin groups"
    )
    expires_in_hours: int = Field(default=24, ge=1, le=168)

class NotificationResponse(BaseModel):
    """Response model for notifications"""
    success: bool
    notification: Dict[str, Any]
    broadcast_count: int

class LockRequest(BaseModel):
    """Request model for content locks"""
    content_type: str = Field(..., description="course, quiz, concept, learning_path")
    content_id: str

class LockResponse(BaseModel):
    """Response model for lock operations"""
    success: bool
    lock_details: Dict[str, Any]

class DashboardMetricsResponse(BaseModel):
    """Response model for dashboard metrics"""
    success: bool
    metrics: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    connections: Dict[str, Any]
    timestamp: str

# =============================================================================
# WebSocket Endpoint
# =============================================================================

@realtime_router.websocket("/ws/admin/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for live admin dashboard updates.
    
    Streams:
    - System metrics updates
    - User activity notifications
    - Content update alerts
    - System health notifications
    """
    admin_id = None
    admin_role = None
    websocket_id = None
    
    try:
        # Wait for initial auth message
        data = await websocket.receive_json()
        
        if data.get("type") != "auth":
            await websocket.close(code=4001)
            return
        
        admin_id = data.get("admin_id")
        admin_role = data.get("admin_role", "ADMIN")
        
        if not admin_id:
            await websocket.close(code=4001)
            return
        
        # Establish connection
        websocket_id = await manager.connect(websocket, admin_id, admin_role)
        
        # Send initial dashboard data
        await manager.send_personal_message({
            "type": "dashboard_initial",
            "metrics": get_live_metrics_data(),
            "alerts": system_alerts[:5],
            "active_locks": manager.get_active_locks(),
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Main message loop
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=300)
                
                # Handle different message types
                message_type = data.get("type")
                
                if message_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                elif message_type == "subscribe":
                    group = data.get("group")
                    if group and group in manager.groups:
                        manager.groups[group].add(websocket_id)
                        await manager.send_personal_message({
                            "type": "subscribed",
                            "group": group,
                            "timestamp": datetime.now().isoformat()
                        }, websocket)
                
                elif message_type == "unsubscribe":
                    group = data.get("group")
                    if group and group in manager.groups:
                        manager.groups[group].discard(websocket_id)
                        await manager.send_personal_message({
                            "type": "unsubscribed",
                            "group": group,
                            "timestamp": datetime.now().isoformat()
                        }, websocket)
                
                elif message_type == "request_lock":
                    lock_result = manager.request_content_lock(
                        data.get("content_type"),
                        data.get("content_id"),
                        admin_id,
                        websocket_id
                    )
                    await manager.send_personal_message({
                        "type": "lock_response",
                        **lock_result
                    }, websocket)
                
                elif message_type == "release_lock":
                    lock_result = manager.release_content_lock(
                        data.get("content_type"),
                        data.get("content_id"),
                        websocket_id
                    )
                    await manager.send_personal_message({
                        "type": "lock_released",
                        **lock_result
                    }, websocket)
                
                elif message_type == "get_metrics":
                    await manager.send_personal_message({
                        "type": "metrics_update",
                        "metrics": get_live_metrics_data(),
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                # Update last activity
                if websocket_id in manager.connection_metadata:
                    manager.connection_metadata[websocket_id]["last_activity"] = (
                        datetime.now().isoformat()
                    )
                    
            except asyncio.TimeoutError:
                # Send heartbeat on timeout
                await manager.send_personal_message({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {admin_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if admin_id and websocket_id:
            await manager.disconnect(websocket_id, admin_id)

def get_live_metrics_data() -> List[Dict[str, Any]]:
    """Convert live metrics to serializable format"""
    return [
        {
            "name": metric.metric_name,
            "value": metric.current_value,
            "unit": metric.unit,
            "change_percent": metric.change_percent,
            "trend": metric.trend,
            "timestamp": metric.timestamp.isoformat()
        }
        for metric in live_metrics.values()
    ]

# =============================================================================
# REST API Endpoints
# =============================================================================

@realtime_router.get("/realtime/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(current_user: Dict = Depends(get_current_user_from_token)):
    """
    Get real-time dashboard metrics and status.
    
    Returns current system metrics, alerts, and connection stats.
    """
    return DashboardMetricsResponse(
        success=True,
        metrics=get_live_metrics_data(),
        alerts=system_alerts[:10],
        connections=manager.get_connection_stats(),
        timestamp=datetime.now().isoformat()
    )

@realtime_router.get("/realtime/connections")
async def get_connection_status(current_user: Dict = Depends(get_current_user_from_token)):
    """
    Get current WebSocket connection statistics.
    """
    stats = manager.get_connection_stats()
    
    # Add detailed connection info (admin IDs only, not websocket IDs)
    connections_detail = {
        "by_admin": {
            admin_id: len(connections)
            for admin_id, connections in manager.admin_connections.items()
        },
        "by_group": {
            group: len(members)
            for group, members in manager.groups.items()
            if group != "all_admins"
        }
    }
    
    return {
        "success": True,
        "summary": stats,
        "details": connections_detail,
        "timestamp": datetime.now().isoformat()
    }

@realtime_router.post("/realtime/notifications", response_model=NotificationResponse)
async def create_notification(
    request: NotificationCreateRequest,
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Create and broadcast a notification to admin groups.
    
    Only SUPER_ADMIN and ADMIN roles can create notifications.
    """
    notification_id = f"notif_{uuid.uuid4().hex[:8]}"
    
    notification = Notification(
        notification_id=notification_id,
        notification_type=request.notification_type,
        title=request.title,
        message=request.message,
        priority=request.priority,
        metadata={"created_by": current_user.get("username")},
        created_at=datetime.now(),
        expires_at=datetime.now() if request.expires_in_hours == 0 else (
            datetime.now()
        ),
        target_groups=request.target_groups
    )
    
    notifications[notification_id] = notification
    
    # Broadcast to target groups
    broadcast_count = 0
    for group in request.target_groups:
        count_before = len(manager.groups.get(group, set()))
        await manager.broadcast_to_group(group, {
            "type": "notification",
            "notification": {
                "notification_id": notification.notification_id,
                "type": notification.notification_type.value,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "created_at": notification.created_at.isoformat()
            }
        })
        count_after = len(manager.groups.get(group, set()))
        broadcast_count += max(count_before, count_after)
    
    return NotificationResponse(
        success=True,
        notification={
            "notification_id": notification.notification_id,
            "type": notification.notification_type.value,
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "created_at": notification.created_at.isoformat()
        },
        broadcast_count=broadcast_count
    )

@realtime_router.get("/realtime/notifications")
async def get_notifications(
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Get notifications for the current admin.
    """
    filtered = [
        n for n in notifications.values()
        if notification_type is None or n.notification_type.value == notification_type
    ]
    
    # Sort by creation time (newest first)
    sorted_notifications = sorted(filtered, key=lambda x: x.created_at, reverse=True)
    
    return {
        "success": True,
        "notifications": [
            {
                "notification_id": n.notification_id,
                "type": n.notification_type.value,
                "title": n.title,
                "message": n.message,
                "priority": n.priority,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat()
            }
            for n in sorted_notifications[:limit]
        ],
        "total": len(sorted_notifications),
        "unread_count": len([n for n in sorted_notifications if not n.is_read])
    }

@realtime_router.post("/realtime/locks", response_model=LockResponse)
async def request_content_lock(
    request: LockRequest,
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Request exclusive edit lock on content.
    
    Returns lock status and details.
    """
    # Get websocket ID for current user
    admin_id = current_user.get("user_id")
    websocket_id = None
    
    if admin_id in manager.admin_connections:
        ws_ids = manager.admin_connections[admin_id]
        if ws_ids:
            websocket_id = list(ws_ids)[0]
    
    if not websocket_id:
        return LockResponse(
            success=False,
            lock_details={"error": "No active WebSocket connection"}
        )
    
    result = manager.request_content_lock(
        request.content_type,
        request.content_id,
        admin_id,
        websocket_id
    )
    
    return LockResponse(
        success=result["success"],
        lock_details=result
    )

@realtime_router.delete("/realtime/locks")
async def release_content_lock(
    content_type: str,
    content_id: str,
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Release content lock held by current admin.
    """
    admin_id = current_user.get("user_id")
    websocket_id = None
    
    if admin_id in manager.admin_connections:
        ws_ids = manager.admin_connections[admin_id]
        if ws_ids:
            websocket_id = list(ws_ids)[0]
    
    if not websocket_id:
        return {
            "success": False,
            "message": "No active WebSocket connection"
        }
    
    result = manager.release_content_lock(content_type, content_id, websocket_id)
    
    return result

@realtime_router.get("/realtime/locks")
async def get_active_locks(current_user: Dict = Depends(get_current_user_from_token)):
    """
    Get all currently active content locks.
    """
    return {
        "success": True,
        "locks": manager.get_active_locks(),
        "total": len(manager.content_locks),
        "timestamp": datetime.now().isoformat()
    }

@realtime_router.get("/realtime/alerts")
async def get_system_alerts(current_user: Dict = Depends(get_current_user_from_token)):
    """
    Get current system alerts.
    """
    return {
        "success": True,
        "alerts": system_alerts,
        "total": len(system_alerts),
        "timestamp": datetime.now().isoformat()
    }

@realtime_router.post("/realtime/alerts")
async def create_system_alert(
    alert_type: str,
    title: str,
    message: str,
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Create a new system alert (Super Admin only).
    """
    if current_user.get("admin_role") != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Only Super Admins can create alerts"}
        )
    
    alert = {
        "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
        "type": alert_type,  # info, warning, error, critical
        "title": title,
        "message": message,
        "created_by": current_user.get("username"),
        "created_at": datetime.now().isoformat()
    }
    
    system_alerts.insert(0, alert)
    
    # Broadcast alert to all admins
    await manager.broadcast_to_group("system_alerts", {
        "type": "system_alert",
        "alert": alert
    })
    
    return {
        "success": True,
        "alert": alert,
        "broadcast_count": len(manager.groups["system_alerts"])
    }

@realtime_router.get("/realtime/metrics/{metric_name}")
async def get_specific_metric(
    metric_name: str,
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Get specific real-time metric value.
    """
    if metric_name not in live_metrics:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Metric not found"}
        )
    
    metric = live_metrics[metric_name]
    
    return {
        "success": True,
        "metric": {
            "name": metric.metric_name,
            "value": metric.current_value,
            "unit": metric.unit,
            "change_percent": metric.change_percent,
            "trend": metric.trend,
            "timestamp": metric.timestamp.isoformat()
        }
    }

@realtime_router.post("/realtime/broadcast")
async def broadcast_message(
    message_type: str,
    title: str,
    content: Dict[str, Any],
    target_groups: List[str] = ["all_admins"],
    current_user: Dict = Depends(get_current_user_from_token)
):
    """
    Broadcast custom message to admin groups.
    
    Only Super Admin can broadcast to all groups.
    """
    if target_groups == ["all_admins"] and current_user.get("admin_role") != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Only Super Admins can broadcast to all admins"}
        )
    
    broadcast_count = 0
    
    for group in target_groups:
        if group in manager.groups:
            await manager.broadcast_to_group(group, {
                "type": message_type,
                "title": title,
                "content": content,
                "broadcast_by": current_user.get("username"),
                "timestamp": datetime.now().isoformat()
            })
            broadcast_count += len(manager.groups[group])
    
    return {
        "success": True,
        "message": "Broadcast sent successfully",
        "target_groups": target_groups,
        "estimated_recipients": broadcast_count
    }

# =============================================================================
# Event Simulation (for demonstration)
# =============================================================================

async def simulate_metric_updates():
    """Simulate periodic metric updates (for demonstration)"""
    while True:
        await asyncio.sleep(30)  # Update every 30 seconds
        
        # Update some metrics with small random changes
        for metric in live_metrics.values():
            change = (hash(metric.metric_name) % 20 - 10) / 100  # -0.1 to 0.1
            metric.current_value = max(0, metric.current_value * (1 + change))
            metric.change_percent = change * 100
            
            if change > 0.05:
                metric.trend = "up"
            elif change < -0.05:
                metric.trend = "down"
            else:
                metric.trend = "stable"
            
            metric.timestamp = datetime.now()
        
        # Broadcast update to dashboard connections
        await manager.broadcast_to_group("all_admins", {
            "type": "metrics_update",
            "metrics": get_live_metrics_data(),
            "timestamp": datetime.now().isoformat()
        })

# Start background task for metric simulation
try:
    asyncio.create_task(simulate_metric_updates())
except Exception:
    pass  # Task already running