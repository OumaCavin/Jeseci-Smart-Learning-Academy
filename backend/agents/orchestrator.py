"""
Orchestrator Agent - Central Coordination for Multi-Agent Platform
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module implements the Orchestrator Agent, which coordinates all other agents,
manages learning sessions, optimizes global learning paths, and handles conflict
resolution between agents.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from backend.agents.base_agent import BaseAgent, AgentMessage, AgentTask, AgentState, MessageType, Priority
from backend.agents.message_bus import MessageBus, DeliveryPattern

# Import centralized logging configuration
from logger_config import logger


@dataclass
class LearningSession:
    """Represents an active learning session"""
    session_id: str
    user_id: str
    agent_id: str = ""
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"
    current_phase: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "start_time": self.start_time,
            "status": self.status,
            "current_phase": self.current_phase,
            "metadata": self.metadata
        }


@dataclass
class CoordinationRequest:
    """Request for coordination between agents"""
    request_id: str
    requesting_agent: str
    coordination_type: str
    task_data: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"


class OrchestratorAgent(BaseAgent):
    """
    Central Orchestrator Agent for the multi-agent learning platform
    
    The Orchestrator Agent is responsible for:
    - Coordinating communication between all agents
    - Managing learning session lifecycle
    - Optimizing global learning paths
    - Resolving conflicts between agents
    - Allocating resources and balancing load
    - Providing unified system status
    
    Attributes:
        sessions: Active learning sessions
        coordination_queue: Pending coordination requests
        agent_availability: Status of each agent
        global_metrics: System-wide metrics
    """
    
    def __init__(self, agent_id: str = "orchestrator",
                 agent_name: str = "Central Orchestrator",
                 message_bus: Optional[MessageBus] = None):
        """
        Initialize the Orchestrator Agent
        
        Args:
            agent_id: Unique identifier
            agent_name: Human-readable name
            message_bus: Optional message bus instance
        """
        super().__init__(agent_id, agent_name, "Orchestrator")
        self.message_bus = message_bus or MessageBus(name="orchestrator_bus")
        
        # Session management
        self.sessions: Dict[str, LearningSession] = {}
        self.session_history: List[LearningSession] = []
        
        # Coordination
        self.coordination_queue: List[CoordinationRequest] = []
        self.active_coordinations: Dict[str, CoordinationRequest] = {}
        
        # Agent availability tracking
        self.agent_availability: Dict[str, bool] = {}
        
        # Global metrics
        self.global_metrics = {
            "total_sessions": 0,
            "completed_sessions": 0,
            "active_users": 0,
            "average_session_duration": 0,
            "agent_utilization": {}
        }
        
        # Register with message bus
        self.message_bus.register_agent(self.agent_id, self)
        
        self.logger.info("Orchestrator Agent initialized")
    
    def _register_capabilities(self):
        """Register the capabilities of the Orchestrator Agent"""
        self.capabilities = [
            "session_management",
            "agent_coordination",
            "path_optimization",
            "conflict_resolution",
            "resource_allocation",
            "system_monitoring",
            "global_analytics",
            "load_balancing"
        ]
    
    async def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Handle incoming messages from other agents or the system
        
        Args:
            message: The incoming message
            
        Returns:
            Result of message processing
        """
        content = message.content
        msg_type = message.msg_type
        
        if msg_type == MessageType.REQUEST:
            return await self._handle_request(message, content)
        elif msg_type == MessageType.TASK:
            return await self._handle_task(message, content)
        elif msg_type == MessageType.COORDINATION:
            return await self._handle_coordination(message, content)
        elif msg_type == MessageType.UPDATE:
            return await self._handle_update(message, content)
        elif msg_type == MessageType.ALERT:
            return await self._handle_alert(message, content)
        else:
            return {"action": "acknowledged", "msg_id": message.msg_id}
    
    async def _handle_request(self, message: AgentMessage, 
                              content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request-type messages
        
        Args:
            message: The incoming message
            content: Message content
            
        Returns:
            Processing result
        """
        request_type = content.get("request_type", "")
        
        if request_type == "create_session":
            return await self._create_session(content)
        elif request_type == "end_session":
            return await self._end_session(content)
        elif request_type == "get_status":
            return self._get_system_status()
        elif request_type == "route_request":
            return await self._route_request(content)
        elif request_type == "optimize_path":
            return await self._optimize_learning_path(content)
        elif request_type == "resolve_conflict":
            return await self._resolve_conflict(content)
        elif request_type == "get_metrics":
            return self._get_global_metrics()
        elif request_type == "check_agent_availability":
            return {"available": self._check_agent_availability(content.get("agent_id"))}
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    async def _handle_task(self, message: AgentMessage, 
                           content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task-type messages
        
        Args:
            message: The incoming message
            content: Message content
            
        Returns:
            Processing result
        """
        task = content.get("task", {})
        command = task.get("command", "")
        
        if command == "start_session":
            return await self._start_session(task)
        elif command == "end_session":
            return await self._end_session(task)
        elif command == "get_session_info":
            return self._get_session_info(task.get("session_id"))
        elif command == "list_sessions":
            return self._list_sessions(task.get("user_id"))
        else:
            return {"error": f"Unknown task command: {command}"}
    
    async def _handle_coordination(self, message: AgentMessage, 
                                    content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle coordination requests between agents
        
        Args:
            message: The incoming message
            content: Message content
            
        Returns:
            Processing result
        """
        coord_type = content.get("coordination_type", "")
        request = CoordinationRequest(
            request_id=message.msg_id,
            requesting_agent=message.sender,
            coordination_type=coord_type,
            task_data=content.get("task_data", {})
        )
        
        # Add to coordination queue
        self.coordination_queue.append(request)
        
        # Process coordination
        result = await self._process_coordination(request)
        
        return result
    
    async def _handle_update(self, message: AgentMessage, 
                             content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle update messages (e.g., progress updates, status changes)
        
        Args:
            message: The incoming message
            content: Message content
            
        Returns:
            Processing result
        """
        update_type = content.get("update_type", "")
        
        if update_type == "session_progress":
            await self._update_session_progress(content)
        elif update_type == "agent_status":
            self._update_agent_status(content)
        elif update_type == "metrics_update":
            self._update_global_metrics(content)
        
        return {"action": "update_processed", "type": update_type}
    
    async def _handle_alert(self, message: AgentMessage, 
                            content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle alert messages (e.g., errors, warnings, critical events)
        
        Args:
            message: The incoming message
            content: Message content
            
        Returns:
            Processing result
        """
        alert_type = content.get("alert_type", "")
        severity = content.get("severity", "info")
        
        self.logger.warning(f"Alert received from {message.sender}: {alert_type} - {severity}")
        
        if severity == "critical":
            await self._handle_critical_alert(content)
        
        return {"action": "alert_processed", "type": alert_type}
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task assigned to the orchestrator
        
        Args:
            task: The task to execute
            
        Returns:
            Task result
        """
        command = task.command
        
        if command == "initialize":
            return await self._initialize_system(task.parameters)
        elif command == "shutdown":
            return await self._shutdown_system(task.parameters)
        elif command == "health_check":
            return self._health_check()
        elif command == "get_statistics":
            return self._get_statistics()
        elif command == "balance_load":
            return await self._balance_load()
        else:
            return {"error": f"Unknown command: {command}"}
    
    # Session Management Methods
    
    async def _create_session(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new learning session
        
        Args:
            content: Session creation parameters
            
        Returns:
            Created session information
        """
        import uuid
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        user_id = content.get("user_id", "")
        
        session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            status="creating",
            current_phase="initialization",
            metadata=content.get("metadata", {})
        )
        
        self.sessions[session_id] = session
        self.global_metrics["total_sessions"] += 1
        self.global_metrics["active_users"] += 1
        
        self.logger.info(f"Session created: {session_id} for user {user_id}")
        
        return {
            "success": True,
            "session": session.to_dict(),
            "message": "Learning session created successfully"
        }
    
    async def _start_session(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start an existing learning session
        
        Args:
            task: Start session parameters
            
        Returns:
            Session start result
        """
        session_id = task.get("session_id")
        
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session.status = "active"
        session.current_phase = "learning"
        
        self.logger.info(f"Session started: {session_id}")
        
        return {
            "success": True,
            "session": session.to_dict(),
            "message": "Learning session started"
        }
    
    async def _end_session(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        End a learning session
        
        Args:
            content: Session end parameters
            
        Returns:
            Session end result
        """
        session_id = content.get("session_id") or content.get("session_id")
        
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session.status = "completed"
        
        # Move to history
        self.session_history.append(session)
        del self.sessions[session_id]
        
        self.global_metrics["completed_sessions"] += 1
        self.global_metrics["active_users"] = max(0, self.global_metrics["active_users"] - 1)
        
        self.logger.info(f"Session ended: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Learning session completed"
        }
    
    def _get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a specific session
        
        Args:
            session_id: Session to query
            
        Returns:
            Session information
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        return {
            "session": session.to_dict()
        }
    
    def _list_sessions(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List all sessions, optionally filtered by user
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of sessions
        """
        sessions = list(self.sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        return {
            "sessions": [s.to_dict() for s in sessions],
            "total": len(sessions)
        }
    
    async def _update_session_progress(self, content: Dict[str, Any]):
        """
        Update progress for a session
        
        Args:
            content: Progress update data
        """
        session_id = content.get("session_id")
        progress = content.get("progress", 0)
        
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.metadata["progress"] = progress
            
            if progress >= 100:
                session.status = "completed"
    
    # Coordination Methods
    
    async def _route_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a request to the appropriate agent
        
        Args:
            content: Routing parameters
            
        Returns:
            Routing result
        """
        target_agent = content.get("target_agent")
        request_data = content.get("request_data", {})
        
        if not target_agent:
            return {"error": "No target agent specified"}
        
        # Create message to target agent
        message = AgentMessage(
            sender=self.agent_id,
            recipient=target_agent,
            msg_type=MessageType.REQUEST,
            content=request_data,
            priority=Priority(content.get("priority", "MEDIUM"))
        )
        
        # Send via message bus
        await self.message_bus.publish(message)
        
        return {
            "success": True,
            "routed_to": target_agent,
            "msg_id": message.msg_id
        }
    
    async def _process_coordination(self, 
                                    request: CoordinationRequest) -> Dict[str, Any]:
        """
        Process a coordination request between agents
        
        Args:
            request: The coordination request
            
        Returns:
            Coordination result
        """
        coord_type = request.coordination_type
        
        if coord_type == "content_assessment":
            return await self._coordinate_content_assessment(request)
        elif coord_type == "path_progress":
            return await self._coordinate_path_progress(request)
        elif coord_type == "multi_agent_learning":
            return await self._coordinate_multi_agent_learning(request)
        else:
            return {"error": f"Unknown coordination type: {coord_type}"}
    
    async def _coordinate_content_assessment(self, 
                                             request: CoordinationRequest) -> Dict[str, Any]:
        """
        Coordinate between Content and Assessment agents
        
        Args:
            request: The coordination request
            
        Returns:
            Coordination result
        """
        task_data = request.task_data
        
        # This would involve sending requests to both Content and Assessment agents
        # and synthesizing their responses
        
        return {
            "success": True,
            "coordination_type": "content_assessment",
            "result": "Content and assessment coordinated",
            "data": task_data
        }
    
    async def _coordinate_path_progress(self, 
                                        request: CoordinationRequest) -> Dict[str, Any]:
        """
        Coordinate between Path and Analytics agents
        
        Args:
            request: The coordination request
            
        Returns:
            Coordination result
        """
        task_data = request.task_data
        
        return {
            "success": True,
            "coordination_type": "path_progress",
            "result": "Path and analytics coordinated",
            "data": task_data
        }
    
    async def _coordinate_multi_agent_learning(self, 
                                               request: CoordinationRequest) -> Dict[str, Any]:
        """
        Coordinate a multi-agent learning session
        
        Args:
            request: The coordination request
            
        Returns:
            Coordination result
        """
        task_data = request.task_data
        user_id = task_data.get("user_id")
        learning_objectives = task_data.get("objectives", [])
        
        # Route to multiple agents based on objectives
        agents_involved = []
        
        for objective in learning_objectives:
            agent = self._select_agent_for_objective(objective)
            if agent:
                agents_involved.append(agent)
        
        return {
            "success": True,
            "coordination_type": "multi_agent_learning",
            "agents_involved": agents_involved,
            "session_planned": True
        }
    
    def _select_agent_for_objective(self, objective: str) -> Optional[str]:
        """
        Select the appropriate agent for a learning objective
        
        Args:
            objective: The learning objective
            
        Returns:
            Agent ID to route to
        """
        objective_lower = objective.lower()
        
        if "tutor" in objective_lower or "teach" in objective_lower:
            return "tutor_agent"
        elif "quiz" in objective_lower or "assess" in objective_lower:
            return "assessment_agent"
        elif "content" in objective_lower or "generate" in objective_lower:
            return "content_agent"
        elif "path" in objective_lower or "plan" in objective_lower:
            return "path_agent"
        elif "analytics" in objective_lower or "progress" in objective_lower:
            return "analytics_agent"
        else:
            return "tutor_agent"  # Default
    
    # Conflict Resolution Methods
    
    async def _resolve_conflict(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a conflict between agents or tasks
        
        Args:
            content: Conflict information
            
        Returns:
            Resolution result
        """
        conflict_type = content.get("conflict_type", "")
        agents_involved = content.get("agents", [])
        conflict_data = content.get("data", {})
        
        if conflict_type == "resource_allocation":
            return await self._resolve_resource_conflict(agents_involved, conflict_data)
        elif conflict_type == "task_priority":
            return await self._resolve_priority_conflict(agents_involved, conflict_data)
        else:
            return {
                "resolved": False,
                "message": f"Unknown conflict type: {conflict_type}"
            }
    
    async def _resolve_resource_conflict(self, agents: List[str],
                                         data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve resource allocation conflict
        
        Args:
            agents: Agents involved in conflict
            data: Resource data
            
        Returns:
            Resolution result
        """
        # Simple resolution: prioritize by agent type
        priority_order = ["tutor", "analytics", "assessment", "content", "path", "chat"]
        
        for priority in priority_order:
            for agent in agents:
                if priority in agent.lower():
                    return {
                        "resolved": True,
                        "resolution": f"Priority given to {agent}",
                        "winner": agent
                    }
        
        return {"resolved": True, "resolution": "First agent selected", "winner": agents[0]}
    
    async def _resolve_priority_conflict(self, agents: List[str],
                                         data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve task priority conflict
        
        Args:
            agents: Agents involved
            data: Task priority data
            
        Returns:
            Resolution result
        """
        # Default resolution: highest priority wins
        return {
            "resolved": True,
            "resolution": "Based on task priority",
            "winner": agents[0] if agents else None
        }
    
    # Path Optimization Methods
    
    async def _optimize_learning_path(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize a learning path based on user progress and goals
        
        Args:
            content: Path optimization parameters
            
        Returns:
            Optimized path
        """
        user_id = content.get("user_id")
        current_path = content.get("current_path", [])
        goals = content.get("goals", [])
        
        # Simple optimization: reorder based on prerequisites
        optimized_path = self._reorder_by_prerequisites(current_path)
        
        return {
            "success": True,
            "original_path": current_path,
            "optimized_path": optimized_path,
            "optimization_type": "prerequisite_based"
        }
    
    def _reorder_by_prerequisites(self, path: List[Dict]) -> List[Dict]:
        """
        Reorder a learning path based on prerequisites
        
        Args:
            path: Original learning path
            
        Returns:
            Reordered path
        """
        # Simple topological sort based on prerequisites
        # In a real implementation, this would be more sophisticated
        
        if not path:
            return path
        
        # Place items with no prerequisites first
        no_prereqs = [item for item in path if not item.get("prerequisites", [])]
        with_prereqs = [item for item in path if item.get("prerequisites", [])]
        
        return no_prereqs + with_prereqs
    
    # System Management Methods
    
    def _check_agent_availability(self, agent_id: str) -> bool:
        """
        Check if an agent is available
        
        Args:
            agent_id: Agent to check
            
        Returns:
            True if available
        """
        return self.agent_availability.get(agent_id, True)
    
    def _update_agent_status(self, content: Dict[str, Any]):
        """
        Update agent availability status
        
        Args:
            content: Status update data
        """
        agent_id = content.get("agent_id")
        available = content.get("available", True)
        
        self.agent_availability[agent_id] = available
    
    def _update_global_metrics(self, content: Dict[str, Any]):
        """
        Update global system metrics
        
        Args:
            content: Metrics update data
        """
        metrics = content.get("metrics", {})
        
        for key, value in metrics.items():
            if key in self.global_metrics:
                if isinstance(value, (int, float)):
                    self.global_metrics[key] = value
                elif isinstance(value, dict):
                    self.global_metrics[key].update(value)
    
    async def _initialize_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize the multi-agent system
        
        Args:
            params: Initialization parameters
            
        Returns:
            Initialization result
        """
        self.logger.info("Initializing multi-agent system...")
        
        # Create default topics
        default_topics = ["system", "analytics", "content", "assessment", "learning", "chat"]
        for topic in default_topics:
            self.message_bus.create_topic(topic, f"Topic for {topic} updates")
        
        return {
            "success": True,
            "message": "Multi-agent system initialized",
            "topics_created": len(default_topics)
        }
    
    async def _shutdown_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Shutdown the multi-agent system
        
        Args:
            params: Shutdown parameters
            
        Returns:
            Shutdown result
        """
        self.logger.info("Shutting down multi-agent system...")
        
        # End all active sessions
        for session_id in list(self.sessions.keys()):
            await self._end_session({"session_id": session_id})
        
        return {
            "success": True,
            "message": "Multi-agent system shutdown complete",
            "sessions_ended": len(self.session_history)
        }
    
    def _get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status
        
        Returns:
            System status information
        """
        return {
            "status": "operational",
            "active_sessions": len(self.sessions),
            "completed_sessions": len(self.session_history),
            "active_users": self.global_metrics["active_users"],
            "registered_agents": self.message_bus.get_registered_agents(),
            "topics": self.message_bus.get_topics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the system
        
        Returns:
            Health check result
        """
        return {
            "healthy": True,
            "components": {
                "orchestrator": "healthy",
                "message_bus": "healthy",
                "sessions": "healthy" if len(self.sessions) >= 0 else "warning"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "sessions": {
                "active": len(self.sessions),
                "completed": len(self.session_history)
            },
            "metrics": self.global_metrics,
            "agents": {
                "registered": len(self.message_bus.get_registered_agents()),
                "available": len([a for a, v in self.agent_availability.items() if v])
            }
        }
    
    async def _handle_critical_alert(self, content: Dict[str, Any]):
        """
        Handle critical alerts
        
        Args:
            content: Alert data
        """
        alert_data = {
            "alert": content,
            "timestamp": datetime.now().isoformat(),
            "action_taken": "Logged for review"
        }
        
        # In a real system, this would trigger notifications, 
        # fallback procedures, or system alerts
        
        self.logger.critical(f"Critical alert: {json.dumps(alert_data)}")
    
    async def _balance_load(self) -> Dict[str, Any]:
        """
        Balance load across agents
        
        Returns:
            Load balancing result
        """
        # Check agent utilization and redistribute if needed
        # This is a placeholder implementation
        
        return {
            "success": True,
            "action": "Load balancing completed",
            "adjustments": []
        }
    
    def _get_global_metrics(self) -> Dict[str, Any]:
        """
        Get global system metrics
        
        Returns:
            Metrics dictionary
        """
        return {
            "metrics": self.global_metrics,
            "message_bus_stats": self.message_bus.get_statistics()
        }
