"""
Silero VAD ONNX Model Implementation for Voice-AI-Core
Based on the Pipecat implementation but optimized for our framework
"""

import os
import time
import numpy as np
from typing import Optional
from loguru import logger


class SileroOnnxModel:
    """ONNX runtime wrapper for the Silero VAD model.
    
    Provides voice activity detection using the pre-trained Silero VAD model
    with ONNX runtime for efficient inference. Handles model state management
    and input validation for audio processing.
    """
    
    def __init__(self, model_path: str, force_onnx_cpu: bool = True):
        """Initialize the Silero ONNX model.
        
        Args:
            model_path: Path to the ONNX model file.
            force_onnx_cpu: Whether to force CPU execution provider.
        """
        try:
            import onnxruntime
        except ImportError:
            raise ImportError("onnxruntime is required for Silero VAD. Install with: pip install onnxruntime")
        
        # Configure ONNX Runtime session
        opts = onnxruntime.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1
        
        if force_onnx_cpu and "CPUExecutionProvider" in onnxruntime.get_available_providers():
            self.session = onnxruntime.InferenceSession(
                model_path, providers=["CPUExecutionProvider"], sess_options=opts
            )
        else:
            self.session = onnxruntime.InferenceSession(model_path, sess_options=opts)
        
        self.reset_states()
        self.sample_rates = [8000, 16000]
        
        logger.info(f"Loaded Silero VAD ONNX model from {model_path}")
    
    def _validate_input(self, x, sr: int):
        """Validate and preprocess input audio data."""
        if np.ndim(x) == 1:
            x = np.expand_dims(x, 0)
        if np.ndim(x) > 2:
            raise ValueError(f"Too many dimensions for input audio chunk {np.ndim(x)}")
        
        if sr not in self.sample_rates:
            raise ValueError(f"Supported sampling rates: {self.sample_rates} (got {sr})")
        if sr / np.shape(x)[1] > 31.25:
            raise ValueError("Input audio chunk is too short")
        
        return x, sr
    
    def reset_states(self, batch_size: int = 1):
        """Reset the internal model states.
        
        Args:
            batch_size: Batch size for state initialization. Defaults to 1.
        """
        self._state = np.zeros((2, batch_size, 128), dtype="float32")
        self._context = np.zeros((batch_size, 0), dtype="float32")
        self._last_sr = 0
        self._last_batch_size = 0
    
    def __call__(self, x, sr: int):
        """Process audio input through the VAD model.
        
        Args:
            x: Audio input array
            sr: Sample rate (8000 or 16000)
            
        Returns:
            Voice activity confidence score
        """
        x, sr = self._validate_input(x, sr)
        num_samples = 512 if sr == 16000 else 256
        
        if np.shape(x)[-1] != num_samples:
            raise ValueError(
                f"Provided number of samples is {np.shape(x)[-1]} "
                f"(Supported values: 256 for 8kHz, 512 for 16kHz)"
            )
        
        batch_size = np.shape(x)[0]
        context_size = 64 if sr == 16000 else 32
        
        # Reset states if needed
        if not self._last_batch_size:
            self.reset_states(batch_size)
        if (self._last_sr) and (self._last_sr != sr):
            self.reset_states(batch_size)
        if (self._last_batch_size) and (self._last_batch_size != batch_size):
            self.reset_states(batch_size)
        
        if not np.shape(self._context)[1]:
            self._context = np.zeros((batch_size, context_size), dtype="float32")
        
        # Concatenate context with input
        x = np.concatenate((self._context, x), axis=1)
        
        # Run inference
        if sr in [8000, 16000]:
            ort_inputs = {"input": x, "state": self._state, "sr": np.array(sr, dtype="int64")}
            ort_outs = self.session.run(None, ort_inputs)
            out, state = ort_outs
            self._state = state
        else:
            raise ValueError(f"Unsupported sample rate: {sr}")
        
        # Update context
        self._context = x[..., -context_size:]
        self._last_sr = sr
        self._last_batch_size = batch_size
        
        return out


def get_silero_model_path() -> Optional[str]:
    """Get the path to the Silero VAD ONNX model."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "data", "silero_vad.onnx")
    
    if os.path.exists(model_path):
        return model_path
    else:
        logger.warning(f"Silero model not found at {model_path}")
        return None