# SHL Recommender - Deployment Guide

## Quick Start

### Option 1: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run recommender directly
python -c "from shl_recommender import SHLRecommender; r = SHLRecommender('shl_product_catalog_clean.json'); print(r.process_turn('leadership assessment'))"

# Start FastAPI server
python api_server.py
# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Option 2: Docker Deployment

```bash
# Build image
docker build -t shl-recommender .

# Run container
docker run -p 8000:8000 -v $(pwd):/app shl-recommender

# Access at http://localhost:8000
```

### Option 3: Cloud Deployment (Render, Railway, Fly.io)

See deployment-specific instructions below.

## API Endpoints

### GET /health
Health check endpoint.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2026-05-15T12:00:00Z",
  "catalog_size": 377,
  "service_ready": true
}
```

### POST /chat
Process user conversation.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "We need leadership assessments for a senior manager"}
    ],
    "session_id": "my_session_123"
  }'
```

Response:
```json
{
  "reply": "Based on your requirements, here are suitable assessments...",
  "recommendations": [
    {
      "name": "OPQ32r",
      "url": "https://www.shl.com/assessments/opq32r",
      "test_type": "Personality"
    }
  ],
  "end_of_conversation": false,
  "request_id": "my_session_123",
  "timestamp": "2026-05-15T12:00:00Z"
}
```

## Running Evaluations

### Evaluate labeled traces (C1-C10):
```bash
python evaluate_traces.py
```

Outputs:
- `evaluation_results.json` - Detailed metrics
- `evaluation_analysis.md` - Analysis report

### Run simulator (labeled + synthetic):
```bash
python simulate_evaluator.py
```

Outputs:
- `evaluation_simulator_report.json` - Comprehensive metrics

### Test production hardening:
```bash
python test_phase3.py
```

## Environment Variables

Create `.env` file:

```bash
# Catalog path (default: shl_product_catalog_clean.json)
CATALOG_PATH=shl_product_catalog_clean.json

# Debug mode (default: false)
DEBUG_MODE=false

# Log level (default: INFO)
LOG_LEVEL=INFO

# API host/port
API_HOST=0.0.0.0
API_PORT=8000
```

## File Structure

```
.
├── shl_recommender.py              # Main recommender system
├── api_server.py                   # FastAPI service
├── evaluate_traces.py              # Evaluation framework
├── simulate_evaluator.py           # Simulator for labeled + synthetic traces
├── fuzzy_retrieval.py             # Fuzzy matching enhancement
├── stack_generator.py              # Recommendation stack generation
├── semantic_role_clustering.py    # Role normalization
├── catalog_relationships.py        # Assessment relationships
├── refinement_handler.py          # Refinement handling
├── evaluation_analytics.py        # Extended analytics
├── shl_product_catalog_clean.json # Catalog (377 assessments)
├── GenAI_SampleConversations/     # Labeled traces (C1-C10)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose
├── .env.example                   # Environment template
├── run.sh                         # Linux/Mac startup script
├── run.bat                        # Windows startup script
└── README.md                      # This file
```

## System Requirements

- Python 3.9+
- 200MB disk space (catalog + models)
- 150MB RAM (typical)
- <100ms response time per request

## Production Checklist

- [ ] Catalog file present (`shl_product_catalog_clean.json`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured (`.env`)
- [ ] API tests pass (`python test_api.py`)
- [ ] Evaluations run successfully (`python evaluate_traces.py`)
- [ ] Docker image builds (if using Docker)
- [ ] Health endpoint responds (GET /health)

## Monitoring

### Response Latency
Monitor average response time - target <100ms.

### Hallucinations
Track false recommendations (URLs not in catalog) - target 0%.

### Schema Compliance
Verify all responses match required schema - target 100%.

### Recall@10
Average recall across test traces - current: 34.44%.

## Troubleshooting

### Catalog not found
```
Error: FileNotFoundError: shl_product_catalog_clean.json
Solution: Ensure catalog file is in working directory
```

### API port already in use
```
Error: Address already in use
Solution: Kill existing process or use different port
  Windows: netstat -ano | findstr :8000
  Linux: lsof -i :8000
```

### Out of memory
```
Solution: Reduce top_k in recommend() or use caching
```

## Performance Tuning

### Faster responses
- Cache frequently used constraints
- Reduce top_k from 20 to 10
- Use async database queries (if future versions)

### Better accuracy
- Fine-tune keyword weights
- Expand semantic skill groups
- Add domain-specific patterns

### Scalability
- Load test with concurrent users
- Implement caching layer
- Consider database backend for assessments

## Support

For issues or questions:
1. Check evaluation reports for metrics
2. Run test suites
3. Review debug logs (if DEBUG_MODE=true)
4. Check API documentation at /docs

## License

This system is proprietary. See LICENSE file for details.
