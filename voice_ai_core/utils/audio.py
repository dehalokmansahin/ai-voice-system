"""
Audio utilities - Essential audio processing functions
Simplified from Pipecat
"""

import numpy as np
from typing import Tuple


def resample_audio(audio_data: bytes, 
                   original_rate: int, 
                   target_rate: int,
                   channels: int = 1) -> bytes:
    """
    Simple audio resampling using linear interpolation
    """
    if original_rate == target_rate:
        return audio_data
    
    # Convert bytes to numpy array (assuming 16-bit audio)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Calculate resampling ratio
    ratio = target_rate / original_rate
    
    # Calculate new length
    new_length = int(len(audio_array) * ratio)
    
    # Create indices for interpolation
    old_indices = np.arange(len(audio_array))
    new_indices = np.linspace(0, len(audio_array) - 1, new_length)
    
    # Linear interpolation
    resampled = np.interp(new_indices, old_indices, audio_array)
    
    # Convert back to int16
    return resampled.astype(np.int16).tobytes()


def convert_audio_format(audio_data: bytes,
                        from_format: str,
                        to_format: str) -> bytes:
    """
    Convert between audio formats (PCM, μ-law, A-law)
    """
    if from_format == to_format:
        return audio_data
    
    # Convert to numpy array
    if from_format == 'pcm16':
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    elif from_format == 'pcm8':
        audio_array = np.frombuffer(audio_data, dtype=np.int8)
        audio_array = audio_array.astype(np.int16) * 256
    elif from_format == 'ulaw':
        # μ-law to PCM conversion (simplified)
        audio_array = np.frombuffer(audio_data, dtype=np.uint8)
        audio_array = ulaw_to_pcm(audio_array)
    elif from_format == 'alaw':
        # A-law to PCM conversion (simplified)
        audio_array = np.frombuffer(audio_data, dtype=np.uint8)
        audio_array = alaw_to_pcm(audio_array)
    else:
        raise ValueError(f"Unsupported format: {from_format}")
    
    # Convert to target format
    if to_format == 'pcm16':
        return audio_array.astype(np.int16).tobytes()
    elif to_format == 'pcm8':
        return (audio_array // 256).astype(np.int8).tobytes()
    elif to_format == 'ulaw':
        return pcm_to_ulaw(audio_array).tobytes()
    elif to_format == 'alaw':
        return pcm_to_alaw(audio_array).tobytes()
    else:
        raise ValueError(f"Unsupported format: {to_format}")


def calculate_audio_duration(audio_data: bytes,
                            sample_rate: int,
                            channels: int = 1,
                            bits_per_sample: int = 16) -> float:
    """Calculate duration of audio data in seconds"""
    bytes_per_sample = bits_per_sample // 8
    total_samples = len(audio_data) // (bytes_per_sample * channels)
    return total_samples / sample_rate


def ulaw_to_pcm(ulaw_data: np.ndarray) -> np.ndarray:
    """Convert μ-law to 16-bit PCM (simplified)"""
    # Simplified μ-law decoding
    ulaw_data = ulaw_data.astype(np.int16)
    sign = (ulaw_data & 0x80) >> 7
    position = ((ulaw_data & 0x70) >> 4) + 5
    quantization = ulaw_data & 0x0F
    
    pcm = ((quantization << position) - 33)
    pcm = np.where(sign, -pcm, pcm)
    return pcm.astype(np.int16)


def pcm_to_ulaw(pcm_data: np.ndarray) -> np.ndarray:
    """Convert 16-bit PCM to μ-law (simplified)"""
    # Simplified μ-law encoding
    pcm_data = np.clip(pcm_data, -32768, 32767).astype(np.int16)
    
    # Extract sign bit
    sign = ((pcm_data < 0).astype(np.uint8)) << 7
    
    # Work with absolute values
    pcm_abs = np.abs(pcm_data).astype(np.int16)
    
    # Apply bias (33)
    pcm_abs = pcm_abs + 33
    
    # Find position (exponent)
    position = np.zeros_like(pcm_abs, dtype=np.uint8)
    
    # Simple position calculation (avoiding log2 for stability)
    for i in range(8):
        mask = pcm_abs >= (33 << (i + 1))
        position = np.where(mask, i, position)
    
    # Calculate quantization bits
    quantization = ((pcm_abs >> (position + 1)) & 0x0F).astype(np.uint8)
    
    # Combine sign, position, and quantization
    ulaw = sign | (position << 4) | quantization
    
    return ulaw


def alaw_to_pcm(alaw_data: np.ndarray) -> np.ndarray:
    """Convert A-law to 16-bit PCM (simplified)"""
    # Simplified A-law decoding - similar to μ-law
    return ulaw_to_pcm(alaw_data)  # Using same logic for simplicity


def pcm_to_alaw(pcm_data: np.ndarray) -> np.ndarray:
    """Convert 16-bit PCM to A-law (simplified)"""
    # Simplified A-law encoding - similar to μ-law
    return pcm_to_ulaw(pcm_data)  # Using same logic for simplicity


def create_default_resampler():
    """Create default resampler (compatibility function)"""
    return None  # Simple placeholder - actual resampling done in convert functions


async def pcm_to_ulaw(pcm_bytes: bytes, input_rate: int, output_rate: int, resampler=None) -> bytes:
    """Convert PCM to μ-law with resampling"""
    # First resample if needed
    if input_rate != output_rate:
        pcm_bytes = resample_audio(pcm_bytes, input_rate, output_rate)
    
    # Convert to μ-law
    pcm_array = np.frombuffer(pcm_bytes, dtype=np.int16)
    ulaw_array = pcm_to_ulaw(pcm_array)
    return ulaw_array.tobytes()


async def ulaw_to_pcm(ulaw_bytes: bytes, input_rate: int, output_rate: int, resampler=None) -> bytes:
    """Convert μ-law to PCM with resampling"""
    # Convert from μ-law
    ulaw_array = np.frombuffer(ulaw_bytes, dtype=np.uint8)
    pcm_array = ulaw_to_pcm(ulaw_array)
    pcm_bytes = pcm_array.tobytes()
    
    # Resample if needed
    if input_rate != output_rate:
        pcm_bytes = resample_audio(pcm_bytes, input_rate, output_rate)
    
    return pcm_bytes