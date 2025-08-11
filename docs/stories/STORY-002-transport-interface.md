# STORY-002: Create Transport Abstraction Interface

## Story
**As a** developer  
**I want to** create a universal transport interface  
**So that** we can support multiple protocols without code duplication  

## Parent Epic
[EPIC-001: Modular Voice Pipeline Refactoring](../epics/EPIC-001-modular-refactoring.md)

## Priority
P0 - Critical

## Story Points
5

## Technical Details

### Implementation Tasks

#### 1. Define Base Transport Interface (Day 1)
```python
# voice-ai-core/transports/base.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TransportConfig:
    """Base configuration for all transports"""
    bind_ip: str = "0.0.0.0"
    bind_port: int = 0
    codec_preferences: List[str] = field(default_factory=lambda: ["opus", "pcm", "ulaw"])
    buffer_size: int = 160  # 20ms at 8kHz
    
@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    remote_ip: str
    remote_port: int
    codec: str
    metadata: Dict[str, Any]

class BaseTransport(ABC):
    """Universal transport interface for all protocols"""
    
    def __init__(self, config: TransportConfig):
        self.config = config
        self._session: Optional[SessionInfo] = None
        self._running = False
        
    @abstractmethod
    async def start(self) -> None:
        """Start the transport service"""
        pass
        
    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport service"""
        pass
        
    @abstractmethod
    async def accept_session(self) -> SessionInfo:
        """Accept incoming session/call"""
        pass
        
    @abstractmethod
    async def audio_input_stream(self) -> AsyncGenerator[AudioFrame, None]:
        """Stream incoming audio frames"""
        pass
        
    @abstractmethod
    async def send_audio(self, frame: AudioFrame) -> None:
        """Send outgoing audio frame"""
        pass
        
    @abstractmethod
    async def handle_signaling(self, message: Dict[str, Any]) -> None:
        """Process signaling messages"""
        pass
        
    @abstractmethod
    async def end_session(self) -> None:
        """Terminate the current session"""
        pass
        
    # Common utility methods
    async def get_statistics(self) -> Dict[str, Any]:
        """Get transport statistics"""
        return {
            "session_id": self._session.session_id if self._session else None,
            "packets_sent": 0,
            "packets_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0
        }
```

#### 2. Create Transport Factory (Day 1)
```python
# voice-ai-core/transports/factory.py
from typing import Dict, Type
from .base import BaseTransport, TransportConfig

class TransportFactory:
    """Factory for creating transport instances"""
    
    _transports: Dict[str, Type[BaseTransport]] = {}
    
    @classmethod
    def register(cls, name: str, transport_class: Type[BaseTransport]):
        """Register a transport implementation"""
        cls._transports[name] = transport_class
        
    @classmethod
    def create(cls, transport_type: str, config: TransportConfig) -> BaseTransport:
        """Create transport instance"""
        if transport_type not in cls._transports:
            raise ValueError(f"Unknown transport type: {transport_type}")
            
        transport_class = cls._transports[transport_type]
        return transport_class(config)
        
    @classmethod
    def list_available(cls) -> List[str]:
        """List available transport types"""
        return list(cls._transports.keys())
```

#### 3. Define Audio Frame Types (Day 2)
```python
# voice-ai-core/transports/frames.py
from dataclasses import dataclass
from enum import Enum

class AudioCodec(Enum):
    PCM_16 = "pcm16"      # 16-bit PCM
    PCM_8 = "pcm8"        # 8-bit PCM
    ULAW = "ulaw"         # G.711 μ-law
    ALAW = "alaw"         # G.711 A-law
    OPUS = "opus"         # Opus
    G722 = "g722"         # G.722

@dataclass
class AudioFrame:
    """Audio frame with metadata"""
    data: bytes
    codec: AudioCodec
    sample_rate: int
    channels: int
    timestamp: int
    duration_ms: int
    
    @property
    def samples(self) -> int:
        """Calculate number of samples"""
        return len(self.data) // (2 * self.channels)  # Assuming 16-bit
```

#### 4. Create Transport Manager (Day 2)
```python
# voice-ai-core/transports/manager.py
class TransportManager:
    """Manages multiple transport instances"""
    
    def __init__(self):
        self._transports: Dict[str, BaseTransport] = {}
        self._active_sessions: Dict[str, str] = {}  # session_id -> transport_id
        
    async def add_transport(self, transport_id: str, transport: BaseTransport):
        """Add a transport instance"""
        self._transports[transport_id] = transport
        await transport.start()
        
    async def remove_transport(self, transport_id: str):
        """Remove a transport instance"""
        if transport_id in self._transports:
            await self._transports[transport_id].stop()
            del self._transports[transport_id]
            
    async def route_session(self, session_info: SessionInfo) -> str:
        """Route session to appropriate transport"""
        # Implement routing logic
        pass
```

#### 5. Integration Points (Day 3)
```python
# voice-ai-core/pipeline/transport_integration.py
class TransportPipeline:
    """Integrates transports with processing pipeline"""
    
    def __init__(self, transport: BaseTransport, pipeline: Pipeline):
        self.transport = transport
        self.pipeline = pipeline
        
    async def run(self):
        """Main processing loop"""
        session = await self.transport.accept_session()
        
        async for audio_frame in self.transport.audio_input_stream():
            # Process through pipeline
            result = await self.pipeline.process(audio_frame)
            
            if result:
                await self.transport.send_audio(result)
```

### Acceptance Criteria
- [ ] Base transport interface defined
- [ ] Transport factory functional
- [ ] Audio frame types complete
- [ ] Transport manager implemented
- [ ] Integration with pipeline working

### Testing Requirements
1. **Unit Tests**
   - Transport interface contracts
   - Factory registration and creation
   - Frame serialization

2. **Integration Tests**
   - Mock transport implementation
   - Pipeline integration
   - Session management

### Definition of Done
- [ ] Interface fully documented
- [ ] Unit tests >90% coverage
- [ ] Integration tests passing
- [ ] Code review completed
- [ ] Merged to development branch

---
*Story Created: 2025-01-10*  
*Status: Not Started*  
*Assignee: Unassigned*