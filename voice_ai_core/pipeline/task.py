"""
Pipeline task - Represents a runnable pipeline task
Extracted and simplified from Pipecat
"""

import asyncio
from typing import Optional, Callable
from .pipeline import Pipeline


class PipelineTask:
    """
    A task that can be run by the pipeline runner
    Simplified for OpenSIPS needs
    """
    
    def __init__(self, pipeline: Pipeline, name: Optional[str] = None):
        self.pipeline = pipeline
        self.name = name or "PipelineTask"
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def run(self):
        """Run the task - override in subclasses for custom behavior"""
        self._running = True
        try:
            # Default: just keep the pipeline running
            while self._running:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
    
    async def cancel(self):
        """Cancel the task"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass