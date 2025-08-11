"""
Unit tests for pipeline components
"""

import pytest
import asyncio
from typing import AsyncIterator
from voice_ai_core.frames import Frame, TextFrame, StartFrame, EndFrame
from voice_ai_core.pipeline import (
    FrameProcessor, FrameDirection,
    Pipeline, PipelineParams,
    PipelineRunner, PipelineTask
)


class MockProcessor(FrameProcessor):
    """Mock processor for testing"""
    
    def __init__(self, name="MockProcessor"):
        super().__init__(name)
        self.processed_frames = []
    
    async def process_frame(self, frame: Frame, direction: FrameDirection) -> AsyncIterator[Frame]:
        """Store and pass through frames"""
        self.processed_frames.append(frame)
        yield frame


class TransformProcessor(FrameProcessor):
    """Processor that transforms text frames"""
    
    async def process_frame(self, frame: Frame, direction: FrameDirection) -> AsyncIterator[Frame]:
        """Transform text frames to uppercase"""
        if isinstance(frame, TextFrame):
            yield TextFrame(text=frame.text.upper())
        else:
            yield frame


class TestFrameProcessor:
    """Test frame processor functionality"""
    
    @pytest.mark.asyncio
    async def test_processor_creation(self):
        """Test processor creation"""
        processor = MockProcessor("TestProcessor")
        assert processor.name == "TestProcessor"
        assert processor._downstream is None
        assert processor._upstream is None
    
    @pytest.mark.asyncio
    async def test_processor_linking(self):
        """Test linking processors"""
        proc1 = MockProcessor("Proc1")
        proc2 = MockProcessor("Proc2")
        proc3 = MockProcessor("Proc3")
        
        proc1.link(proc2).link(proc3)
        
        assert proc1._downstream == proc2
        assert proc2._upstream == proc1
        assert proc2._downstream == proc3
        assert proc3._upstream == proc2
    
    @pytest.mark.asyncio
    async def test_frame_propagation(self):
        """Test frame propagation through processors"""
        proc1 = MockProcessor("Proc1")
        proc2 = MockProcessor("Proc2")
        proc1.link(proc2)
        
        frame = TextFrame(text="test")
        await proc1.push_frame(frame)
        
        assert len(proc1.processed_frames) == 1
        assert len(proc2.processed_frames) == 1
        assert proc1.processed_frames[0] == frame
        assert proc2.processed_frames[0] == frame
    
    @pytest.mark.asyncio
    async def test_frame_transformation(self):
        """Test frame transformation in pipeline"""
        proc1 = TransformProcessor()
        proc2 = MockProcessor()
        proc1.link(proc2)
        
        frame = TextFrame(text="hello")
        await proc1.push_frame(frame)
        
        assert len(proc2.processed_frames) == 1
        transformed = proc2.processed_frames[0]
        assert isinstance(transformed, TextFrame)
        assert transformed.text == "HELLO"


class TestPipeline:
    """Test pipeline functionality"""
    
    @pytest.mark.asyncio
    async def test_pipeline_creation(self):
        """Test pipeline creation with processors"""
        proc1 = MockProcessor("Proc1")
        proc2 = MockProcessor("Proc2")
        proc3 = MockProcessor("Proc3")
        
        pipeline = Pipeline([proc1, proc2, proc3])
        
        assert len(pipeline.processors) == 3
        assert pipeline._source == proc1
        assert pipeline._sink == proc3
        assert proc1._downstream == proc2
        assert proc2._downstream == proc3
    
    @pytest.mark.asyncio
    async def test_pipeline_params(self):
        """Test pipeline with custom params"""
        params = PipelineParams(
            allow_interruptions=False,
            enable_metrics=True,
            enable_vad=False
        )
        pipeline = Pipeline([], params)
        
        assert pipeline.params.allow_interruptions is False
        assert pipeline.params.enable_metrics is True
        assert pipeline.params.enable_vad is False
    
    @pytest.mark.asyncio
    async def test_pipeline_start_stop(self):
        """Test pipeline start/stop lifecycle"""
        proc = MockProcessor()
        pipeline = Pipeline([proc])
        
        await pipeline.start()
        assert pipeline._running is True
        assert len(proc.processed_frames) == 1  # StartFrame
        assert isinstance(proc.processed_frames[0], StartFrame)
        
        await pipeline.stop()
        assert pipeline._running is False
        assert len(proc.processed_frames) == 2  # StartFrame, EndFrame
        assert isinstance(proc.processed_frames[1], EndFrame)
    
    @pytest.mark.asyncio
    async def test_pipeline_push_frame(self):
        """Test pushing frames through pipeline"""
        proc = MockProcessor()
        pipeline = Pipeline([proc])
        
        await pipeline.start()
        frame = TextFrame(text="test")
        await pipeline.push_frame(frame)
        
        assert len(proc.processed_frames) == 2  # StartFrame, TextFrame
        assert proc.processed_frames[1] == frame


class TestPipelineTask:
    """Test pipeline task functionality"""
    
    @pytest.mark.asyncio
    async def test_task_creation(self):
        """Test task creation"""
        pipeline = Pipeline([])
        task = PipelineTask(pipeline, "TestTask")
        
        assert task.pipeline == pipeline
        assert task.name == "TestTask"
        assert task._running is False
    
    @pytest.mark.asyncio
    async def test_task_run_cancel(self):
        """Test task run and cancel"""
        pipeline = Pipeline([MockProcessor()])
        task = PipelineTask(pipeline)
        
        # Start task in background
        run_task = asyncio.create_task(task.run())
        await asyncio.sleep(0.01)  # Let it start
        
        assert task._running is True
        
        # Cancel the task
        await task.cancel()
        assert task._running is False
        
        # Clean up
        try:
            await run_task
        except asyncio.CancelledError:
            pass


class TestPipelineRunner:
    """Test pipeline runner functionality"""
    
    @pytest.mark.asyncio
    async def test_runner_creation(self):
        """Test runner creation"""
        runner = PipelineRunner()
        assert runner._task is None
        assert runner._running is False
    
    @pytest.mark.asyncio
    async def test_runner_run(self):
        """Test running a pipeline task"""
        proc = MockProcessor()
        pipeline = Pipeline([proc])
        task = PipelineTask(pipeline)
        runner = PipelineRunner()
        
        # Run task with timeout
        run_task = asyncio.create_task(runner.run(task))
        await asyncio.sleep(0.01)
        
        assert runner._running is True
        assert runner._task == task
        assert pipeline._running is True
        
        # Stop runner
        await runner.stop()
        assert runner._running is False
        
        # Clean up
        try:
            await run_task
        except asyncio.CancelledError:
            pass