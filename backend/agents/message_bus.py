"""
Message Bus - Agent Communication Infrastructure
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module provides the message bus system for inter-agent communication,
enabling agents to exchange messages asynchronously with various delivery patterns.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import uuid

from .base_agent import AgentMessage, MessageType, Priority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeliveryPattern(Enum):
    """Message delivery patterns supported by the message bus"""
    DIRECT = "direct"              # Direct agent-to-agent
    PUBLISH_SUBSCRIBE = "pub_sub"  # Publish to topic, subscribers receive
    BROADCAST = "broadcast"        # Send to all agents
    REQUEST_REPLY = "request_reply" # Request-response pattern
    FAN_OUT = "fan_out"            # Send to multiple specific agents


@dataclass
class Topic:
    """Represents a message topic for pub/sub communication"""
    name: str
    description: str = ""
    subscribers: Set[str] = field(default_factory=set)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def subscribe(self, agent_id: str):
        """Subscribe an agent to this topic"""
        self.subscribers.add(agent_id)
        
    def unsubscribe(self, agent_id: str):
        """Unsubscribe an agent from this topic"""
        self.subscribers.discard(agent_id)
    
    def get_subscribers(self) -> List[str]:
        """Get list of current subscribers"""
        return list(self.subscribers)


@dataclass
class Subscription:
    """Represents a subscription to the message bus"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    topic: str = ""
    pattern: DeliveryPattern = DeliveryPattern.PUBLISH_SUBSCRIBE
    filters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MessageBus:
    """
    Central message bus for agent communication
    
    The message bus handles routing of messages between agents using various
    delivery patterns. It supports direct messaging, publish/subscribe,
    broadcasting, and request-response patterns.
    
    Attributes:
        name: Name identifier for this message bus instance
        agents: Registered agents indexed by agent_id
        topics: Active topics for pub/sub communication
        subscriptions: Active subscriptions
        message_history: Recent message history for debugging
        max_history: Maximum number of messages to keep in history
        logger: Logger instance
    """
    
    def __init__(self, name: str = "main_bus", max_history: int = 1000):
        """
        Initialize the message bus
        
        Args:
            name: Name identifier for this message bus
            max_history: Maximum number of messages to keep in history
        """
        self.name = name
        self.agents: Dict[str, Any] = {}  # agent_id -> agent reference
        self.topics: Dict[str, Topic] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.message_history: List[AgentMessage] = []
        self.max_history = max_history
        self.logger = logger
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "topics_created": 0,
            "subscriptions_created": 0
        }
        
        # Default topics
        self._create_default_topics()
        
        self.logger.info(f"MessageBus '{name}' initialized")
    
    def _create_default_topics(self):
        """Create default topics for common communication patterns"""
        default_topics = [
            ("system", "System-wide announcements and alerts"),
            ("analytics", "Analytics and progress tracking updates"),
            ("content", "Content generation and curation updates"),
            ("assessment", "Assessment and quiz updates"),
            ("learning", "Learning path and progress updates"),
            ("chat", "Chat and conversation updates")
        ]
        
        for topic_name, description in default_topics:
            self.create_topic(topic_name, description)
    
    def register_agent(self, agent_id: str, agent: Any) -> bool:
        """
        Register an agent with the message bus
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Reference to the agent object
            
        Returns:
            True if registration was successful
        """
        if agent_id in self.agents:
            self.logger.warning(f"Agent {agent_id} already registered")
            return False
        
        self.agents[agent_id] = agent
        self.logger.info(f"Agent registered: {agent_id}")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the message bus
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            True if unregistration was successful
        """
        if agent_id not in self.agents:
            self.logger.warning(f"Agent {agent_id} not registered")
            return False
        
        del self.agents[agent_id]
        
        # Cleanup subscriptions
        for sub_id in list(self.subscriptions.keys()):
            if self.subscriptions[sub_id].agent_id == agent_id:
                del self.subscriptions[sub_id]
        
        # Cleanup topic subscriptions
        for topic in self.topics.values():
            topic.unsubscribe(agent_id)
        
        self.logger.info(f"Agent unregistered: {agent_id}")
        return True
    
    def create_topic(self, topic_name: str, description: str = "") -> Topic:
        """
        Create a new topic for pub/sub communication
        
        Args:
            topic_name: Unique name for the topic
            description: Human-readable description
            
        Returns:
            The created Topic object
        """
        if topic_name in self.topics:
            self.logger.warning(f"Topic {topic_name} already exists")
            return self.topics[topic_name]
        
        topic = Topic(name=topic_name, description=description)
        self.topics[topic_name] = topic
        self.stats["topics_created"] += 1
        self.logger.info(f"Topic created: {topic_name}")
        return topic
    
    def subscribe(self, agent_id: str, topic: str, 
                  pattern: DeliveryPattern = DeliveryPattern.PUBLISH_SUBSCRIBE,
                  filters: Dict[str, Any] = None) -> Optional[str]:
        """
        Subscribe an agent to a topic
        
        Args:
            agent_id: Agent to subscribe
            topic: Topic name to subscribe to
            pattern: Delivery pattern for the subscription
            filters: Optional filters for message selection
            
        Returns:
            Subscription ID if successful, None otherwise
        """
        if agent_id not in self.agents:
            self.logger.warning(f"Agent {agent_id} not registered")
            return None
        
        if topic not in self.topics:
            self.logger.warning(f"Topic {topic} does not exist")
            return None
        
        # Add agent to topic subscribers
        self.topics[topic].subscribe(agent_id)
        
        # Create subscription record
        subscription = Subscription(
            agent_id=agent_id,
            topic=topic,
            pattern=pattern,
            filters=filters or {}
        )
        self.subscriptions[subscription.subscription_id] = subscription
        self.stats["subscriptions_created"] += 1
        
        self.logger.info(f"Agent {agent_id} subscribed to topic {topic}")
        return subscription.subscription_id
    
    def unsubscribe(self, agent_id: str, topic: str) -> bool:
        """
        Unsubscribe an agent from a topic
        
        Args:
            agent_id: Agent to unsubscribe
            topic: Topic name to unsubscribe from
            
        Returns:
            True if successful
        """
        if topic in self.topics:
            self.topics[topic].unsubscribe(agent_id)
        
        # Remove subscription record
        for sub_id, subscription in list(self.subscriptions.items()):
            if subscription.agent_id == agent_id and subscription.topic == topic:
                del self.subscriptions[sub_id]
                self.logger.info(f"Agent {agent_id} unsubscribed from {topic}")
                return True
        
        return False
    
    async def publish(self, message: AgentMessage) -> int:
        """
        Publish a message through the message bus
        
        The message is delivered based on its recipient and the message type
        
        Args:
            message: The message to publish
            
        Returns:
            Number of agents that received the message
        """
        self.message_history.append(message)
        
        # Trim history if needed
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        self.stats["messages_sent"] += 1
        
        delivery_count = 0
        
        try:
            if message.recipient == "*":
                # Broadcast to all agents
                delivery_count = await self._broadcast(message)
            elif message.recipient.startswith("@"):
                # Topic-based delivery
                topic = message.recipient[1:]
                delivery_count = await self._publish_to_topic(message, topic)
            elif message.recipient.startswith("+"):
                # Fan-out to multiple recipients
                recipients = message.recipient[1:].split(",")
                delivery_count = await self._fan_out(message, recipients)
            else:
                # Direct delivery
                delivery_count = await self._direct_delivery(message)
            
            self.stats["messages_received"] += delivery_count
            
        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
        
        return delivery_count
    
    async def _direct_delivery(self, message: AgentMessage) -> int:
        """
        Deliver message directly to specified recipient
        
        Args:
            message: The message to deliver
            
        Returns:
            1 if delivered, 0 otherwise
        """
        recipient = self.agents.get(message.recipient)
        
        if recipient:
            await recipient.receive_message(message)
            return 1
        
        self.logger.warning(f"Direct delivery failed: recipient {message.recipient} not found")
        return 0
    
    async def _broadcast(self, message: AgentMessage) -> int:
        """
        Broadcast message to all registered agents
        
        Args:
            message: The message to broadcast
            
        Returns:
            Number of agents that received the message
        """
        delivery_count = 0
        
        for agent_id, agent in self.agents.items():
            # Skip sender if specified
            if message.sender == agent_id:
                continue
            
            try:
                await agent.receive_message(message)
                delivery_count += 1
            except Exception as e:
                self.logger.error(f"Broadcast delivery failed to {agent_id}: {e}")
        
        return delivery_count
    
    async def _publish_to_topic(self, message: AgentMessage, 
                                 topic_name: str) -> int:
        """
        Publish message to all subscribers of a topic
        
        Args:
            message: The message to publish
            topic_name: The topic to publish to
            
        Returns:
            Number of subscribers that received the message
        """
        topic = self.topics.get(topic_name)
        
        if not topic:
            self.logger.warning(f"Topic {topic_name} not found")
            return 0
        
        delivery_count = 0
        subscribers = topic.get_subscribers()
        
        for agent_id in subscribers:
            # Skip sender if applicable
            if message.sender == agent_id:
                continue
            
            agent = self.agents.get(agent_id)
            if agent:
                try:
                    await agent.receive_message(message)
                    delivery_count += 1
                except Exception as e:
                    self.logger.error(f"Topic delivery failed to {agent_id}: {e}")
        
        return delivery_count
    
    async def _fan_out(self, message: AgentMessage, 
                       recipients: List[str]) -> int:
        """
        Deliver message to multiple specific recipients
        
        Args:
            message: The message to deliver
            recipients: List of recipient agent IDs
            
        Returns:
            Number of successful deliveries
        """
        delivery_count = 0
        
        for recipient_id in recipients:
            recipient_id = recipient_id.strip()
            if not recipient_id:
                continue
                
            agent = self.agents.get(recipient_id)
            if agent:
                try:
                    await agent.receive_message(message)
                    delivery_count += 1
                except Exception as e:
                    self.logger.error(f"Fan-out delivery failed to {recipient_id}: {e}")
        
        return delivery_count
    
    async def request_reply(self, message: AgentMessage, 
                           timeout: float = 5.0) -> Optional[AgentMessage]:
        """
        Send a request and wait for a response
        
        Implements the request-reply pattern with timeout
        
        Args:
            message: The request message
            timeout: Maximum time to wait for response
            
        Returns:
            Response message if received, None otherwise
        """
        response_received = asyncio.Event()
        response_message = None
        
        async def handle_response(resp: AgentMessage):
            nonlocal response_message
            response_message = resp
            response_received.set()
        
        # Store the response handler (in a real implementation, 
        # this would use a correlation ID)
        self._response_handlers = getattr(self, '_response_handlers', {})
        self._response_handlers[message.correlation_id or message.msg_id] = handle_response
        
        # Send the message
        await self.publish(message)
        
        # Wait for response with timeout
        try:
            await asyncio.wait_for(response_received.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"Request timeout: {message.msg_id}")
        
        # Clean up handler
        if message.correlation_id or message.msg_id in self._response_handler:
            del self._response_handlers[message.correlation_id or message.msg_id]
        
        return response_message
    
    def get_topic_subscribers(self, topic_name: str) -> List[str]:
        """
        Get list of subscribers for a topic
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            List of subscriber agent IDs
        """
        topic = self.topics.get(topic_name)
        if topic:
            return topic.get_subscribers()
        return []
    
    def get_registered_agents(self) -> List[str]:
        """
        Get list of all registered agent IDs
        
        Returns:
            List of agent IDs
        """
        return list(self.agents.keys())
    
    def get_topics(self) -> List[str]:
        """
        Get list of all topic names
        
        Returns:
            List of topic names
        """
        return list(self.topics.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get message bus statistics
        
        Returns:
            Dictionary containing statistics
        """
        return {
            "name": self.name,
            "registered_agents": len(self.agents),
            "topics": len(self.topics),
            "subscriptions": len(self.subscriptions),
            "message_history_size": len(self.message_history),
            **self.stats
        }
    
    def get_message_history(self, 
                           agent_id: Optional[str] = None,
                           topic: Optional[str] = None,
                           limit: int = 100) -> List[AgentMessage]:
        """
        Get message history with optional filtering
        
        Args:
            agent_id: Filter by sender or recipient
            topic: Filter by topic (for pub/sub messages)
            limit: Maximum number of messages to return
            
        Returns:
            List of matching messages
        """
        messages = self.message_history
        
        if agent_id:
            messages = [m for m in messages 
                       if m.sender == agent_id or m.recipient == agent_id]
        
        if topic:
            messages = [m for m in messages 
                       if m.metadata.get("topic") == topic]
        
        return messages[-limit:]
