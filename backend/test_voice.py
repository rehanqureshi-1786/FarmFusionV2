"""
Test Script for FarmFusion Voice Assistant

This script tests the voice assistant endpoints to make sure everything is working.
Run this after starting the server: python main.py

Usage:
    python test_voice.py

Requirements:
    - Server must be running at http://localhost:8000
    - Groq API key must be configured in .env
"""
import requests
import json
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test queries in different languages
TEST_QUERIES = [
    {
        "name": "Hindi - Mandi Price",
        "payload": {
            "query": "गेहूं का रेट क्या है",
            "location": "Madhya Pradesh"
        }
    },
    {
        "name": "Hinglish - Weather",
        "payload": {
            "query": "mausam kaisa hai",
            "location": "Punjab"
        }
    },
    {
        "name": "English - Weather",
        "payload": {
            "query": "what's the weather today?",
            "location": "Mumbai"
        }
    },
    {
        "name": "Hinglish - Crop Prediction",
        "payload": {
            "query": "konsi fasal lagau"
        }
    },
    {
        "name": "Hindi - Disease Detection",
        "payload": {
            "query": "पत्ते पीले हो रहे हैं"
        }
    },
    {
        "name": "English - Mandi Price",
        "payload": {
            "query": "what is the price of wheat?"
        }
    },
    {
        "name": "Hinglish - General Query",
        "payload": {
            "query": "khad kaise dale"
        }
    },
    {
        "name": "Hindi - Weather Forecast",
        "payload": {
            "query": "कल बारिश होगी क्या"
        }
    }
]


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_separator():
    """Print a separator line"""
    print("-" * 70)


def test_health_endpoint():
    """Test the health check endpoint"""
    print_header("Testing Health Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/voice/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"✅ Service: {data.get('service', 'unknown')}")
            print(f"✅ Features: {', '.join(data.get('features', {}).keys())}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Make sure the server is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_voice_endpoint(query_info):
    """Test a single voice query"""
    name = query_info["name"]
    payload = query_info["payload"]

    print(f"\n📝 Testing: {name}")
    print(f"   Query: {payload['query']}")
    print(f"   Location: {payload.get('location', 'auto')}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/voice",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            print(f"\n   ✅ SUCCESS!")
            print(f"   Intent: {data.get('intent')}")
            print(f"   Action: {data.get('action')}")
            print(f"   Language: {data.get('detected_language')}")
            print(f"   Confidence: {data.get('confidence', 0):.2f}")
            print(f"   Response: {data.get('response', 'N/A')[:100]}...")

            return True
        else:
            print(f"\n   ❌ FAILED: HTTP {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n   ❌ TIMEOUT: Request took too long")
        return False
    except Exception as e:
        print(f"\n   ❌ ERROR: {str(e)}")
        return False


def test_intent_detection():
    """Test the intent-only endpoint"""
    print_header("Testing Intent Detection Only")

    test_query = {
        "query": "gehu ka rate kya hai",
        "location": "Punjab"
    }

    print(f"Query: {test_query['query']}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/voice/intent-only",
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Intent Detection Successful!")
            print(f"   Intent: {data.get('intent')}")
            print(f"   Crop: {data.get('crop')}")
            print(f"   Language: {data.get('language')}")
            print(f"   Confidence: {data.get('confidence', 0):.2f}")
            return True
        else:
            print(f"\n❌ Failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_languages_endpoint():
    """Test the languages endpoint"""
    print_header("Testing Languages Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/voice/languages", timeout=5)

        if response.status_code == 200:
            data = response.json()
            languages = data.get('languages', [])
            print(f"✅ Found {len(languages)} supported languages:")
            for lang in languages:
                print(f"   - {lang['name']} ({lang['code']})")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_intents_endpoint():
    """Test the intents endpoint"""
    print_header("Testing Intents Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/voice/intents", timeout=5)

        if response.status_code == 200:
            data = response.json()
            intents = data.get('intents', [])
            print(f"✅ Found {len(intents)} supported intents:")
            for intent in intents:
                print(f"   - {intent['name']} ({intent['code']})")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║           FarmFusion Voice Assistant Test Suite                  ║
    ║                                                                  ║
    ║   Make sure the server is running: python main.py                ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # Track results
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    # Test 1: Health Check
    if test_health_endpoint():
        results["passed"] += 1
        results["tests"].append(("Health Check", "✅"))
    else:
        results["failed"] += 1
        results["tests"].append(("Health Check", "❌"))
        print("\n⚠️  Health check failed. Make sure the server is running!")
        print(f"   Start with: python main.py")
        return results

    # Test 2: Languages Endpoint
    if test_languages_endpoint():
        results["passed"] += 1
        results["tests"].append(("Languages Endpoint", "✅"))
    else:
        results["failed"] += 1
        results["tests"].append(("Languages Endpoint", "❌"))

    # Test 3: Intents Endpoint
    if test_intents_endpoint():
        results["passed"] += 1
        results["tests"].append(("Intents Endpoint", "✅"))
    else:
        results["failed"] += 1
        results["tests"].append(("Intents Endpoint", "❌"))

    # Test 4: Intent Detection Only
    if test_intent_detection():
        results["passed"] += 1
        results["tests"].append(("Intent Detection", "✅"))
    else:
        results["failed"] += 1
        results["tests"].append(("Intent Detection", "❌"))

    # Test 5+: Voice Queries
    print_header("Testing Voice Queries")

    for query_info in TEST_QUERIES:
        if test_voice_endpoint(query_info):
            results["passed"] += 1
            results["tests"].append((query_info["name"], "✅"))
        else:
            results["failed"] += 1
            results["tests"].append((query_info["name"], "❌"))

    return results


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    for test_name, status in results["tests"]:
        print(f"  {status} {test_name}")

    print_separator()
    print(f"  Total: {results['passed'] + results['failed']} tests")
    print(f"  ✅ Passed: {results['passed']}")
    print(f"  ❌ Failed: {results['failed']}")

    if results["failed"] == 0:
        print("\n  🎉 All tests passed!")
    else:
        print(f"\n  ⚠️  {results['failed']} test(s) failed")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        results = run_all_tests()
        print_summary(results)

        # Exit with appropriate code
        sys.exit(0 if results["failed"] == 0 else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
