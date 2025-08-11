"""
Frame processor base class - Core of the pipeline processing
Extracted and simplified from Pipecat
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import AsyncIterator, Optional, List
import asyncio
from ..frames.base import Frame, SystemFrame


class FrameDirection(Enum):
    """Direction of frame flow in pipeline"""
    DOWNSTREAM = "downstream"
    UPSTREAM = "upstream"


class FrameProcessor(ABC):
    """Base class for all frame processors in the pipeline"""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self._running = False
        self._downstream: Optional['FrameProcessor'] = None
        self._upstream: Optional['FrameProcessor'] = None
        
    def link(self, processor: 'FrameProcessor') -> 'FrameProcessor':
        """Link this processor to the next one in the pipeline"""
        self._downstream = processor
        processor._upstream = self
        return processor
    
    async def process_frame(self, frame: Frame, direction: FrameDirection = FrameDirection.DOWNSTREAM) -> AsyncIterator[Frame]:
        """
        Process a single frame. Override this in subclasses.
        Can yield zero or more frames.
        """
        # Default implementation: pass through
        yield frame
    
    async def push_frame(self, frame: Frame, direction: FrameDirection = FrameDirection.DOWNSTREAM):
        """Push a frame through the pipeline"""
        async for processed_frame in self.process_frame(frame, direction):
            if direction == FrameDirection.DOWNSTREAM and self._downstream:
                await self._downstream.push_frame(processed_frame, direction)
            elif direction == FrameDirection.UPSTREAM and self._upstream:
                await self._upstream.push_frame(processed_frame, direction)
    
    async def start(self):
        """Start the processor"""
        self._running = True
        
    async def stop(self):
        """Stop the processor"""
        self._running = False