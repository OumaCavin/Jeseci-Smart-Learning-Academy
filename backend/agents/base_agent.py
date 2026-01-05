"""
Base Agent Framework - Core Foundation for Multi-Agent Platform
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module provides the foundational classes and interfaces for all agents
in the multi-agent learning system.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

# Import centralized logging configuration
from logger_config import logger


class AgentState(Enum):
    """Represents the current state of an agent"""
    IDLE = "idle"
    PROCESSING = "processing"
    THINKING = "thinking"
    COMMUNICATING = "communicating"
    LEARNING = "learning"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


class MessageType(Enum):
    """Types of messages agents can exchange"""
    REQUEST = "request"
    RESPONSE = "response"
    QUERY = "query"
    UPDATE = "update"
    ALERT = "alert"
    COORDINATION = "coordination"
    FEEDBACK = "feedback"
    TASK = "task"
    RESULT = "result"


class Priority(Enum):
    """Message and task priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class AgentMessage:
    """
    Standardized message format for inter-agent communication
    
    Attributes:
        msg_id: Unique identifier for the message
        sender: Agent ID or name of the sending agent
        recipient: Agent ID or name of the receiving agent
        msg_type: Type of message (request, response, query, etc.)
        priority: Message priority level
        content: Message payload (dictionary for flexibility)
        timestamp: When the message was created
        correlation_id: ID for tracking related messages
        metadata: Additional metadata for the message
    """
    priority: Priority = Priority.MEDIUM
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sender: str
    recipient: str
    msg_type: MessageType
    content: Dict[str, Any]
    
    def to_json(self) -> str:
        """Serialize message to JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Deserialize message from JSON string"""
        data = json.loads(json_str)
        data['msg_type'] = MessageType(data['msg_type'])
        data['priority'] = Priority(data['priority'])
        return cls(**data)
    
    def create_response(self, content: Dict[str, Any], 
                        success: bool = True) -> 'AgentMessage':
        """Create a response message to this message"""
        return AgentMessage(
            sender=self.recipient,
            recipient=self.sender,
            msg_type=MessageType.RESPONSE,
            content={**content, "success": success},
            priority=self.priority,
            correlation_id=self.correlation_id or self.msg_id,
            metadata={"original_msg_id": self.msg_id}
        )


@dataclass
class AgentTask:
    """
    Represents a task assigned to an agent
    
    Attributes:
        task_id: Unique identifier for the task
        agent_type: Type of agent this task is for
        command: The command/action to perform
        parameters: Parameters for the command
        priority: Task priority level
        created_at: When the task was created
        deadline: Optional deadline for completion
        context: Context information for the task
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str = ""
    command: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    deadline: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize task to JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentTask':
        """Deserialize task from JSON string"""
        data = json.loads(json_str)
        data['priority'] = Priority(data['priority'])
        return cls(**data)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent platform
    
    This class provides the foundational functionality that all agents share:
    - Message handling and processing
    - State management
    - Task execution
    - Communication with other agents
    - Logging and error handling
    
    Attributes:
        agent_id: Unique identifier for this agent
        agent_name: Human-readable name for the agent
        agent_type: Type/category of the agent
        state: Current operational state
        capabilities: List of capabilities this agent supports
        message_queue: Queue for incoming messages
        task_queue: Queue for pending tasks
        logger: Logger instance for this agent
    """
    
    def __init__(self, agent_id: str, agent_name: str, agent_type: str):
        """
        Initialize a new agent instance
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name
            agent_type: Type/category of the agent
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.capabilities: List[str] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logger
        self._running = False
        self._processing_lock = asyncio.Lock()
        
        # Setup logging
        self.logger = logging.getLogger(f"Agent[{agent_id}]")
        
        # Register capabilities (to be overridden by subclasses)
        self._register_capabilities()
        
        self.logger.info(f"Agent {agent_name} ({agent_id}) initialized")
    
    def _register_capabilities(self):
        """Register the capabilities this agent supports"""
        self.capabilities = [
            "message_handling",
            "task_processing",
            "state_management"
        ]
    
    @property
    def is_running(self) -> bool:
        """Check if the agent is currently running"""
        return self._running
    
    @property
    def is_idle(self) -> bool:
        """Check if the agent is idle and ready for new tasks"""
        return self.state == AgentState.IDLE and not self._processing_lock.locked()
    
    async def start(self):
        """Start the agent's processing loops"""
        if self._running:
            self.logger.warning(f"Agent {self.agent_name} is already running")
            return
        
        self._running = True
        self.state = AgentState.IDLE
        self.logger.info(f"Agent {self.agent_name} started")
        
        # Start message and task processing loops
        await asyncio.gather(
            self._message_processing_loop(),
            self._task_processing_loop()
        )
    
    async def stop(self):
        """Stop the agent gracefully"""
        self._running = False
        self.state = AgentState.SHUTTING_DOWN
        self.logger.info(f"Agent {self.agent_name} stopping...")
        
        # Clear queues
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
                
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self.state = AgentState.IDLE
        self.logger.info(f"Agent {self.agent_name} stopped")
    
    async def send_message(self, message: AgentMessage, 
                          message_bus: 'MessageBus') -> bool:
        """
        Send a message to another agent via the message bus
        
        Args:
            message: The message to send
            message_bus: The message bus to use for delivery
            
        Returns:
            True if message was queued successfully
        """
        try:
            await message_bus.publish(message)
            self.logger.debug(f"Message sent to {message.recipient}: {message.msg_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    async def receive_message(self, message: AgentMessage):
        """
        Receive and queue a message from another agent
        
        Args:
            message: The received message
        """
        await self.message_queue.put(message)
        self.logger.debug(f"Message received from {message.sender}: {message.msg_id}")
    
    async def queue_task(self, task: AgentTask):
        """
        Queue a task for processing
        
        Args:
            task: The task to queue
        """
        await self.task_queue.put(task)
        self.logger.debug(f"Task queued: {task.task_id}")
    
    async def _message_processing_loop(self):
        """Background loop for processing incoming messages"""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                async with self._processing_lock:
                    await self._process_message(message)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _task_processing_loop(self):
        """Background loop for processing queued tasks"""
        while self._running:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                async with self._processing_lock:
                    await self._execute_task(task)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_message(self, message: AgentMessage):
        """
        Process an incoming message
        
        This method should be overridden by subclasses to implement
        specific message handling logic
        
        Args:
            message: The message to process
        """
        self.state = AgentState.PROCESSING
        self.logger.info(f"Processing message from {message.sender}")
        
        try:
            # Default handling - echo back acknowledgment
            response = message.create_response(
                content={
                    "received": True,
                    "agent": self.agent_name,
                    "action": "message_acknowledged"
                }
            )
            
            # In subclasses, implement actual message processing
            await self.handle_message(message)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.state = AgentState.ERROR
        finally:
            if self.state != AgentState.ERROR:
                self.state = AgentState.IDLE
    
    async def _execute_task(self, task: AgentTask):
        """
        Execute a queued task
        
        This method should be overridden by subclasses to implement
        specific task execution logic
        
        Args:
            task: The task to execute
        """
        self.state = AgentState.PROCESSING
        self.logger.info(f"Executing task: {task.command}")
        
        try:
            # Default implementation
            result = await self.execute_task(task)
            
            self.logger.info(f"Task completed: {task.task_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            self.state = AgentState.ERROR
        finally:
            if self.state != AgentState.ERROR:
                self.state = AgentState.IDLE
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Handle an incoming message
        
        Subclasses must implement this method to define their
        message handling behavior
        
        Args:
            message: The incoming message
            
        Returns:
            Result of message processing
        """
        pass
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task
        
        Subclasses must implement this method to define their
        task execution behavior
        
        Args:
            task: The task to execute
            
        Returns:
            Result of task execution
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "capabilities": self.capabilities,
            "queue_size": {
                "messages": self.message_queue.qsize(),
                "tasks": self.task_queue.qsize()
            }
        }
    
    def __repr__(self) -> str:
        return f"{self.agent_name}({self.agent_id})"
    
    def __str__(self) -> str:
        return f"{self.agent_type} Agent: {self.agent_name}"
