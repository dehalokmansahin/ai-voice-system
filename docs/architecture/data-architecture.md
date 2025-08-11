# Data Architecture

## Primary Storage
```yaml
Transactional Data:
  Service: Cloud SQL (PostgreSQL)
  Configuration: HA with read replicas
  Backup: Automated daily with PITR

Session State:
  Service: Memorystore Redis
  Configuration: Standard tier with replication
  TTL: 24 hours

Object Storage:
  Service: Cloud Storage
  Buckets:
    - recordings (30-day retention)
    - models (versioned)
    - exports (7-day retention)
```

## Analytics Pipeline
```yaml
Stream Processing:
  Service: Pub/Sub + Dataflow
  Purpose: Real-time metrics

Data Warehouse:
  Service: BigQuery
  Datasets:
    - calls (raw data)
    - analytics (aggregated)
    - billing (usage metrics)
```
