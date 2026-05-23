"""
Test script for Disease Detection AI

This script tests if the Gemini Vision API is properly configured and working.

Usage:
    python test_disease_ai.py

Requirements:
    - Backend server should be running
    - GEMINI_API_KEY must be set in .env file
"""
import asyncio
import sys
from app.agents.gemini_client import gemini_client
from app.agents.disease_agent import disease_agent
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_gemini_availability():
    """Test if Gemini API is configured"""
    print("\n" + "="*60)
    print("TEST 1: Checking Gemini API Availability")
    print("="*60)

    is_available = gemini_client.is_available()
    print(f"Gemini Available: {is_available}")

    if not is_available:
        print("\n❌ GEMINI API IS NOT AVAILABLE")
        print("\nPossible reasons:")
        print("1. GEMINI_API_KEY not set in .env file")
        print("2. google.generativeai library not installed")
        print("3. Invalid API key")
        print("\nTo fix:")
        print("1. Add GEMINI_API_KEY=your_key to backend/.env")
        print("2. Get a key at: https://makersuite.google.com/app/apikey")
        print("3. Install library: pip install google-generative-ai")
        return False

    print("\n✅ GEMINI API IS CONFIGURED")
    print(f"Model: {gemini_client.model_name}")
    return True


async def test_disease_detection_with_sample():
    """Test disease detection with a sample image"""
    print("\n" + "="*60)
    print("TEST 2: Testing Disease Detection")
    print("="*60)

    # Create a simple test image (small colored squares)
    # This is just for testing the API connectivity
    from PIL import Image, ImageDraw
    import io

    print("Creating test image...")
    img = Image.new('RGB', (100, 100), color='green')
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill='brown')

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    image_data = img_bytes.getvalue()

    print(f"Test image size: {len(image_data)} bytes")

    # Test detection
    print("\nCalling disease detection...")
    result = await disease_agent.detect_disease(
        image_data=image_data,
        crop_type="tomato",
        user_id="test_user"
    )

    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    print(f"Disease Name: {result.get('disease_name')}")
    print(f"Confidence: {result.get('confidence')}")
    print(f"Severity: {result.get('severity')}")
    print(f"Source: {result.get('source')}")
    print(f"AI Analyzed: {result.get('ai_analyzed')}")

    if result.get('error'):
        print(f"\n❌ ERROR: {result.get('error')}")
        return False

    if result.get('ai_analyzed'):
        print("\n✅ SUCCESS: AI actually analyzed the image!")
        print(f"\nDescription: {result.get('description', 'N/A')[:100]}...")
        return True
    else:
        print("\n⚠️ WARNING: Analysis was NOT performed by AI")
        print(f"Source indicates: {result.get('source')}")
        return False


async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        FarmFusion Disease Detection AI Test Suite            ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Check availability
    gemini_ok = await test_gemini_availability()

    if not gemini_ok:
        print("\n" + "="*60)
        print("ABORTING: Gemini API is not configured")
        print("="*60)
        sys.exit(1)

    # Test 2: Try detection
    detection_ok = await test_disease_detection_with_sample()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Gemini API Configured: {'✅ YES' if gemini_ok else '❌ NO'}")
    print(f"AI Analysis Working: {'✅ YES' if detection_ok else '❌ NO'}")

    if detection_ok:
        print("\n🎉 Disease detection is working correctly!")
    else:
        print("\n⚠️ Disease detection needs configuration")
        print("\nNext steps:")
        print("1. Check backend console for detailed logs")
        print("2. Verify GEMINI_API_KEY is valid")
        print("3. Restart the server: python main.py")

    return detection_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
