"""
Voice AI Core - Voice Activity Detection (VAD) Components
Extracted and simplified from Pipecat
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class VADState(Enum):
    """Voice Activity Detection state"""
    QUIET = "quiet"
    SPEAKING = "speaking"
    
@dataclass
class VADParams:
    """VAD analyzer parameters"""
    confidence: float = 0.5
    start_secs: float = 0.2
    stop_secs: float = 0.5
    min_volume: float = 0.6