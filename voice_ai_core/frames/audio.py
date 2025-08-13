"""
Audio frame types - Essential audio processing frames
Extracted and simplified from Pipecat
"""

from dataclasses import dataclass, field
from typing import Optional
from .base import DataFrame, SystemFrame


@dataclass
class AudioFrame(DataFrame):
    """Base audio frame"""
    audio: bytes = field(default=b"")
    sample_rate: int = 16000
    channels: int = 1
    
    @property
    def num_samples(self) -> int:
        """Calculate number of samples (assuming 16-bit audio)"""
        return len(self.audio) // (2 * self.channels)
    
    @property
    def duration(self) -> float:
        """Duration in seconds"""
        return self.num_samples / self.sample_rate


@dataclass
class InputAudioRawFrame(AudioFrame):
    """Raw audio input from user"""
    pass


@dataclass 
class OutputAudioRawFrame(AudioFrame):
    """Raw audio output to user"""
    pass


@dataclass
class TTSStartedFrame(SystemFrame):
    """TTS synthesis started"""
    pass


@dataclass
class TTSStoppedFrame(SystemFrame):
    """TTS synthesis stopped"""
    pass


@dataclass
class TTSAudioRawFrame(AudioFrame):
    """TTS audio output frame"""
    pass


# Compatibility aliases
AudioRawFrame = AudioFrame