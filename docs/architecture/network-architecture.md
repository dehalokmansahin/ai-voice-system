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
        TS --> WR[WebRTC]
        TS --> TURN[Coturn Relay]
    end
    
    SIP --> PSTN[PSTN/SIP Trunks]
    WR --> Browser[Web Browsers]
    TURN --> NAT[NAT Traversal]
```

## Service Mesh
- **Istio** for service-to-service communication
- **mTLS** for internal encryption
- **Circuit breakers** for resilience
- **Distributed tracing** with Jaeger
