"""
Base frame types - Core of the voice processing system
Extracted and simplified from Pipecat
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
import time


@dataclass
class Frame(ABC):
    """Base frame class for all data flowing through the pipeline"""
    id: Optional[str] = field(default=None)
    timestamp: float = field(default_factory=lambda: time.time())
    
    def __post_init__(self):
        if self.id is None:
            # Generate simple ID based on timestamp
            self.id = f"{self.__class__.__name__}_{int(self.timestamp * 1000000)}"


@dataclass
class SystemFrame(Frame):
    """System control frames"""
    pass


@dataclass
class DataFrame(Frame):
    """Data-carrying frames"""
    pass


@dataclass
class ErrorFrame(SystemFrame):
    """Error frame for pipeline error handling"""
    error: str = ""
    details: Optional[Dict[str, Any]] = field(default=None)


@dataclass
class StartFrame(SystemFrame):
    """Indicates start of processing"""
    pass


@dataclass
class EndFrame(SystemFrame):
    """Indicates end of processing"""
    pass


@dataclass
class CancelFrame(SystemFrame):
    """Cancel current processing"""
    pass