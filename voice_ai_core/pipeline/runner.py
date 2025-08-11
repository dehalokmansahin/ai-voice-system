"""
Pipeline runner - Manages pipeline execution
Extracted and simplified from Pipecat
"""

import asyncio
from typing import Optional
from .pipeline import Pipeline
from .task import PipelineTask


class PipelineRunner:
    """
    Runs a pipeline task
    Simplified version for OpenSIPS transport
    """
    
    def __init__(self):
        self._task: Optional[PipelineTask] = None
        self._running = False
    
    async def run(self, task: PipelineTask):
        """Run a pipeline task"""
        self._task = task
        self._running = True
        
        try:
            # Start the pipeline
            await task.pipeline.start()
            
            # Run the task
            await task.run()
            
        finally:
            # Always stop the pipeline
            await task.pipeline.stop()
            self._running = False
    
    async def stop(self):
        """Stop the runner"""
        self._running = False
        if self._task:
            await self._task.cancel()