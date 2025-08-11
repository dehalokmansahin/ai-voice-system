# Current System (POC Phase)

## Existing Services
- **ai-voice-backend**: Main orchestrator using Pipecat library
- **opensips**: SIP proxy (ports 5060, 8080, 8087, 8090)
- **vosk-server**: STT service (WebSocket port 2700)
- **piper-tts-server**: TTS service (ports 8000/8001)
- **llm-server**: LLM service (WebSocket port 8765) or OpenAI API

## POC Deployment (Active)
- **Platform**: GKE Standard with 3x e2-standard-4 nodes
- **Capacity**: 5-10 concurrent calls
- **Storage**: 36GB persistent volumes
- **Cost**: ~$225-245/month
- **Architecture**: Monolithic services with WebSocket communication
