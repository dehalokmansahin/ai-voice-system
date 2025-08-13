"""
Voice AI Core - Base Processor Classes
Extracted and simplified from Pipecat
"""

from enum import Enum
from abc import ABC, abstractmethod
from typing import AsyncIterator
from ..frames import Frame


class FrameDirection(Enum):
    """Direction for frame processing"""
    DOWNSTREAM = "downstream"
    UPSTREAM = "upstream"


class FrameProcessor(ABC):
    """Base frame processor class"""
    
    def __init__(self):
        self._frame_queue = []
    
    @abstractmethod
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process a frame in the given direction"""
        pass
    
    async def push_frame(self, frame: Frame, direction: FrameDirection = FrameDirection.DOWNSTREAM):
        """Push a frame downstream or upstream"""
        # Simple implementation - in real Pipecat this would handle pipeline routing
        await self.process_frame(frame, direction)
    
    async def start(self):
        """Start the processor"""
        pass
    
    async def stop(self):
        """Stop the processor"""
        pass