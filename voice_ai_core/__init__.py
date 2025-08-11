"""
Voice AI Core - Lightweight voice processing framework
Extracted from Pipecat with 70% code reduction

Key features:
- Essential frame types only
- Simplified pipeline processing
- Transport-agnostic design
- Minimal dependencies
"""

__version__ = "0.1.0"

# Import main components
from .frames import *
from .pipeline import *
from .transports import *
from .services import *
from .utils import *
from .audio import *
from .processors import *
from .observers import *

# For backward compatibility
from .compat import *