"""
Voice AI Core - Log Observers
Extracted and simplified from Pipecat
"""

import time
import structlog
from typing import Tuple, Any
from abc import ABC, abstractmethod

from ..frames import Frame, TextFrame, TTSStartedFrame, TTSStoppedFrame

logger = structlog.get_logger()


class BaseObserver(ABC):
    """Base observer class"""
    
    @abstractmethod
    async def on_frame(self, frame: Frame) -> None:
        """Handle frame observation"""
        pass


class DebugLogObserver(BaseObserver):
    """Debug frame observer for logging specific frame types"""
    
    def __init__(self, frame_types: Tuple[Any, ...] = None):
        self._frame_types = frame_types or (Frame,)
    
    async def on_frame(self, frame: Frame) -> None:
        """Log frames of specified types"""
        if isinstance(frame, self._frame_types):
            logger.debug(
                "Debug frame observed",
                frame_type=type(frame).__name__,
                frame_data=getattr(frame, 'text', None) or getattr(frame, '__dict__', {})
            )


class LLMLogObserver(BaseObserver):
    """Observer for LLM-related events"""
    
    async def on_frame(self, frame: Frame) -> None:
        """Log LLM events"""
        if isinstance(frame, TextFrame):
            logger.info(
                "LLM text generated",
                text=frame.text[:100] + ("..." if len(frame.text) > 100 else ""),
                length=len(frame.text)
            )


class TranscriptionLogObserver(BaseObserver):
    """Observer for transcription events"""
    
    async def on_frame(self, frame: Frame) -> None:
        """Log transcription events"""
        if isinstance(frame, TextFrame):
            logger.info(
                "Transcription received",
                text=frame.text,
                length=len(frame.text)
            )


class UserBotLatencyLogObserver(BaseObserver):
    """Observer for tracking user-bot interaction latency"""
    
    def __init__(self):
        self._last_user_speech_time = None
        self._last_bot_speech_time = None
    
    async def on_frame(self, frame: Frame) -> None:
        """Track latency between user and bot speech"""
        current_time = time.time()
        
        if isinstance(frame, TTSStartedFrame):
            self._last_bot_speech_time = current_time
            if self._last_user_speech_time:
                latency = current_time - self._last_user_speech_time
                logger.info(
                    "User-bot latency measured",
                    latency_ms=round(latency * 1000, 2)
                )
        
        # Note: We'd need UserStoppedSpeakingFrame to track user speech end
        # This is simplified for the migration