# SHL Recommender API - Usage Examples

This document provides practical examples for using the SHL Recommender REST API.

## Deployment URL

Once deployed, the API will be available at:
```
https://your-deployment-url/
```

API documentation is automatically available at:
```
https://your-deployment-url/docs
```

---

## 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Check if the service is running and catalog is loaded.

**cURL Example:**
```bash
curl -X GET "https://your-deployment-url/health"
```

**Response (Success):**
```json
{
  "status": "ok",
  "timestamp": "2026-05-15T14:50:00Z",
  "catalog_size": 377,
  "service_ready": true
}
```

**Response (Degraded):**
```json
{
  "status": "degraded",
  "timestamp": "2026-05-15T14:50:00Z",
  "catalog_size": 0,
  "service_ready": false
}
```

---

## 2. Basic Recommendation Request

**Endpoint:** `POST /chat`

**Purpose:** Get assessment recommendations for a hiring scenario.

**Basic cURL Example:**
```bash
curl -X POST "https://your-deployment-url/chat" \
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
  "reply": "I can help you find leadership assessments. Based on your requirements for a senior manager role, I recommend these assessments.",
  "recommendations": [
    {
      "name": "OPQ32r",
      "url": "https://example.com/assessments/opq32r",
      "test_type": "Personality & Behavior"
    },
    {
      "name": "Hogan HPI",
      "url": "https://example.com/assessments/hogan-hpi",
      "test_type": "Personality & Behavior"
    },
    {
      "name": "WAVE",
      "url": "https://example.com/assessments/wave",
      "test_type": "Leadership & Potential"
    }
  ],
  "end_of_conversation": false,
  "request_id": "req_abc123",
  "timestamp": "2026-05-15T14:51:00Z"
}
```

---

## 3. Engineering Role Recommendation

**cURL Example:**
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "We are hiring a senior backend engineer. Looking for technical skills and problem-solving abilities."
      }
    ]
  }'
```

**Expected Response Format:**
- Assessment recommendations focused on technical skills
- Likely includes: Verify G+, logical reasoning tests, technical assessments
- Multiple options for different assessment depths

---

## 4. Refinement Example - Adding Assessment Type

**Multi-turn Conversation:**

First message:
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Middle management role for a manufacturing company"
      }
    ],
    "session_id": "session_001"
  }'
```

Follow-up refinement:
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Middle management role for a manufacturing company"
      },
      {
        "role": "assistant",
        "content": "I found several assessments..."
      },
      {
        "role": "user",
        "content": "Add a personality assessment to the recommendations"
      }
    ],
    "session_id": "session_001"
  }'
```

---

## 5. Duration Filtering Example

**Request:** Find quick assessments
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "We need a quick assessment - under 30 minutes - for initial screening"
      }
    ]
  }'
```

---

## 6. Comparison Request Example

**Request:** Compare similar assessments
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Compare OPQ32r with the Hogan assessments"
      }
    ]
  }'
```

---

## 7. Error Handling Examples

### Invalid Message Content
**Request:**
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": []
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "messages"],
      "msg": "ensure this value has at least 1 items"
    }
  ]
}
```

### Missing Required Field
**Request:**
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user"
      }
    ]
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "messages", 0, "content"],
      "msg": "field required"
    }
  ]
}
```

### Empty Content
**Request:**
```bash
curl -X POST "https://your-deployment-url/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": ""
      }
    ]
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "messages", 0, "content"],
      "msg": "ensure this value has at least 1 characters"
    }
  ]
}
```

---

## 8. Python Client Example

**Using requests library:**
```python
import requests
import json

BASE_URL = "https://your-deployment-url"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(f"Service Status: {response.json()['status']}")

# Get recommendations
payload = {
    "messages": [
        {
            "role": "user",
            "content": "Senior manager role requiring leadership skills"
        }
    ],
    "session_id": "session_123"
}

response = requests.post(f"{BASE_URL}/chat", json=payload)
data = response.json()

print(f"Reply: {data['reply']}")
print(f"Recommendations: {len(data['recommendations'])}")

for rec in data['recommendations'][:3]:
    print(f"  - {rec['name']} ({rec['test_type']})")
```

---

## 9. JavaScript Client Example

**Using fetch API:**
```javascript
const BASE_URL = "https://your-deployment-url";

// Health check
fetch(`${BASE_URL}/health`)
  .then(r => r.json())
  .then(data => console.log(`Service: ${data.status}`));

// Get recommendations
const payload = {
  messages: [
    {
      role: "user",
      content: "We need technical assessments for a software engineer"
    }
  ]
};

fetch(`${BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
})
  .then(r => r.json())
  .then(data => {
    console.log(`Reply: ${data.reply}`);
    console.log(`Recommendations: ${data.recommendations.length}`);
    data.recommendations.forEach(rec => {
      console.log(`  - ${rec.name} (${rec.test_type})`);
    });
  });
```

---

## 10. Response Schema Reference

All responses follow this schema:

**Chat Response:**
```json
{
  "reply": "string (1-5000 chars) - Natural language response",
  "recommendations": [
    {
      "name": "string - Assessment name",
      "url": "string - Assessment URL",
      "test_type": "string - Assessment category"
    }
  ],
  "end_of_conversation": "boolean - Whether conversation has concluded",
  "request_id": "string - Unique request identifier",
  "timestamp": "string - ISO 8601 timestamp"
}
```

**Health Response:**
```json
{
  "status": "string - 'ok' or 'degraded'",
  "timestamp": "string - ISO 8601 timestamp",
  "catalog_size": "integer - Number of assessments loaded",
  "service_ready": "boolean - Service operational status"
}
```

---

## Request Limits & Constraints

- **Maximum message content length:** 10,000 characters
- **Maximum number of messages:** 100
- **Supported roles:** "user", "assistant"
- **Response timeout:** 30 seconds
- **Request rate:** No strict limits (implement client-side throttling)

---

## Common Use Cases

### 1. Initial Screening Assessments
```json
{
  "messages": [
    {
      "role": "user",
      "content": "We need 2-3 quick assessments for initial candidate screening. Looking for something under 20 minutes."
    }
  ]
}
```

### 2. Competency Validation
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Software engineer role - we want to validate problem-solving, technical knowledge, and logical reasoning"
    }
  ]
}
```

### 3. Leadership Development
```json
{
    "messages": [
      {
        "role": "user",
        "content": "We're looking for leadership potential assessments for our high-potential talent program"
      }
    ]
}
```

### 4. Role Comparison
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the difference between assessing a team lead vs a department manager?"
    }
  ]
}
```

---

## Troubleshooting

### 400 Bad Request
- Verify JSON format is correct
- Ensure all required fields are present
- Check that message content is not empty

### 500 Internal Server Error
- Service may be starting up
- Check `/health` endpoint
- Retry after 5 seconds
- Contact support if issue persists

### Empty Recommendations  
- May indicate no matching assessments found
- Try rephrasing the request
- Service may still be initializing catalog

### High Latency
- Normal warm-up period: first request ~3-5 seconds
- Subsequent requests: typically <200ms
- Check service status at `/health`

---

## Rate Limiting & Best Practices

1. **Client-side throttling:** Implement 1-2 second delays between requests
2. **Session management:** Use session_id to maintain conversation context
3. **Error handling:** Implement exponential backoff for retries
4. **Caching:** Cache health status (refresh every 60 seconds)
5. **Timeout:** Set client timeout to 60 seconds

---

## Support & Documentation

- API Docs: `https://your-deployment-url/docs`
- OpenAPI Schema: `https://your-deployment-url/openapi.json`
- GitHub Repository: See main README
- Issue Tracking: Use GitHub Issues

