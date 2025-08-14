# Overview

**Purpose**: Complete technical architecture for transforming the AI Voice System from POC to enterprise SaaS platform with modular, transport-agnostic design featuring WebRTC real-time communication.

**Evolution**: POC (5-10 calls) → MVP (100 calls) → Production (1,000 calls) → Enterprise (10,000+ calls)

## WebRTC Integration

The system now integrates **LiveKit WebRTC Transport** as the primary real-time communication layer, enabling:

- **Bidirectional Audio Streaming**: Real-time audio capture and playback with 16kHz mono PCM
- **Low Latency**: ~150-300ms transport latency with Smart-Turn v2 for natural turn-taking
- **Browser Compatibility**: Native WebRTC support across all modern browsers
- **Self-Hosted Control**: Full on-premises WebRTC infrastructure with LiveKit server
- **Turkish Language Support**: Optimized for Turkish conversation patterns and filler words

### Key Components

1. **LiveKit Server**: WebRTC signaling and TURN server for peer connection management
2. **Pipecat Integration**: Native LiveKitTransport with VAD and Smart-Turn analyzers
3. **Streaming Pipeline**: Full-duplex audio processing with barge-in capabilities
4. **Browser Client**: LiveKit JS SDK for seamless audio capture/playback
