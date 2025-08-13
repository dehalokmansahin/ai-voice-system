"""
Text and speech event frames
Extracted and simplified from Pipecat
"""

from dataclasses import dataclass, field
from typing import Optional
from .base import DataFrame, SystemFrame


@dataclass
class TextFrame(DataFrame):
    """Text data frame"""
    text: str = ""


@dataclass
class TranscriptionFrame(TextFrame):
    """Speech-to-text transcription result"""
    confidence: Optional[float] = None
    is_final: bool = True


@dataclass
class UserStartedSpeakingFrame(SystemFrame):
    """User started speaking event"""
    pass


@dataclass
class UserStoppedSpeakingFrame(SystemFrame):
    """User stopped speaking event"""
    pass


@dataclass
class VADUserStartedSpeakingFrame(SystemFrame):
    """VAD detected user started speaking"""
    pass


@dataclass
class VADUserStoppedSpeakingFrame(SystemFrame):
    """VAD detected user stopped speaking"""
    pass


@dataclass
class InterimTranscriptionFrame(TranscriptionFrame):
    """Interim/partial speech transcription result"""
    is_final: bool = False


@dataclass
class LLMTextFrame(TextFrame):
    """LLM generated text frame"""
    pass


@dataclass
class LLMMessagesFrame(DataFrame):
    """LLM messages frame"""
    messages: list = field(default_factory=list)


@dataclass
class LLMFullResponseStartFrame(SystemFrame):
    """LLM full response started"""
    pass


@dataclass
class LLMFullResponseEndFrame(SystemFrame):
    """LLM full response ended"""
    pass