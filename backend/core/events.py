"""
Event system for decoupled agent communication and pipeline coordination.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Callable, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

class EventType(Enum):
    """Types of events in the agent system."""
    # Agent lifecycle events
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    AGENT_PROGRESS = "agent_progress"
    
    # Pipeline events
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_STEP_STARTED = "pipeline_step_started"
    PIPELINE_STEP_COMPLETED = "pipeline_step_completed"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    
    # Data flow events
    DATA_AVAILABLE = "data_available"
    DATA_PROCESSED = "data_processed"
    DATA_VALIDATION_FAILED = "data_validation_failed"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    SYSTEM_INFO = "system_info"

@dataclass
class AgentEvent:
    """Event data structure for agent system communication."""
    event_type: EventType
    source: str  # Agent name or system component
    timestamp: float = field(default_factory=time.time)
    data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None  # For tracking related events
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata or {},
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentEvent':
        """Create event from dictionary."""
        return cls(
            event_type=EventType(data["event_type"]),
            source=data["source"],
            timestamp=data.get("timestamp", time.time()),
            data=data.get("data"),
            metadata=data.get("metadata"),
            correlation_id=data.get("correlation_id")
        )

class EventFilter:
    """Filter for event subscriptions."""
    
    def __init__(self, 
                 event_types: Optional[List[EventType]] = None,
                 sources: Optional[List[str]] = None,
                 correlation_id: Optional[str] = None):
        self.event_types = event_types or []
        self.sources = sources or []
        self.correlation_id = correlation_id
    
    def matches(self, event: AgentEvent) -> bool:
        """Check if event matches this filter."""
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        if self.sources and event.source not in self.sources:
            return False
        
        if self.correlation_id and event.correlation_id != self.correlation_id:
            return False
        
        return True

class EventBus:
    """Central event bus for agent system communication."""
    
    def __init__(self, max_history: int = 1000):
        self.logger = logging.getLogger(__name__)
        self._subscribers: Dict[str, List[Callable]] = {}
        self._filtered_subscribers: List[tuple[EventFilter, Callable]] = []
        self._event_history: List[AgentEvent] = []
        self._max_history = max_history
        self._event_count = 0
        self._lock = asyncio.Lock()
    
    def subscribe(self, 
                  event_type: EventType, 
                  callback: Callable[[AgentEvent], Union[None, Any]],
                  subscriber_id: Optional[str] = None) -> str:
        """
        Subscribe to specific event type.
        Returns subscription ID for unsubscribing.
        """
        event_key = event_type.value
        if event_key not in self._subscribers:
            self._subscribers[event_key] = []
        
        self._subscribers[event_key].append(callback)
        
        sub_id = subscriber_id or f"sub_{len(self._subscribers[event_key])}"
        self.logger.debug(f"Subscribed {sub_id} to {event_type.value}")
        return sub_id
    
    def subscribe_filtered(self, 
                          event_filter: EventFilter,
                          callback: Callable[[AgentEvent], Union[None, Any]]) -> str:
        """
        Subscribe with custom filter.
        Returns subscription ID for unsubscribing.
        """
        self._filtered_subscribers.append((event_filter, callback))
        sub_id = f"filtered_sub_{len(self._filtered_subscribers)}"
        self.logger.debug(f"Added filtered subscription {sub_id}")
        return sub_id
    
    def subscribe_multiple(self,
                          event_types: List[EventType],
                          callback: Callable[[AgentEvent], Union[None, Any]]) -> List[str]:
        """Subscribe to multiple event types with same callback."""
        subscription_ids = []
        for event_type in event_types:
            sub_id = self.subscribe(event_type, callback)
            subscription_ids.append(sub_id)
        return subscription_ids
    
    async def publish(self, event: AgentEvent) -> int:
        """
        Publish an event to all subscribers.
        Returns the number of subscribers notified.
        """
        async with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            self._event_count += 1
            
            # Log the event
            self.logger.debug(f"Publishing event: {event.event_type.value} from {event.source}")
            
            notified_count = 0
            
            # Notify direct subscribers
            event_key = event.event_type.value
            if event_key in self._subscribers:
                tasks = []
                for callback in self._subscribers[event_key]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            tasks.append(callback(event))
                        else:
                            # Run sync callbacks in thread pool
                            tasks.append(asyncio.get_event_loop().run_in_executor(
                                None, callback, event
                            ))
                        notified_count += 1
                    except Exception as e:
                        self.logger.error(f"Error preparing callback: {str(e)}")
                
                # Execute all callbacks
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            self.logger.error(f"Callback {i} failed: {str(result)}")
            
            # Notify filtered subscribers
            for event_filter, callback in self._filtered_subscribers:
                if event_filter.matches(event):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            await asyncio.get_event_loop().run_in_executor(
                                None, callback, event
                            )
                        notified_count += 1
                    except Exception as e:
                        self.logger.error(f"Filtered callback failed: {str(e)}")
            
            return notified_count
    
    def publish_sync(self, event: AgentEvent) -> int:
        """Synchronous version of publish for non-async contexts."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.publish(event))
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(self.publish(event))
    
    def get_event_history(self, 
                         event_filter: Optional[EventFilter] = None,
                         limit: Optional[int] = None) -> List[AgentEvent]:
        """
        Get event history, optionally filtered.
        Returns most recent events first.
        """
        events = list(reversed(self._event_history))
        
        if event_filter:
            events = [e for e in events if event_filter.matches(e)]
        
        if limit:
            events = events[:limit]
        
        return events
    
    def get_events_by_correlation_id(self, correlation_id: str) -> List[AgentEvent]:
        """Get all events with a specific correlation ID."""
        return [e for e in self._event_history if e.correlation_id == correlation_id]
    
    def get_events_by_source(self, source: str, limit: Optional[int] = None) -> List[AgentEvent]:
        """Get events from a specific source."""
        events = [e for e in reversed(self._event_history) if e.source == source]
        if limit:
            events = events[:limit]
        return events
    
    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()
        self.logger.info("Cleared event history")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        event_type_counts = {}
        source_counts = {}
        
        for event in self._event_history:
            event_type_counts[event.event_type.value] = event_type_counts.get(event.event_type.value, 0) + 1
            source_counts[event.source] = source_counts.get(event.source, 0) + 1
        
        return {
            "total_events": self._event_count,
            "history_size": len(self._event_history),
            "subscribers": len(self._subscribers),
            "filtered_subscribers": len(self._filtered_subscribers),
            "event_type_counts": event_type_counts,
            "source_counts": source_counts
        }
    
    def create_correlation_id(self) -> str:
        """Create a unique correlation ID for tracking related events."""
        import uuid
        return str(uuid.uuid4())

# Global event bus instance
event_bus = EventBus()

# Convenience functions for common event publishing
async def publish_agent_started(agent_name: str, correlation_id: Optional[str] = None, **metadata):
    """Publish agent started event."""
    event = AgentEvent(
        event_type=EventType.AGENT_STARTED,
        source=agent_name,
        correlation_id=correlation_id,
        metadata=metadata
    )
    return await event_bus.publish(event)

async def publish_agent_completed(agent_name: str, result: Any = None, correlation_id: Optional[str] = None, **metadata):
    """Publish agent completed event."""
    event = AgentEvent(
        event_type=EventType.AGENT_COMPLETED,
        source=agent_name,
        data=result,
        correlation_id=correlation_id,
        metadata=metadata
    )
    return await event_bus.publish(event)

async def publish_agent_failed(agent_name: str, error: str, correlation_id: Optional[str] = None, **metadata):
    """Publish agent failed event."""
    event = AgentEvent(
        event_type=EventType.AGENT_FAILED,
        source=agent_name,
        data={"error": error},
        correlation_id=correlation_id,
        metadata=metadata
    )
    return await event_bus.publish(event)

async def publish_pipeline_step_completed(step_name: str, result: Any = None, correlation_id: Optional[str] = None, **metadata):
    """Publish pipeline step completed event."""
    event = AgentEvent(
        event_type=EventType.PIPELINE_STEP_COMPLETED,
        source=f"pipeline_step_{step_name}",
        data=result,
        correlation_id=correlation_id,
        metadata=metadata
    )
    return await event_bus.publish(event)
