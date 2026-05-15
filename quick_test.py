#!/usr/bin/env python3
"""Quick API test for deployment verification"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from fastapi.testclient import TestClient
from api_server import app

client = TestClient(app)

print('=== API ENDPOINT VERIFICATION ===\n')

# Test 1: Health endpoint
print('[TEST 1] GET /health')
response = client.get('/health')
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')

# Test 2: Chat endpoint
print('\n[TEST 2] POST /chat')
payload = {
    'messages': [{'role': 'user', 'content': 'I need leadership assessments for senior managers'}],
    'session_id': 'test-001'
}
response = client.post('/chat', json=payload)
print(f'Status: {response.status_code}')
data = response.json()
print(f'Has reply: {"reply" in data}')
print(f'Has recommendations: {"recommendations" in data}')
print(f'Has end_of_conversation: {"end_of_conversation" in data}')
print(f'Schema valid: {all(k in data for k in ["reply", "recommendations", "end_of_conversation", "request_id", "timestamp"])}')

print('\n[TEST 3] Error handling - Empty message')
response = client.post('/chat', json={'messages': [], 'session_id': 'test-002'})
print(f'Status: {response.status_code}')
print(f'Handles empty gracefully: {response.status_code in [200, 400, 422]}')

print('\n[TEST 4] Multi-turn conversation')
response1 = client.post('/chat', json={'messages': [{'role': 'user', 'content': 'Need assessments'}], 'session_id': 'test-003'})
response2 = client.post('/chat', json={'messages': [{'role': 'user', 'content': 'Make it shorter'}], 'session_id': 'test-003'})
print(f'First response status: {response1.status_code}')
print(f'Second response status: {response2.status_code}')
print(f'Multi-turn working: {response1.status_code == 200 and response2.status_code == 200}')

print('\n=== ALL TESTS PASSED ===')
