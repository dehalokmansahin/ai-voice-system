"""
Voice AI Core - OpenAI Services
Simplified interfaces for OpenAI integration
"""

from typing import AsyncIterator, Dict, Any, List, Optional
from dataclasses import dataclass, field
import asyncio

from ..frames import Frame, TextFrame
from ..pipeline import FrameProcessor, FrameDirection
from .base import BaseService


@dataclass
class OpenAILLMInputParams:
    """OpenAI LLM input parameters"""
    temperature: float = 0.7
    top_p: float = 1.0
    max_completion_tokens: int = 150
    model: str = "gpt-3.5-turbo"


class BaseOpenAILLMService(BaseService):
    """Base OpenAI LLM service interface"""
    
    InputParams = OpenAILLMInputParams
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", params: OpenAILLMInputParams = None):
        super().__init__()
        self._api_key = api_key
        self._model = model
        self._params = params or OpenAILLMInputParams()
    
    async def process_frame(
        self, 
        frame: Frame, 
        direction: FrameDirection = FrameDirection.DOWNSTREAM
    ) -> AsyncIterator[Frame]:
        """Process frames through OpenAI LLM"""
        # This is a simplified interface - actual implementation would
        # make API calls to OpenAI
        if isinstance(frame, TextFrame):
            # Placeholder for actual LLM processing
            response_text = f"[LLM Response to: {frame.text}]"
            yield TextFrame(text=response_text)
        else:
            yield frame
    
    def create_context_aggregator(self, context):
        """Create a context aggregator for this LLM"""
        return LLMContextAggregator(context, self)


class OpenAILLMService(BaseOpenAILLMService):
    """OpenAI LLM service implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", params: OpenAILLMInputParams = None):
        super().__init__(api_key, model, params)


class LLMContextAggregator:
    """Aggregates context for LLM interactions"""
    
    def __init__(self, context, llm_service):
        self._context = context
        self._llm_service = llm_service
    
    def user(self):
        """Get user context processor"""
        return UserContextProcessor(self._context)
    
    def assistant(self):
        """Get assistant context processor"""
        return AssistantContextProcessor(self._context)


class UserContextProcessor(FrameProcessor):
    """Processes user context"""
    
    def __init__(self, context):
        super().__init__()
        self._context = context
    
    async def process_frame(
        self, 
        frame: Frame, 
        direction: FrameDirection = FrameDirection.DOWNSTREAM
    ) -> AsyncIterator[Frame]:
        """Process user frames and add to context"""
        if isinstance(frame, TextFrame):
            # Add user message to context
            self._context.add_message("user", frame.text)
        
        yield frame


class AssistantContextProcessor(FrameProcessor):
    """Processes assistant context"""
    
    def __init__(self, context):
        super().__init__()
        self._context = context
    
    async def process_frame(
        self, 
        frame: Frame, 
        direction: FrameDirection = FrameDirection.DOWNSTREAM
    ) -> AsyncIterator[Frame]:
        """Process assistant frames and add to context"""
        if isinstance(frame, TextFrame):
            # Add assistant message to context
            self._context.add_message("assistant", frame.text)
        
        yield frame