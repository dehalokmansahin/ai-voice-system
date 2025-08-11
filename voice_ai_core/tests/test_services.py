"""
Unit tests for service interfaces
"""

import pytest
import asyncio
from typing import AsyncIterator
from voice_ai_core.frames import Frame, AudioFrame, TextFrame, TranscriptionFrame
from voice_ai_core.services import BaseService, STTService, TTSService, LLMService


class MockSTTService(STTService):
    """Mock STT service for testing"""
    
    async def transcribe(self, audio: AudioFrame) -> AsyncIterator[TranscriptionFrame]:
        """Mock transcription"""
        yield TranscriptionFrame(text="transcribed text", confidence=0.95)


class MockTTSService(TTSService):
    """Mock TTS service for testing"""
    
    async def synthesize(self, text: str) -> AsyncIterator[AudioFrame]:
        """Mock synthesis"""
        # Generate dummy audio
        audio_data = b"\x00\x01" * 160
        yield AudioFrame(audio=audio_data, sample_rate=16000)


class MockLLMService(LLMService):
    """Mock LLM service for testing"""
    
    async def generate(self, prompt: str, context=None) -> AsyncIterator[TextFrame]:
        """Mock text generation"""
        yield TextFrame(text=f"Response to: {prompt}")


class TestBaseService:
    """Test base service functionality"""
    
    @pytest.mark.asyncio
    async def test_service_creation(self):
        """Test service creation"""
        service = MockSTTService("TestSTT")
        assert service.name == "TestSTT"
        assert service._initialized is False
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and cleanup"""
        service = MockSTTService()
        
        await service.initialize()
        assert service._initialized is True
        
        await service.cleanup()
        assert service._initialized is False


class TestSTTService:
    """Test STT service functionality"""
    
    @pytest.mark.asyncio
    async def test_stt_transcribe(self):
        """Test STT transcription"""
        service = MockSTTService()
        audio = AudioFrame(audio=b"\x00\x01" * 160, sample_rate=16000)
        
        transcriptions = []
        async for transcription in service.transcribe(audio):
            transcriptions.append(transcription)
        
        assert len(transcriptions) == 1
        assert transcriptions[0].text == "transcribed text"
        assert transcriptions[0].confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_stt_process_frame(self):
        """Test STT frame processing"""
        service = MockSTTService()
        audio = AudioFrame(audio=b"\x00\x01" * 160, sample_rate=16000)
        
        frames = []
        async for frame in service.process_frame(audio, None):
            frames.append(frame)
        
        assert len(frames) == 1
        assert isinstance(frames[0], TranscriptionFrame)
        assert frames[0].text == "transcribed text"
    
    @pytest.mark.asyncio
    async def test_stt_passthrough_non_audio(self):
        """Test STT passes through non-audio frames"""
        service = MockSTTService()
        text_frame = TextFrame(text="test")
        
        frames = []
        async for frame in service.process_frame(text_frame, None):
            frames.append(frame)
        
        assert len(frames) == 1
        assert frames[0] == text_frame


class TestTTSService:
    """Test TTS service functionality"""
    
    @pytest.mark.asyncio
    async def test_tts_synthesize(self):
        """Test TTS synthesis"""
        service = MockTTSService()
        
        audio_frames = []
        async for audio in service.synthesize("Hello, world!"):
            audio_frames.append(audio)
        
        assert len(audio_frames) == 1
        assert isinstance(audio_frames[0], AudioFrame)
        assert audio_frames[0].sample_rate == 16000
    
    @pytest.mark.asyncio
    async def test_tts_process_frame(self):
        """Test TTS frame processing"""
        service = MockTTSService()
        text_frame = TextFrame(text="Hello")
        
        frames = []
        async for frame in service.process_frame(text_frame, None):
            frames.append(frame)
        
        assert len(frames) == 1
        assert isinstance(frames[0], AudioFrame)
    
    @pytest.mark.asyncio
    async def test_tts_passthrough_non_text(self):
        """Test TTS passes through non-text frames"""
        service = MockTTSService()
        audio_frame = AudioFrame(audio=b"\x00\x01", sample_rate=16000)
        
        frames = []
        async for frame in service.process_frame(audio_frame, None):
            frames.append(frame)
        
        assert len(frames) == 1
        assert frames[0] == audio_frame


class TestLLMService:
    """Test LLM service functionality"""
    
    @pytest.mark.asyncio
    async def test_llm_generate(self):
        """Test LLM text generation"""
        service = MockLLMService()
        
        responses = []
        async for response in service.generate("Hello"):
            responses.append(response)
        
        assert len(responses) == 1
        assert responses[0].text == "Response to: Hello"
    
    @pytest.mark.asyncio
    async def test_llm_process_frame(self):
        """Test LLM frame processing"""
        service = MockLLMService()
        text_frame = TextFrame(text="Question")
        
        frames = []
        async for frame in service.process_frame(text_frame, None):
            frames.append(frame)
        
        assert len(frames) == 1
        assert isinstance(frames[0], TextFrame)
        assert frames[0].text == "Response to: Question"
    
    @pytest.mark.asyncio
    async def test_llm_passthrough_non_text(self):
        """Test LLM passes through non-text frames"""
        service = MockLLMService()
        audio_frame = AudioFrame(audio=b"\x00\x01", sample_rate=16000)
        
        frames = []
        async for frame in service.process_frame(audio_frame, None):
            frames.append(frame)
        
        assert len(frames) == 1
        assert frames[0] == audio_frame