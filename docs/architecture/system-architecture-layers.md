# System Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend Layer                         │
│   React Dashboard │ Flow Builder │ Team Manager │ API    │
├─────────────────────────────────────────────────────────┤
│                 Management Platform                      │
│  Teams │ Prompts │ Flows │ Analytics │ MCP Server       │
├─────────────────────────────────────────────────────────┤
│              Voice AI Pipeline Core                      │
│  Transport Abstraction │ Audio Pipeline │ AI Services   │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure                          │
│    Kubernetes (GKE) │ PostgreSQL │ Redis │ Storage      │
└─────────────────────────────────────────────────────────┘
```
