"""
Voice AI Core - Frame Types
Extracted essential frame types from Pipecat
"""

from .base import (
    Frame,
    SystemFrame,
    DataFrame,
    ErrorFrame,
    StartFrame,
    EndFrame,
    CancelFrame
)

from .audio import (
    AudioFrame,
    AudioRawFrame,
    InputAudioRawFrame,
    OutputAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    TTSAudioRawFrame
)

from .text import (
    TextFrame,
    TranscriptionFrame,
    InterimTranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    VADUserStartedSpeakingFrame,
    VADUserStoppedSpeakingFrame,
    LLMTextFrame,
    LLMMessagesFrame,
    LLMFullResponseStartFrame,
    LLMFullResponseEndFrame
)

__all__ = [
    # Base frames
    'Frame',
    'SystemFrame', 
    'DataFrame',
    'ErrorFrame',
    'StartFrame',
    'EndFrame',
    'CancelFrame',
    
    # Audio frames
    'AudioFrame',
    'AudioRawFrame',  # Compatibility alias
    'InputAudioRawFrame',
    'OutputAudioRawFrame',
    'TTSStartedFrame',
    'TTSStoppedFrame',
    'TTSAudioRawFrame',
    
    # Text frames
    'TextFrame',
    'TranscriptionFrame',
    'InterimTranscriptionFrame',
    'UserStartedSpeakingFrame',
    'UserStoppedSpeakingFrame',
    'VADUserStartedSpeakingFrame',
    'VADUserStoppedSpeakingFrame',
    'LLMTextFrame',
    'LLMMessagesFrame',
    'LLMFullResponseStartFrame',
    'LLMFullResponseEndFrame'
]