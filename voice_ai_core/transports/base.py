"""
Base transport interfaces - Core transport abstractions
Extracted and simplified from Pipecat
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, AsyncIterator
from ..frames.base import Frame
from ..pipeline.processor import FrameProcessor


@dataclass
class TransportParams:
    """Base transport configuration"""
    audio_in_enabled: bool = True
    audio_out_enabled: bool = True
    vad_enabled: bool = True
    vad_analyzer: Optional[object] = None  # VAD analyzer instance
    sample_rate: int = 16000
    channels: int = 1


class BaseTransport(FrameProcessor):
    """Base class for all transports"""
    
    def __init__(self, params: TransportParams):
        super().__init__()
        self.params = params
        self._running = False
    
    @abstractmethod
    async def start(self):
        """Start the transport"""
        self._running = True
    
    @abstractmethod 
    async def stop(self):
        """Stop the transport"""
        self._running = False


class BaseInputTransport(BaseTransport):
    """Base class for input transports (receives data)"""
    
    @abstractmethod
    async def read_frames(self) -> AsyncIterator[Frame]:
        """Read frames from the transport"""
        pass
    
    async def run_input(self):
        """Main input loop"""
        async for frame in self.read_frames():
            if self._running:
                await self.push_frame(frame)


class BaseOutputTransport(BaseTransport):
    """Base class for output transports (sends data)"""
    
    @abstractmethod
    async def write_frame(self, frame: Frame):
        """Write a frame to the transport"""
        pass
    
    async def process_frame(self, frame: Frame, direction) -> AsyncIterator[Frame]:
        """Process and write output frames"""
        await self.write_frame(frame)
        yield frame  # Pass through for downstream processors