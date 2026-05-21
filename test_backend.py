#!/usr/bin/env python3
"""
Quick test script for FarmFusion Backend
Run this to verify all endpoints are working
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"


def test_endpoint(name, method, endpoint, data=None, params=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            print(f"✅ {name}: OK")
            return response.json()
        else:
            print(f"❌ {name}: Failed ({response.status_code})")
            return None
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return None


def main():
    print("🧪 Testing FarmFusion Backend...\n")

    # Test 1: Health Check
    print("1️⃣ Testing Health Endpoint...")
    result = test_endpoint("Health", "GET", "/health")
    if not result:
        print("\n⚠️  Backend is not running! Start it with: python main.py")
        sys.exit(1)
    print(f"   Status: {result.get('status')}\n")

    # Test 2: Crop Recommendation
    print("2️⃣ Testing Crop Recommendation...")
    crop_data = {
        "location": "Mumbai, India",
        "soil_type": "loamy",
        "rainfall_mm": 1200,
        "temperature_c": 30,
        "farm_size_acres": 2.5
    }
    result = test_endpoint("Crop API", "POST", "/crop/recommend", data=crop_data)
    if result:
        print(f"   AI Insights: {result.get('ai_insights', 'N/A')[:100]}...")
        recs = result.get('recommendations', [])
        print(f"   Recommendations: {len(recs)} crops")
        for rec in recs[:2]:
            print(f"      - {rec.get('crop_name')}: {rec.get('confidence_score', 0)*100:.0f}% confidence")
    print()

    # Test 3: Market Prices
    print("3️⃣ Testing Market Prices...")
    result = test_endpoint("Market API", "GET", "/market/prices", params={"region": "India"})
    if result:
        prices = result.get('data', [])
        print(f"   Found {len(prices)} crops")
        for price in prices[:3]:
            print(f"      - {price.get('crop')}: ₹{price.get('price_per_kg')}")
    print()

    # Test 4: Weather
    print("4️⃣ Testing Weather API...")
    result = test_endpoint("Weather API", "GET", "/weather/current", params={"lat": 19.076, "lon": 72.877})
    if result:
        data = result.get('data', {})
        print(f"   Location: {data.get('location')}")
        print(f"   Temperature: {data.get('temperature_c')}°C")
        print(f"   Weather: {data.get('weather')}")
    print()

    # Test 5: Disease Info
    print("5️⃣ Testing Disease API...")
    result = test_endpoint("Disease API", "GET", "/disease/info/rice_blast")
    if result:
        data = result.get('data', {})
        print(f"   Disease: {data.get('name')}")
        print(f"   Severity: {data.get('severity')}")
    print()

    # Test 6: API Docs
    print("6️⃣ Testing API Documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI: Available at http://localhost:8000/docs")
        else:
            print("❌ Swagger UI: Not available")
    except Exception as e:
        print(f"❌ Swagger UI: Error - {e}")
    print()

    print("=" * 50)
    print("✅ Backend test complete!")
    print("=" * 50)
    print("\n📱 Next steps:")
    print("   1. Open Android Studio")
    print("   2. Run the frontend app")
    print("   3. Test Crop Recommendation screen")
    print("\n📚 API Documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
