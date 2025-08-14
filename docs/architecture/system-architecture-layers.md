# System Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend Layer                         │
│   React Dashboard │ Flow Builder │ WebRTC Client │ API   │
├─────────────────────────────────────────────────────────┤
│                 Management Platform                      │
│  Teams │ Prompts │ Flows │ Analytics │ MCP Server       │
├─────────────────────────────────────────────────────────┤
│              Voice AI Pipeline Core                      │
│  WebRTC Transport │ Audio Pipeline │ AI Services        │
├─────────────────────────────────────────────────────────┤
│                  WebRTC Layer                            │
│  LiveKit Server │ TURN │ WebRTC Signaling │ ICE         │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure                          │
│    Kubernetes (GKE) │ PostgreSQL │ Redis │ Storage      │
└─────────────────────────────────────────────────────────┘
```

## WebRTC Transport Layer Details

```
┌─────────────────────────────────────────────────────────┐
│                 Browser Client                           │
│  LiveKit JS SDK │ Audio Capture │ Media Player         │
├─────────────────────────────────────────────────────────┤
│                 WebRTC Stack                             │
│  ICE Candidates │ DTLS │ SRTP │ Echo Cancellation      │
├─────────────────────────────────────────────────────────┤
│                 LiveKit Server                           │
│  Room Management │ TURN Server │ SFU │ Participant API  │
├─────────────────────────────────────────────────────────┤
│              Pipecat Integration                         │
│  LiveKitTransport │ VAD │ Smart-Turn v2 │ Streaming    │
└─────────────────────────────────────────────────────────┘
```
