"""
Unit tests for utility functions
"""

import pytest
import numpy as np
from voice_ai_core.utils import (
    resample_audio,
    convert_audio_format,
    calculate_audio_duration
)


class TestAudioUtils:
    """Test audio utility functions"""
    
    def test_resample_audio_same_rate(self):
        """Test resampling when rates are the same"""
        audio_data = b"\x00\x01" * 160
        resampled = resample_audio(audio_data, 16000, 16000)
        assert resampled == audio_data
    
    def test_resample_audio_upsample(self):
        """Test upsampling audio"""
        # Create simple audio data
        audio_data = np.array([0, 100, 200, 300], dtype=np.int16).tobytes()
        
        # Upsample from 8kHz to 16kHz (double)
        resampled = resample_audio(audio_data, 8000, 16000)
        
        # Should have roughly double the samples
        original_samples = len(audio_data) // 2
        resampled_samples = len(resampled) // 2
        assert resampled_samples == original_samples * 2
    
    def test_resample_audio_downsample(self):
        """Test downsampling audio"""
        # Create simple audio data
        audio_data = np.array([0, 50, 100, 150, 200, 250, 300, 350], dtype=np.int16).tobytes()
        
        # Downsample from 16kHz to 8kHz (half)
        resampled = resample_audio(audio_data, 16000, 8000)
        
        # Should have roughly half the samples
        original_samples = len(audio_data) // 2
        resampled_samples = len(resampled) // 2
        assert resampled_samples == original_samples // 2
    
    def test_convert_audio_format_same(self):
        """Test converting to same format"""
        audio_data = b"\x00\x01" * 160
        converted = convert_audio_format(audio_data, 'pcm16', 'pcm16')
        assert converted == audio_data
    
    def test_convert_pcm16_to_pcm8(self):
        """Test PCM16 to PCM8 conversion"""
        # Create PCM16 data
        pcm16_data = np.array([0, 256, -256, 512], dtype=np.int16).tobytes()
        
        # Convert to PCM8
        pcm8_data = convert_audio_format(pcm16_data, 'pcm16', 'pcm8')
        
        # Check size is halved
        assert len(pcm8_data) == len(pcm16_data) // 2
        
        # Convert back and check values are similar
        pcm16_back = convert_audio_format(pcm8_data, 'pcm8', 'pcm16')
        original = np.frombuffer(pcm16_data, dtype=np.int16)
        converted_back = np.frombuffer(pcm16_back, dtype=np.int16)
        
        # Values should be close (within quantization error)
        for orig, conv in zip(original, converted_back):
            assert abs(orig - conv) <= 256  # 8-bit quantization error
    
    def test_convert_pcm_to_ulaw(self):
        """Test PCM to μ-law conversion"""
        pcm_data = np.array([0, 1000, -1000, 5000], dtype=np.int16).tobytes()
        
        # Convert to μ-law
        ulaw_data = convert_audio_format(pcm_data, 'pcm16', 'ulaw')
        
        # μ-law should be 8-bit (half the size)
        assert len(ulaw_data) == len(pcm_data) // 2
        
        # Convert back
        pcm_back = convert_audio_format(ulaw_data, 'ulaw', 'pcm16')
        assert len(pcm_back) == len(pcm_data)
    
    def test_calculate_audio_duration(self):
        """Test audio duration calculation"""
        # 320 bytes = 160 samples (16-bit) = 0.01 seconds at 16kHz
        audio_data = b"\x00\x01" * 160
        
        duration = calculate_audio_duration(audio_data, 16000, 1, 16)
        assert abs(duration - 0.01) < 0.0001
        
        # Test with different parameters
        # 640 bytes = 160 samples (16-bit stereo) = 0.01 seconds at 16kHz
        duration = calculate_audio_duration(audio_data * 2, 16000, 2, 16)
        assert abs(duration - 0.01) < 0.0001
        
        # 160 bytes = 160 samples (8-bit) = 0.02 seconds at 8kHz
        audio_data_8bit = b"\x00" * 160
        duration = calculate_audio_duration(audio_data_8bit, 8000, 1, 8)
        assert abs(duration - 0.02) < 0.0001
    
    def test_invalid_format_conversion(self):
        """Test invalid format conversion raises error"""
        audio_data = b"\x00\x01" * 160
        
        with pytest.raises(ValueError):
            convert_audio_format(audio_data, 'invalid', 'pcm16')
        
        with pytest.raises(ValueError):
            convert_audio_format(audio_data, 'pcm16', 'invalid')