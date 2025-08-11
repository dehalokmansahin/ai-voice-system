"""
Pipeline orchestration - Manages frame processors
Extracted and simplified from Pipecat
"""

from dataclasses import dataclass
from typing import List, Optional
import asyncio
from .processor import FrameProcessor
from ..frames.base import Frame, StartFrame, EndFrame


@dataclass
class PipelineParams:
    """Pipeline configuration parameters"""
    allow_interruptions: bool = True
    enable_metrics: bool = False
    enable_vad: bool = True


class Pipeline:
    """
    Pipeline manages a chain of frame processors
    Simplified version focused on OpenSIPS transport needs
    """
    
    def __init__(self, processors: List[FrameProcessor], params: Optional[PipelineParams] = None):
        self.processors = processors
        self.params = params or PipelineParams()
        self._running = False
        self._source: Optional[FrameProcessor] = None
        self._sink: Optional[FrameProcessor] = None
        
        # Link processors together
        if processors:
            for i in range(len(processors) - 1):
                processors[i].link(processors[i + 1])
            self._source = processors[0]
            self._sink = processors[-1]
    
    async def push_frame(self, frame: Frame):
        """Push a frame into the pipeline"""
        if self._source and self._running:
            await self._source.push_frame(frame)
    
    async def start(self):
        """Start the pipeline"""
        self._running = True
        
        # Start all processors
        for processor in self.processors:
            await processor.start()
        
        # Send start frame
        await self.push_frame(StartFrame())
    
    async def stop(self):
        """Stop the pipeline"""
        # Send end frame
        await self.push_frame(EndFrame())
        
        self._running = False
        
        # Stop all processors
        for processor in self.processors:
            await processor.stop()