"""
Pipecat compatibility imports
Maps original Pipecat imports to new voice-ai-core structure
"""

# Frame imports - maintain original Pipecat paths
from ..frames import (
    Frame,
    SystemFrame,
    DataFrame,
    ErrorFrame,
    StartFrame,
    EndFrame,
    CancelFrame,
    AudioFrame,
    InputAudioRawFrame,
    OutputAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    TextFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    VADUserStartedSpeakingFrame,
    VADUserStoppedSpeakingFrame
)

# Pipeline imports
from ..pipeline import (
    FrameProcessor,
    FrameDirection,
    Pipeline,
    PipelineParams,
    PipelineRunner,
    PipelineTask
)

# Transport imports
from ..transports import (
    BaseTransport,
    BaseInputTransport,
    BaseOutputTransport,
    TransportParams
)

# Service imports
from ..services import (
    BaseService,
    STTService,
    TTSService,
    LLMService,
    BaseOpenAILLMService,
    OpenAILLMService,
    OpenAILLMInputParams
)

# Audio/VAD imports
from ..audio import (
    VADParams,
    VADState,
    SileroVADAnalyzer,
    BaseVADAnalyzer,
    WebRTCVADAnalyzer,
    create_vad_analyzer
)

# Processor imports
from ..processors import (
    OpenAILLMContext,
    SentenceAggregator
)

# Observer imports
from ..observers import (
    DebugLogObserver,
    LLMLogObserver,
    TranscriptionLogObserver,
    UserBotLatencyLogObserver
)

# Create module aliases for compatibility
class CompatibilityModule:
    """Module wrapper for compatibility imports"""
    
    def __init__(self, module_name):
        self.module_name = module_name
    
    def __getattr__(self, name):
        # Map old module paths to new ones
        mappings = {
            'pipecat.frames.frames': {
                'Frame': Frame,
                'SystemFrame': SystemFrame,
                'DataFrame': DataFrame,
                'ErrorFrame': ErrorFrame,
                'StartFrame': StartFrame,
                'EndFrame': EndFrame,
                'CancelFrame': CancelFrame,
                'InputAudioRawFrame': InputAudioRawFrame,
                'OutputAudioRawFrame': OutputAudioRawFrame,
                'TTSStartedFrame': TTSStartedFrame,
                'TTSStoppedFrame': TTSStoppedFrame,
                'TextFrame': TextFrame,
                'TranscriptionFrame': TranscriptionFrame,
                'UserStartedSpeakingFrame': UserStartedSpeakingFrame,
                'UserStoppedSpeakingFrame': UserStoppedSpeakingFrame,
                'VADUserStartedSpeakingFrame': VADUserStartedSpeakingFrame,
                'VADUserStoppedSpeakingFrame': VADUserStoppedSpeakingFrame
            },
            'pipecat.pipeline.pipeline': {
                'Pipeline': Pipeline,
                'PipelineParams': PipelineParams
            },
            'pipecat.pipeline.runner': {
                'PipelineRunner': PipelineRunner
            },
            'pipecat.pipeline.task': {
                'PipelineTask': PipelineTask
            },
            'pipecat.processors.frame_processor': {
                'FrameProcessor': FrameProcessor,
                'FrameDirection': FrameDirection
            },
            'pipecat.transports.base_transport': {
                'BaseTransport': BaseTransport,
                'TransportParams': TransportParams
            },
            'pipecat.transports.base_input': {
                'BaseInputTransport': BaseInputTransport
            },
            'pipecat.transports.base_output': {
                'BaseOutputTransport': BaseOutputTransport
            }
        }
        
        if self.module_name in mappings and name in mappings[self.module_name]:
            return mappings[self.module_name][name]
        
        raise AttributeError(f"module '{self.module_name}' has no attribute '{name}'")


# Export all for star imports
__all__ = [
    # Frames
    'Frame',
    'SystemFrame',
    'DataFrame',
    'ErrorFrame',
    'StartFrame',
    'EndFrame',
    'CancelFrame',
    'AudioFrame',
    'InputAudioRawFrame',
    'OutputAudioRawFrame',
    'TTSStartedFrame',
    'TTSStoppedFrame',
    'TextFrame',
    'TranscriptionFrame',
    'UserStartedSpeakingFrame',
    'UserStoppedSpeakingFrame',
    'VADUserStartedSpeakingFrame',
    'VADUserStoppedSpeakingFrame',
    
    # Pipeline
    'FrameProcessor',
    'FrameDirection',
    'Pipeline',
    'PipelineParams',
    'PipelineRunner',
    'PipelineTask',
    
    # Transport
    'BaseTransport',
    'BaseInputTransport',
    'BaseOutputTransport',
    'TransportParams',
    
    # Services
    'BaseService',
    'STTService',
    'TTSService',
    'LLMService'
]