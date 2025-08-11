"""
Voice AI Core - VAD Analyzer Implementation
Extracted and optimized VAD functionality
"""

import asyncio
import time
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Callable
from enum import Enum
from dataclasses import dataclass
from loguru import logger

from .vad import VADParams, VADState
from .silero_onnx import SileroOnnxModel, get_silero_model_path


class BaseVADAnalyzer(ABC):
    """Base Voice Activity Detection analyzer"""
    
    def __init__(self, params: VADParams = None):
        self.params = params or VADParams()
        self.sample_rate = 16000  # Default sample rate
    
    @abstractmethod
    async def analyze_audio(self, audio_data: bytes) -> VADState:
        """Analyze audio data and return VAD state"""
        pass
    
    @abstractmethod 
    async def initialize(self):
        """Initialize the VAD analyzer"""
        pass
    
    async def cleanup(self):
        """Cleanup VAD resources"""
        pass


class SileroVADAnalyzer(BaseVADAnalyzer):
    """
    Silero VAD implementation using ONNX runtime (no PyTorch needed!)
    Optimized for Turkish speech with proper Silero VAD model
    """
    
    # Model reset interval to prevent memory growth
    _MODEL_RESET_INTERVAL = 5.0
    
    def __init__(self, params: VADParams = None):
        super().__init__(params)
        self._model = None
        self._initialized = False
        self._current_state = VADState.QUIET
        self._speech_start_time = None
        self._silence_start_time = None
        self._last_reset_time = 0
        self._frames_required = 512  # Default for 16kHz
        
    async def initialize(self):
        """Initialize Silero ONNX VAD model"""
        try:
            # Try to load the ONNX Silero model
            model_path = get_silero_model_path()
            if model_path:
                self._model = SileroOnnxModel(model_path, force_onnx_cpu=True)
                logger.info("✅ Silero ONNX VAD model loaded successfully")
                
                # Set frame requirements based on sample rate
                self._frames_required = 512 if self.sample_rate == 16000 else 256
                self._initialized = True
                
            else:
                logger.warning("❌ Silero model file not found, using energy-based VAD fallback")
                self._initialized = True
                self._model = None
                
        except Exception as e:
            logger.warning(f"❌ Failed to load Silero ONNX model: {e}, using energy-based VAD fallback")
            self._initialized = True
            self._model = None
    
    def set_sample_rate(self, sample_rate: int):
        """Set the sample rate for audio processing."""
        if sample_rate not in [8000, 16000]:
            logger.warning(f"Silero VAD works best with 8kHz or 16kHz (got {sample_rate})")
        
        self.sample_rate = sample_rate
        self._frames_required = 512 if sample_rate == 16000 else 256
        
        # Reset model state if already initialized
        if self._model:
            self._model.reset_states()
    
    def num_frames_required(self) -> int:
        """Get the number of audio frames required for VAD analysis."""
        return self._frames_required
    
    async def analyze_audio(self, audio_data: bytes) -> VADState:
        """Analyze audio and return VAD state"""
        if not self._initialized:
            await self.initialize()
        
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        if self._model is not None:
            return await self._analyze_with_silero_onnx(audio_array)
        else:
            return await self._analyze_with_energy(audio_array)
    
    async def _analyze_with_silero_onnx(self, audio_array: np.ndarray) -> VADState:
        """Analyze using Silero ONNX model"""
        try:
            if len(audio_array) == 0:
                return self._current_state
            
            # Ensure we have the right number of samples for the model
            required_samples = self._frames_required
            if len(audio_array) != required_samples:
                # Pad or truncate to required size
                if len(audio_array) < required_samples:
                    audio_array = np.pad(audio_array, (0, required_samples - len(audio_array)))
                else:
                    audio_array = audio_array[:required_samples]
            
            # Run ONNX inference
            speech_prob = self._model(audio_array, self.sample_rate)[0]
            
            # Apply confidence threshold
            is_speech = speech_prob > self.params.confidence
            
            # Periodic model state reset to prevent memory growth
            current_time = time.time()
            if current_time - self._last_reset_time >= self._MODEL_RESET_INTERVAL:
                self._model.reset_states()
                self._last_reset_time = current_time
            
            return await self._update_vad_state(is_speech)
            
        except Exception as e:
            logger.warning(f"Silero ONNX VAD error: {e}, falling back to energy-based VAD")
            return await self._analyze_with_energy(audio_array)
    
    async def _analyze_with_energy(self, audio_array: np.ndarray) -> VADState:
        """Fallback energy-based VAD for Turkish speech optimization"""
        if len(audio_array) == 0:
            return self._current_state
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_array ** 2))
        
        # Turkish speech optimized energy threshold (lower than default)
        energy_threshold = self.params.min_volume if self.params.min_volume > 0 else 0.01
        
        # Turkish speech tends to have different energy patterns
        # Apply Turkish-specific adjustments
        turkish_adjustment = 0.7  # Lower threshold for Turkish speech characteristics
        adjusted_threshold = energy_threshold * turkish_adjustment
        
        is_speech = rms > adjusted_threshold
        
        return await self._update_vad_state(is_speech)
    
    async def _update_vad_state(self, is_speech: bool) -> VADState:
        """Update VAD state with hysteresis"""
        current_time = asyncio.get_event_loop().time()
        
        if is_speech:
            if self._current_state == VADState.QUIET:
                if self._speech_start_time is None:
                    self._speech_start_time = current_time
                elif (current_time - self._speech_start_time) >= self.params.start_secs:
                    self._current_state = VADState.SPEAKING
                    self._speech_start_time = None
                    self._silence_start_time = None
            else:
                # Continue speaking
                self._silence_start_time = None
        else:
            if self._current_state == VADState.SPEAKING:
                if self._silence_start_time is None:
                    self._silence_start_time = current_time
                elif (current_time - self._silence_start_time) >= self.params.stop_secs:
                    self._current_state = VADState.QUIET
                    self._silence_start_time = None
                    self._speech_start_time = None
            else:
                # Continue quiet
                self._speech_start_time = None
        
        return self._current_state


class WebRTCVADAnalyzer(BaseVADAnalyzer):
    """Alternative WebRTC VAD implementation (lightweight)"""
    
    def __init__(self, params: VADParams = None):
        super().__init__(params)
        self._vad = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize WebRTC VAD"""
        try:
            import webrtcvad
            # WebRTC VAD aggressiveness (0-3, 3 is most aggressive)
            aggressiveness = min(3, max(0, int(self.params.confidence * 3)))
            self._vad = webrtcvad.Vad(aggressiveness)
            self._initialized = True
        except ImportError:
            print("Warning: webrtcvad not available")
            self._initialized = False
    
    async def analyze_audio(self, audio_data: bytes) -> VADState:
        """Analyze using WebRTC VAD"""
        if not self._initialized:
            await self.initialize()
            
        if not self._vad:
            return VADState.QUIET
            
        try:
            # WebRTC VAD expects specific frame sizes
            # 10ms, 20ms, or 30ms at 8kHz, 16kHz, 32kHz, or 48kHz
            is_speech = self._vad.is_speech(audio_data, self.sample_rate)
            return VADState.SPEAKING if is_speech else VADState.QUIET
        except:
            return VADState.QUIET


def create_vad_analyzer(vad_type: str = "silero", params: VADParams = None) -> BaseVADAnalyzer:
    """Factory function to create VAD analyzer"""
    if vad_type.lower() == "silero":
        return SileroVADAnalyzer(params)
    elif vad_type.lower() == "webrtc":
        return WebRTCVADAnalyzer(params)
    else:
        raise ValueError(f"Unknown VAD type: {vad_type}")