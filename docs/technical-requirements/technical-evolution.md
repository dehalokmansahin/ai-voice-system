# Technical Evolution

## Current System (POC)
- **Architecture**: Docker Compose → Kubernetes (GKE)
- **Services**: 5 containers (OpenSIPS, Vosk, Piper, LLM, AI-Backend)  
- **Capacity**: 5-10 concurrent calls
- **Protocols**: SIP (OpenSIPS) only
- **Dependencies**: Full Pipecat library (~18K LOC)

## Target System (Platform)
- **Architecture**: Modular Kubernetes microservices
- **Capacity**: 10,000+ concurrent calls
- **Protocols**: SIP, WebRTC, PSTN with TURN relay
- **Dependencies**: Custom core (~5K LOC, 70% reduction)
