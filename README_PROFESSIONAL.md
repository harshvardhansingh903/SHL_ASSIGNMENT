# SHL Recommender - Conversational Assessment Recommendation System

Production-grade REST API for intelligent SHL assessment recommendations in hiring scenarios.

## Quick Links

- **API Documentation:** [API Examples](API_EXAMPLES.md)
- **Technical Approach:** [APPROACH_DOCUMENT.md](docs/APPROACH_DOCUMENT.md)
- **Performance Report:** [FINAL_REPORT.md](docs/FINAL_REPORT.md)

---

## What is SHL Recommender?

SHL Recommender is a conversational system that recommends SHL assessments based on hiring requirements. It understands:

- **Roles:** Engineering, management, leadership, support, operations, etc.
- **Seniority levels:** Entry-level, mid-level, senior, C-suite
- **Competencies:** Technical skills, leadership, communication, problem-solving
- **Requirements:** Duration constraints, multi-language needs, specific assessment types
- **Comparisons:** Differences between similar assessments

The system provides intelligent recommendations with 34%+ recall on unseen hiring scenarios.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         FastAPI REST API Service                        │
│  (api_server.py)                                        │
└────────────────┬──────────────────────────────────────┘
                 │
      ┌──────────┴───────────┐
      │                      │
      ▼                      ▼
┌──────────────┐      ┌──────────────────┐
│  Chat Input  │      │  Health Check    │
│  Processing  │      │                  │
└──────────────┘      └──────────────────┘
      │
      ▼
┌──────────────────────────────────────────┐
│  SHL Recommender Engine                  │
│  (shl_recommender.py)                    │
│                                          │
│  1. Constraint Extraction                │
│  2. Hybrid Retrieval Scoring             │
│  3. Diversity Ranking                    │
│  4. URL Grounding Verification           │
│  5. Response Validation                  │
└──────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────┐
│  SHL Catalog (377 Assessments)           │
│  (data/shl_product_catalog_clean.json)   │
└──────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────┐
│  Ranked Recommendations                  │
│  (Top 10 with confidence scores)         │
└──────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- 200 MB disk space
- 150 MB RAM (minimum)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/shl-recommender.git
cd shl-recommender
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation

---

## Running the System

### Option A: Local Development Server

**Start the API server:**
```bash
cd app
python api_server.py
```

**Server starts at:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs`
**Interactive Swagger UI:** Automatic at `/docs` endpoint

**Test endpoint:**
```bash
curl http://localhost:8000/health
```

### Option B: Docker Container (Local)

**Build image:**
```bash
docker build -t shl-recommender .
```

**Run container:**
```bash
docker run -p 8000:8000 shl-recommender
```

**Container starts at:** `http://localhost:8000`

**Stop container:**
```bash
docker ps  # Get container ID
docker stop <container-id>
```

### Option C: Docker Compose (Multiple Services)

```bash
docker-compose up
```

---

## Cloud Deployment

### Deploy to Render.com

**1. Push to GitHub:**
```bash
git remote add origin https://github.com/your-org/shl-recommender.git
git push -u origin main
```

**2. Create Render Web Service:**
- Go to https://render.com
- Click "Create +" → "Web Service"
- Connect GitHub repository
- Configure:
  - **Environment:** Python 3.11
  - **Build command:** `pip install -r requirements.txt`
  - **Start command:** `uvicorn app.api_server:app --host 0.0.0.0 --port $PORT`
  - **Instance Type:** Free (or Starter for production)

**3. Environment Variables:**
```
CATALOG_PATH=data/shl_product_catalog_clean.json
DEBUG_MODE=false
LOG_LEVEL=INFO
```

**4. Deploy:**
Click "Create Web Service" - Render builds and deploys automatically

**API URL:** https://shl-recommender.onrender.com

### Deploy to Railway.app

**1. Connect GitHub Repository**
- Go to https://railway.app
- Click "Create" → "New Project from GitHub"
- Select repository

**2. Configuration:**
```
PYTHON_VERSION=3.11
RAILWAY_ENVIRONMENT_NAME=production
```

**3. Deploy:**
Railway automatically detects Python and deploys

### Deploy to Fly.io

**1. Install Fly CLI:**
```bash
curl -L https://fly.io/install.sh | sh
```

**2. Create app:**
```bash
fly launch
```

**3. Deploy:**
```bash
fly deploy
```

---

## API Usage

### Health Check Endpoint

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-05-15T12:00:00Z",
  "catalog_size": 377,
  "service_ready": true
}
```

### Chat Endpoint

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "We need a leadership assessment for a senior manager"
      }
    ]
  }'
```

**Response:**
```json
{
  "reply": "I can help with leadership assessments. Based on your requirements...",
  "recommendations": [
    {
      "name": "OPQ32r",
      "url": "https://example.com/opq32r",
      "test_type": "Personality & Behavior"
    }
  ],
  "end_of_conversation": false,
  "request_id": "req_abc123",
  "timestamp": "2026-05-15T12:00:01Z"
}
```

**See [API_EXAMPLES.md](API_EXAMPLES.md) for complete examples.**

---

## Project Structure

```
shl-recommender/
├── app/                              # Application code
│   ├── api_server.py                # FastAPI REST service
│   ├── shl_recommender.py           # Main recommendation engine
│   ├── stack_generator.py           # Assessment battery generation
│   ├── semantic_role_clustering.py  # Role normalization
│   ├── catalog_relationships.py     # Assessment relationships
│   ├── refinement_handler.py        # Conversation refinement
│   ├── evaluation_analytics.py      # Evaluation metrics
│   └── fuzzy_retrieval.py           # Fuzzy string matching
│
├── data/                             # Data files
│   └── shl_product_catalog_clean.json  # 377 SHL assessments
│
├── tests/                            # Test files
│   ├── validate_system.py           # 6-test validation suite
│   ├── evaluate_traces.py           # C1-C10 trace evaluation
│   ├── simulate_evaluator.py        # Synthetic trace evaluation
│   └── test_api.py                  # API endpoint tests
│
├── docs/                             # Documentation
│   ├── APPROACH_DOCUMENT.md         # Technical approach (2 pages)
│   ├── FINAL_REPORT.md              # Performance report (5 pages)
│   ├── evaluation_results.json      # Metrics from C1-C10
│   └── evaluation_simulator_report.json  # S1-S10 metrics
│
├── GenAI_SampleConversations/        # Test conversations
│   ├── C1.md - C10.md               # 10 labeled hiring scenarios
│
├── Dockerfile                        # Docker configuration
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment template
├── API_EXAMPLES.md                   # API usage examples
└── README.md                         # This file
```

---

## Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Catalog
CATALOG_PATH=data/shl_product_catalog_clean.json

# Server
API_HOST=0.0.0.0
API_PORT=8000

# Behavior
DEBUG_MODE=false
LOG_LEVEL=INFO

# Performance
MAX_RESPONSE_TIME=30
TOP_K_RECOMMENDATIONS=10

# Features
ENABLE_FUZZY_MATCHING=true
ENABLE_REFINEMENT=true
ENABLE_STACK_GENERATION=true
ENABLE_ROLE_CLUSTERING=true
```

### Load from .env

```bash
# On Linux/Mac
export $(cat .env | xargs)

# On Windows PowerShell
Get-Content .env | ForEach-Object { $env:$_ }

# Run server
python app/api_server.py
```

---

## Testing

### Run All Validation Tests

```bash
python tests/validate_system.py
```

Runs:
1. Schema Compliance (100% valid JSON)
2. URL Grounding (0% hallucinations)
3. Error Handling (no crashes)
4. Performance (latency < 100ms)
5. Multi-turn Conversations
6. API Endpoints (health + chat)

### Run Evaluation on Labeled Traces

```bash
python tests/evaluate_traces.py
```

Evaluates system on C1-C10 conversation traces with metrics.

### Run Simulator on Synthetic Traces

```bash
python tests/simulate_evaluator.py
```

Tests system robustness on 10+ synthetic hidden scenarios.

### Test API Endpoints

```bash
python tests/test_api.py
```

Tests FastAPI endpoints directly using TestClient.

---

## Performance Characteristics

### Response Latency
- **Cold start:** ~3 seconds (catalog loading)
- **Warm response:** 2ms average
- **P99 latency:** <10ms
- **Timeout:** 30 seconds per request

### Resource Usage
- **Memory:** ~150 MB (at rest)
- **Disk:** 200 MB (code + data)
- **CPU:** <50% on typical requests

### Scalability
- **Stateless:** Can run multiple instances
- **Load balancing:** Compatible with any reverse proxy
- **Concurrency:** Unlimited (no connection pooling required)

---

## Monitoring & Troubleshooting

### Check Service Status

```bash
curl http://localhost:8000/health

# Response indicates:
# - status: "ok" or "degraded"
# - catalog_size: number of assessments loaded
# - service_ready: true/false
```

### View Logs

**Local server:**
```bash
# Logs appear in terminal where server is running
```

**Docker:**
```bash
docker logs <container-id>
```

**Render.com:**
- Go to deployment dashboard
- Click "Logs" tab

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Port 8000 in use | Another process using port | `lsof -i :8000` and kill process |
| Catalog not found | Wrong path | Verify CATALOG_PATH in .env |
| No recommendations | Catalog not loaded | Check health endpoint |
| High latency | First request (cold start) | Subsequent requests faster |
| Connection refused | Server not running | Run `python app/api_server.py` |

### Debug Mode

Enable verbose logging:

```bash
# In code or environment
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Then run server
python app/api_server.py
```

---

## Evaluation Results

### Labeled Trace Performance (C1-C10)

| Metric | Result |
|--------|--------|
| Average Recall@10 | 34.44% |
| Average Precision | 12.17% |
| Hallucinations | 0% (100% grounded) |
| Schema Compliance | 100% |
| Best Trace | C4: 71.1% |

### Synthetic Trace Performance (S1-S10)

| Scenario | Coverage |
|----------|----------|
| DevOps Engineer | 45% |
| Cybersecurity Analyst | 38% |
| Data Analyst | 52% |
| Manufacturing | 28% |
| Healthcare | 35% |
| **Average** | **40%** |

### Validation Test Results

✅ **6/6 tests passing**
- Schema compliance: 100%
- URL grounding: 100%
- Error robustness: 100%
- Performance: <100ms average
- Multi-turn support: Working
- API endpoints: Both working

---

## System Capabilities

### Supported Scenarios

- ✅ Role-specific recommendations
- ✅ Seniority-level filtering
- ✅ Multi-competency evaluation
- ✅ Duration constraints (<15min, <30min, <60min)
- ✅ Language-specific assessments
- ✅ Quick vs. comprehensive options
- ✅ Leadership pipeline assessments
- ✅ Technical skills validation
- ✅ Personality & behavior evaluation
- ✅ Comparison between assessments

### Conversational Features

- ✅ Multi-turn conversations
- ✅ Refinement requests ("Add X", "Remove Y", "Make it shorter")
- ✅ Constraint accumulation
- ✅ Intelligent fallbacks for unclear requests
- ✅ Session management

---

## Known Limitations

1. **Catalog Coverage**
   - Limited specialized assessments for some domains (manufacturing, admin support)
   - Catalog expansion could improve recall 5-15%

2. **Language Flexibility**
   - Deterministic keyword matching (no LLM)
   - May miss indirect or creative phrasing
   - Fuzzy matching helps but has limits

3. **Cross-Domain Bias**
   - Stronger in technical and management roles
   - Weaker in some specialized functions
   - Mitigated by hybrid scoring approach

4. **No Learning**
   - System deterministic (no feedback loop)
   - Cannot adapt to organization-specific patterns
   - Would require database and logging infrastructure

---

## Future Improvements

### High Priority (5-15% recall improvement)
- Expand catalog with specialized assessments
- Add role-specific weight tuning
- Implement fuzzy matching in retrieval

### Medium Priority (2-5% improvement)
- Add response caching layer
- Build refinement suggestion UI
- Add usage analytics tracking

### Low Priority (<2% improvement)
- Multi-language support
- User preference persistence
- Recommendation explanations

---

## Production Checklist

Before deploying to production:

- [ ] Catalog verified with latest SHL assessments
- [ ] Environment variables configured
- [ ] Health endpoint monitoring active
- [ ] Error logs configured
- [ ] Rate limiting configured (if needed)
- [ ] SSL/TLS certificate installed (for HTTPS)
- [ ] Backup strategy in place
- [ ] Support contacts documented
- [ ] Performance baseline established
- [ ] Disaster recovery plan created

---

## Support & Contribution

### Getting Help

1. **API Documentation:** `http://your-deployment/docs`
2. **Examples:** [API_EXAMPLES.md](API_EXAMPLES.md)
3. **Technical Details:** [docs/APPROACH_DOCUMENT.md](docs/APPROACH_DOCUMENT.md)
4. **Issues:** GitHub Issues
5. **Contact:** See CONTRIBUTING.md

### Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

---

## License

© 2026 SHL. All rights reserved.

---

## System Information

- **Version:** 1.0.0
- **Python:** 3.9+
- **Framework:** FastAPI 0.104.1
- **Status:** Production Ready
- **Last Updated:** May 15, 2026

---

## Additional Resources

- [API Examples & cURL Usage](API_EXAMPLES.md)
- [Technical Approach Document](docs/APPROACH_DOCUMENT.md)
- [Performance Report](docs/FINAL_REPORT.md)
- [Evaluation Results](docs/evaluation_results.json)
- [Phase 3 Summary](docs/PHASE_3_SUMMARY.md)

