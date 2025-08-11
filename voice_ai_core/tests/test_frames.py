"""
Unit tests for frame types
"""

import pytest
import time
from voice_ai_core.frames import (
    Frame, SystemFrame, DataFrame, ErrorFrame,
    StartFrame, EndFrame, CancelFrame,
    AudioFrame, InputAudioRawFrame, OutputAudioRawFrame,
    TTSStartedFrame, TTSStoppedFrame,
    TextFrame, TranscriptionFrame,
    UserStartedSpeakingFrame, UserStoppedSpeakingFrame,
    VADUserStartedSpeakingFrame, VADUserStoppedSpeakingFrame
)


class TestBaseFrames:
    """Test base frame types"""
    
    def test_frame_creation(self):
        """Test basic frame creation"""
        frame = StartFrame()
        assert frame.id is not None
        assert frame.timestamp > 0
        assert "StartFrame" in frame.id
    
    def test_frame_with_custom_id(self):
        """Test frame with custom ID"""
        frame = EndFrame(id="custom-id")
        assert frame.id == "custom-id"
    
    def test_error_frame(self):
        """Test error frame creation"""
        frame = ErrorFrame(error="Test error", details={"code": 500})
        assert frame.error == "Test error"
        assert frame.details["code"] == 500
    
    def test_system_frames(self):
        """Test system frame types"""
        start = StartFrame()
        end = EndFrame()
        cancel = CancelFrame()
        
        assert isinstance(start, SystemFrame)
        assert isinstance(end, SystemFrame)
        assert isinstance(cancel, SystemFrame)


class TestAudioFrames:
    """Test audio frame types"""
    
    def test_audio_frame_creation(self):
        """Test audio frame creation"""
        audio_data = b"\x00\x01" * 160  # 320 bytes
        frame = AudioFrame(audio=audio_data, sample_rate=16000, channels=1)
        
        assert frame.audio == audio_data
        assert frame.sample_rate == 16000
        assert frame.channels == 1
    
    def test_audio_frame_properties(self):
        """Test audio frame calculated properties"""
        # 320 bytes = 160 samples (16-bit) = 0.01 seconds at 16kHz
        audio_data = b"\x00\x01" * 160
        frame = AudioFrame(audio=audio_data, sample_rate=16000)
        
        assert frame.num_samples == 160
        assert abs(frame.duration - 0.01) < 0.0001
    
    def test_input_output_audio_frames(self):
        """Test input/output audio frame types"""
        audio_data = b"\x00\x01" * 160
        
        input_frame = InputAudioRawFrame(audio=audio_data)
        output_frame = OutputAudioRawFrame(audio=audio_data)
        
        assert isinstance(input_frame, AudioFrame)
        assert isinstance(output_frame, AudioFrame)
        assert isinstance(input_frame, DataFrame)
        assert isinstance(output_frame, DataFrame)
    
    def test_tts_frames(self):
        """Test TTS control frames"""
        started = TTSStartedFrame()
        stopped = TTSStoppedFrame()
        
        assert isinstance(started, SystemFrame)
        assert isinstance(stopped, SystemFrame)


class TestTextFrames:
    """Test text and speech event frames"""
    
    def test_text_frame(self):
        """Test text frame creation"""
        frame = TextFrame(text="Hello, world!")
        assert frame.text == "Hello, world!"
        assert isinstance(frame, DataFrame)
    
    def test_transcription_frame(self):
        """Test transcription frame"""
        frame = TranscriptionFrame(
            text="Transcribed text",
            confidence=0.95,
            is_final=True
        )
        assert frame.text == "Transcribed text"
        assert frame.confidence == 0.95
        assert frame.is_final is True
        assert isinstance(frame, TextFrame)
    
    def test_speech_event_frames(self):
        """Test speech event frames"""
        started = UserStartedSpeakingFrame()
        stopped = UserStoppedSpeakingFrame()
        vad_started = VADUserStartedSpeakingFrame()
        vad_stopped = VADUserStoppedSpeakingFrame()
        
        for frame in [started, stopped, vad_started, vad_stopped]:
            assert isinstance(frame, SystemFrame)
            assert frame.id is not None
            assert frame.timestamp > 0