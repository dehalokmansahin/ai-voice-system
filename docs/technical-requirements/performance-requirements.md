# Performance Requirements

## Latency Targets
- **Audio Processing**: <50ms end-to-end
- **Call Setup**: <2 seconds  
- **API Response**: <100ms p95
- **Database Queries**: <10ms p95
- **WebSocket Updates**: <100ms

### WebRTC-Specific Latency Requirements
- **WebRTC Connection**: <3 seconds establishment
- **ICE Gathering**: <2 seconds candidate collection
- **DTLS Handshake**: <1 second encryption setup  
- **Media Transmission**: <150ms audio roundtrip
- **VAD Detection**: <30ms speech onset
- **Smart-Turn Decision**: <100ms turn completion
- **Barge-in Response**: <300ms interruption handling
- **End-to-End Voice**: <800ms user speech to AI response

## Throughput Targets
- **Concurrent Calls**: 10,000+
- **API Requests**: 100,000/minute
- **WebSocket Connections**: 50,000
- **Database Connections**: 1,000 per service
- **Message Queue**: 1M messages/minute

### WebRTC Throughput Requirements
- **WebRTC Connections**: 1,000+ concurrent per LiveKit server
- **Audio Frame Processing**: 50 frames/second per connection (16kHz, 20ms frames)
- **LiveKit Rooms**: 500+ concurrent rooms per server
- **TURN Relay Bandwidth**: 10 Gbps aggregate capacity
- **Media Packet Rate**: 100,000+ packets/second per server
- **VAD Processing**: 1,000+ concurrent audio streams
- **Smart-Turn Analysis**: 8-second audio windows at 50 FPS

## Scalability Requirements
- **Horizontal Scaling**: Auto-scaling based on metrics
- **Database**: Read replicas + connection pooling
- **Cache**: Redis cluster mode
- **Storage**: Object storage with CDN
- **Network**: Load balancing across regions
