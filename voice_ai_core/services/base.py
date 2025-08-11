"""
Base service interfaces - Defines contracts for AI services
Extracted and simplified from Pipecat
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, List
from ..frames.base import Frame
from ..frames.audio import AudioFrame
from ..frames.text import TextFrame, TranscriptionFrame
from ..pipeline.processor import FrameProcessor


class BaseService(FrameProcessor):
    """Base class for all AI services"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the service"""
        self._initialized = True
    
    async def cleanup(self):
        """Cleanup service resources"""
        self._initialized = False


class STTService(BaseService):
    """Speech-to-Text service interface"""
    
    @abstractmethod
    async def transcribe(self, audio: AudioFrame) -> AsyncIterator[TranscriptionFrame]:
        """Transcribe audio to text"""
        pass
    
    async def process_frame(self, frame: Frame, direction) -> AsyncIterator[Frame]:
        """Process audio frames for transcription"""
        if isinstance(frame, AudioFrame):
            async for transcription in self.transcribe(frame):
                yield transcription
        else:
            yield frame


class TTSService(BaseService):
    """Text-to-Speech service interface"""
    
    @abstractmethod
    async def synthesize(self, text: str) -> AsyncIterator[AudioFrame]:
        """Synthesize text to audio"""
        pass
    
    async def process_frame(self, frame: Frame, direction) -> AsyncIterator[Frame]:
        """Process text frames for synthesis"""
        if isinstance(frame, TextFrame):
            async for audio in self.synthesize(frame.text):
                yield audio
        else:
            yield frame


class LLMService(BaseService):
    """Language Model service interface"""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[List[dict]] = None) -> AsyncIterator[TextFrame]:
        """Generate text from prompt"""
        pass
    
    async def process_frame(self, frame: Frame, direction) -> AsyncIterator[Frame]:
        """Process text frames for generation"""
        if isinstance(frame, TextFrame):
            async for response in self.generate(frame.text):
                yield response
        else:
            yield frame