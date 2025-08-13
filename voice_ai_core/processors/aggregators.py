"""
Voice AI Core - Aggregator Processors
Extracted and simplified from Pipecat
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
import asyncio

from ..frames import Frame, TextFrame, StartFrame, EndFrame, DataFrame
from .base import FrameProcessor, FrameDirection


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
    
    @classmethod
    def from_messages(cls, messages: List[Dict[str, str]]) -> "OpenAILLMContext":
        """Create context from messages list"""
        return cls(messages)


@dataclass
class OpenAILLMContextFrame(DataFrame):
    """Frame containing OpenAI LLM context"""
    context: OpenAILLMContext = field(default_factory=OpenAILLMContext)


class LLMUserContextAggregator(FrameProcessor):
    """Aggregates user context for LLM"""
    
    def __init__(self, context: OpenAILLMContext):
        super().__init__()
        self._context = context
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process user context frames"""
        if isinstance(frame, TextFrame):
            self._context.add_message("user", frame.text)
        await self.push_frame(frame, direction)


class LLMAssistantContextAggregator(FrameProcessor):
    """Aggregates assistant context for LLM"""
    
    def __init__(self, context: OpenAILLMContext):
        super().__init__()
        self._context = context
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process assistant context frames"""
        if isinstance(frame, TextFrame):
            self._context.add_message("assistant", frame.text)
        await self.push_frame(frame, direction)


class SentenceAggregator(FrameProcessor):
    """Aggregates text frames into complete sentences"""
    
    def __init__(self):
        super().__init__()
        self._aggregation = ""
        self._sentence_endings = {'.', '!', '?', '\n'}
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process incoming frames and aggregate sentences"""
        
        if isinstance(frame, TextFrame):
            # Add text to buffer
            self._aggregation += frame.text
            
            # Check if we have a complete sentence
            if any(ending in self._aggregation for ending in self._sentence_endings):
                # Find the last sentence ending
                last_pos = -1
                for ending in self._sentence_endings:
                    pos = self._aggregation.rfind(ending)
                    if pos > last_pos:
                        last_pos = pos
                
                if last_pos >= 0:
                    # Extract complete sentence(s)
                    sentence = self._aggregation[:last_pos + 1].strip()
                    self._aggregation = self._aggregation[last_pos + 1:].strip()
                    
                    if sentence:
                        await self.push_frame(TextFrame(text=sentence), direction)
            
        else:
            # Pass through non-text frames
            await self.push_frame(frame, direction)