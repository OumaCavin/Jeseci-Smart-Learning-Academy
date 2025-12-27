"""
Agent Registry - Agent Lifecycle Management
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module provides the agent registry for managing the lifecycle of all agents
in the multi-agent system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field

from backend.agents.base_agent import BaseAgent, AgentState
from backend.agents.message_bus import MessageBus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agent instantiation"""
    agent_id: str
    agent_name: str
    agent_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    auto_start: bool = True
    dependencies: List[str] = field(default_factory=list)


class AgentRegistry:
    """
    Central registry for managing agent lifecycle
    
    The registry handles:
    - Agent registration and unregistration
    - Agent configuration management
    - Agent startup and shutdown
    - Dependency management between agents
    - Health monitoring and status reporting
    
    Attributes:
        name: Name of this registry instance
        agents: Dictionary of registered agents
        configs: Agent configurations
        message_bus: Associated message bus
        logger: Logger instance
    """
    
    def __init__(self, name: str = "agent_registry", 
                 message_bus: Optional[MessageBus] = None):
        """
        Initialize the agent registry
        
        Args:
            name: Name identifier for this registry
            message_bus: Optional message bus instance
        """
        self.name = name
        self.agents: Dict[str, BaseAgent] = {}
        self.configs: Dict[str, AgentConfig] = {}
        self.message_bus = message_bus or MessageBus(name="registry_bus")
        self.logger = logger
        self._running = False
        
        self.logger.info(f"AgentRegistry '{name}' initialized")
    
    def register_config(self, config: AgentConfig) -> bool:
        """
        Register an agent configuration
        
        Args:
            config: AgentConfig to register
            
        Returns:
            True if registration successful
        """
        if config.agent_id in self.configs:
            self.logger.warning(f"Config for {config.agent_id} already registered")
            return False
        
        self.configs[config.agent_id] = config
        self.logger.info(f"Agent config registered: {config.agent_id}")
        return True
    
    def unregister_config(self, agent_id: str) -> bool:
        """
        Unregister an agent configuration
        
        Args:
            agent_id: Agent configuration to remove
            
        Returns:
            True if successful
        """
        if agent_id in self.configs:
            del self.configs[agent_id]
            self.logger.info(f"Agent config unregistered: {agent_id}")
            return True
        return False
    
    def get_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Get agent configuration by ID
        
        Args:
            agent_id: Agent to look up
            
        Returns:
            AgentConfig if found, None otherwise
        """
        return self.configs.get(agent_id)
    
    def list_configs(self) -> List[AgentConfig]:
        """
        List all registered configurations
        
        Returns:
            List of all AgentConfig objects
        """
        return list(self.configs.values())
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent instance
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if registration successful
        """
        if agent.agent_id in self.agents:
            self.logger.warning(f"Agent {agent.agent_id} already registered")
            return False
        
        self.agents[agent.agent_id] = agent
        
        # Register with message bus
        self.message_bus.register_agent(agent.agent_id, agent)
        
        self.logger.info(f"Agent registered: {agent.agent_id}")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent instance
        
        Args:
            agent_id: Agent to unregister
            
        Returns:
            True if successful
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            # Stop the agent if running
            if agent.is_running:
                asyncio.create_task(agent.stop())
            
            # Unregister from message bus
            self.message_bus.unregister_agent(agent_id)
            
            del self.agents[agent_id]
            self.logger.info(f"Agent unregistered: {agent_id}")
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get agent instance by ID
        
        Args:
            agent_id: Agent to look up
            
        Returns:
            Agent instance if found, None otherwise
        """
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent IDs
        
        Returns:
            List of agent IDs
        """
        return list(self.agents.keys())
    
    async def start_agent(self, agent_id: str) -> bool:
        """
        Start an agent by ID
        
        Args:
            agent_id: Agent to start
            
        Returns:
            True if started successfully
        """
        agent = self.agents.get(agent_id)
        
        if not agent:
            self.logger.warning(f"Agent {agent_id} not found")
            return False
        
        if agent.is_running:
            self.logger.warning(f"Agent {agent_id} already running")
            return False
        
        # Check dependencies
        config = self.configs.get(agent_id)
        if config and config.dependencies:
            for dep_id in config.dependencies:
                dep = self.agents.get(dep_id)
                if dep and not dep.is_running:
                    self.logger.info(f"Starting dependency {dep_id} for {agent_id}")
                    await self.start_agent(dep_id)
        
        # Start the agent
        await agent.start()
        self.logger.info(f"Agent started: {agent_id}")
        return True
    
    async def stop_agent(self, agent_id: str) -> bool:
        """
        Stop an agent by ID
        
        Args:
            agent_id: Agent to stop
            
        Returns:
            True if stopped successfully
        """
        agent = self.agents.get(agent_id)
        
        if not agent:
            self.logger.warning(f"Agent {agent_id} not found")
            return False
        
        if not agent.is_running:
            self.logger.warning(f"Agent {agent_id} not running")
            return False
        
        await agent.stop()
        self.logger.info(f"Agent stopped: {agent_id}")
        return True
    
    async def start_all(self) -> int:
        """
        Start all registered agents
        
        Returns:
            Number of agents started
        """
        started = 0
        
        # Start in dependency order
        remaining = set(self.agents.keys())
        
        while remaining:
            progress_made = False
            
            for agent_id in list(remaining):
                config = self.configs.get(agent_id)
                dependencies = config.dependencies if config else []
                
                # Check if all dependencies are running
                deps_ready = all(
                    dep_id not in remaining or 
                    self.agents.get(dep_id, None) is None or
                    self.agents[dep_id].is_running
                    for dep_id in dependencies
                )
                
                if deps_ready:
                    if await self.start_agent(agent_id):
                        started += 1
                        remaining.remove(agent_id)
                        progress_made = True
            
            if not progress_made and remaining:
                # Circular dependency or missing dependency - start anyway
                for agent_id in list(remaining):
                    await self.start_agent(agent_id)
                    started += 1
                    remaining.remove(agent_id)
        
        self._running = True
        self.logger.info(f"All agents started: {started} total")
        return started
    
    async def stop_all(self) -> int:
        """
        Stop all registered agents
        
        Returns:
            Number of agents stopped
        """
        stopped = 0
        
        for agent_id in list(self.agents.keys()):
            if await self.stop_agent(agent_id):
                stopped += 1
        
        self._running = False
        self.logger.info(f"All agents stopped: {stopped} total")
        return stopped
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get registry status including all agent statuses
        
        Returns:
            Dictionary containing registry status
        """
        agent_statuses = {}
        
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()
        
        return {
            "registry_name": self.name,
            "total_agents": len(self.agents),
            "running_agents": sum(1 for a in self.agents.values() if a.is_running),
            "total_configs": len(self.configs),
            "message_bus_status": self.message_bus.get_statistics(),
            "agents": agent_statuses,
            "is_running": self._running
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics
        
        Returns:
            Dictionary containing statistics
        """
        return {
            "total_agents": len(self.agents),
            "running_agents": sum(1 for a in self.agents.values() if a.is_running),
            "total_configs": len(self.configs),
            "enabled_configs": sum(1 for c in self.configs.values() if c.enabled),
            "auto_start_configs": sum(1 for c in self.configs.values() if c.auto_start),
            "message_bus": self.message_bus.get_statistics()
        }
