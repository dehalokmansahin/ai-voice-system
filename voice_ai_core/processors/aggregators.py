"""
Voice AI Core - Aggregator Processors
Extracted and simplified from Pipecat
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
import asyncio

from ..frames import Frame, TextFrame, StartFrame, EndFrame
from ..pipeline import FrameProcessor, FrameDirection


class OpenAILLMContext:
    """Simplified OpenAI LLM context manager"""
    
    def __init__(self, messages: List[Dict[str, str]] = None):
        self._messages = messages or []
    
    @property
    def messages(self) -> List[Dict[str, str]]:
        return self._messages
    
    def add_message(self, role: str, content: str):
        """Add a message to the context"""
        self._messages.append({"role": role, "content": content})
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages"""
        return self._messages.copy()


class SentenceAggregator(FrameProcessor):
    """Aggregates text frames into complete sentences"""
    
    def __init__(self):
        super().__init__()
        self._buffer = ""
        self._sentence_endings = {'.', '!', '?', '\n'}
    
    async def process_frame(
        self, 
        frame: Frame, 
        direction: FrameDirection = FrameDirection.DOWNSTREAM
    ) -> AsyncIterator[Frame]:
        """Process incoming frames and aggregate sentences"""
        
        if isinstance(frame, TextFrame):
            # Add text to buffer
            self._buffer += frame.text
            
            # Check if we have a complete sentence
            if any(ending in self._buffer for ending in self._sentence_endings):
                # Find the last sentence ending
                last_pos = -1
                for ending in self._sentence_endings:
                    pos = self._buffer.rfind(ending)
                    if pos > last_pos:
                        last_pos = pos
                
                if last_pos >= 0:
                    # Extract complete sentence(s)
                    sentence = self._buffer[:last_pos + 1].strip()
                    self._buffer = self._buffer[last_pos + 1:].strip()
                    
                    if sentence:
                        yield TextFrame(text=sentence)
            
        else:
            # Pass through non-text frames
            yield frame