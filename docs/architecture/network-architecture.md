# Network Architecture

## Traffic Flow
```mermaid
graph TB
    User[User Device] --> CDN[Cloud CDN]
    CDN --> LB[Global Load Balancer]
    
    subgraph "GKE Cluster"
        LB --> IG[Ingress Gateway]
        IG --> API[API Gateway]
        
        API --> MS[Management Services]
        API --> VP[Voice Pipeline]
        
        VP --> TS[Transport Services]
        VP --> AS[AI Services]
        
        TS --> SIP[SIP Protocols]
        TS --> LK[LiveKit Server]
        TS --> WR[WebRTC Gateway]
        
        LK --> TURN[LiveKit TURN]
        LK --> SFU[SFU Media Server]
        WR --> ICE[ICE Candidates]
    end
    
    SIP --> PSTN[PSTN/SIP Trunks]
    LK --> Browser[Web Browsers]
    TURN --> NAT[NAT Traversal]
    ICE --> WebClient[WebRTC Clients]
```

## WebRTC Network Architecture

### LiveKit WebRTC Stack
```mermaid
graph TB
    Browser[Web Browser] --> JS[LiveKit JS SDK]
    JS --> WTC[WebRTC Connection]
    
    subgraph "LiveKit Server"
        WTC --> SIG[Signaling Server]
        SIG --> RM[Room Manager]
        RM --> SFU[SFU Engine]
        SFU --> TURN[TURN Server]
    end
    
    subgraph "Pipecat Pipeline"
        SFU --> LKT[LiveKitTransport]
        LKT --> VAD[VAD Processor]
        VAD --> ST[Smart-Turn v2]
        ST --> STT[Vosk STT]
        STT --> LLM[OpenAI LLM]
        LLM --> TTS[Piper TTS]
        TTS --> LKT
    end
    
    TURN --> NAT[NAT Traversal]
```

### Network Flow Details

#### Connection Establishment
1. **ICE Gathering**: Browser collects local candidates
2. **Signaling**: Exchange SDP offers/answers via LiveKit
3. **DTLS Handshake**: Establish encrypted media channel
4. **SRTP Setup**: Secure real-time transport protocol
5. **Media Flow**: Bidirectional audio streaming begins

#### Audio Processing Pipeline
```
Browser Microphone → WebRTC Capture → LiveKit → Pipecat Pipeline
                                                       ↓
Browser Speakers  ← WebRTC Playback ← LiveKit ← Audio Processing
```

#### Port Configuration
```yaml
LiveKit Server:
  - 7880: WebRTC signaling (TCP)
  - 7881: TURN server (TCP/UDP)  
  - 7882-7950: ICE candidate range (UDP)

Network Requirements:
  - UDP: Required for media transmission
  - TCP: Fallback for restricted networks
  - STUN/TURN: NAT traversal support
```

## Service Mesh
- **Istio** for service-to-service communication
- **mTLS** for internal encryption
- **Circuit breakers** for resilience
- **Distributed tracing** with Jaeger

## WebRTC Security
- **DTLS**: End-to-end media encryption
- **SRTP**: Secure audio stream transport
- **Token Authentication**: LiveKit JWT tokens
- **Origin Validation**: CORS and domain restrictions
