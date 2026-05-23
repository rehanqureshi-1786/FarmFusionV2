"""
AI Setup Checker for FarmFusion Disease Detection.

Run this script to verify your AI configuration is correct.

Usage:
    python check_ai_setup.py
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))


def get_effective_env_value(key_name: str) -> str:
    """Return the last non-comment value for a key from backend/.env."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return ""

    value = ""
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or not line.startswith(f"{key_name}="):
            continue
        value = line.split("=", 1)[1].strip()
    return value


def check_env_file() -> bool:
    """Check if .env file exists and has required keys."""
    print("=" * 60)
    print("CHECKING .env FILE")
    print("=" * 60)

    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("[FAIL] .env file not found")
        print(f"   Expected at: {env_path}")
        return False

    print(f"[OK] .env file found at: {env_path}")

    key = get_effective_env_value("GEMINI_API_KEY")
    if not key:
        print("[FAIL] GEMINI_API_KEY not found in .env")
        return False

    if key and key not in {"your_gemini_api_key_here", "your_gemini_api_key"}:
        print("[OK] GEMINI_API_KEY is set")
        print(f"   Key length: {len(key)} characters")
        print(f"   Key preview: {key[:10]}...")
        return True

    print("[FAIL] GEMINI_API_KEY is empty or still a placeholder")
    return False


def check_gemini_library() -> bool:
    """Check if Google Generative AI library is installed."""
    print("\n" + "=" * 60)
    print("CHECKING GEMINI LIBRARY")
    print("=" * 60)

    try:
        import google.generativeai  # noqa: F401

        print("[OK] google.generativeai library is installed")
        return True
    except ImportError:
        print("[FAIL] google.generativeai library is NOT installed")
        print("   Install it with: pip install google-generative-ai")
        return False


def check_gemini_client() -> bool:
    """Check if Gemini client can be initialized."""
    print("\n" + "=" * 60)
    print("CHECKING GEMINI CLIENT")
    print("=" * 60)

    try:
        import google.generativeai as genai

        api_key = get_effective_env_value("GEMINI_API_KEY")
        if not api_key or api_key in {"your_gemini_api_key_here", "your_gemini_api_key"}:
            print("[FAIL] Gemini client is NOT available")
            print("   GEMINI_API_KEY is missing or still a placeholder")
            return False

        genai.configure(api_key=api_key)
        model_name = "gemini-1.5-flash"
        genai.GenerativeModel(model_name)
        print("[OK] Gemini client is available")
        print(f"   Model: {model_name}")
        print("   API Key present: True")
        return True
    except Exception as exc:
        print(f"[FAIL] Error initializing Gemini client: {exc}")
        return False


def print_fix_instructions() -> None:
    """Print instructions to fix issues."""
    print("\n" + "=" * 60)
    print("HOW TO FIX")
    print("=" * 60)
    print(
        """
1. Get a Gemini API key:
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key

2. Add the key to backend/.env:
   GEMINI_API_KEY=your_actual_key_here

3. Install the required library if needed:
   pip install google-generative-ai

4. Restart the backend server:
   python main.py

5. Test again:
   python check_ai_setup.py
        """.strip()
    )


def main() -> bool:
    print(
        """
============================================================
         FarmFusion Disease AI Setup Checker
============================================================
        """.strip()
    )

    env_ok = check_env_file()
    lib_ok = check_gemini_library()
    client_ok = check_gemini_client()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    results = [
        (".env file configured", env_ok),
        ("Gemini library installed", lib_ok),
        ("Gemini client working", client_ok),
    ]

    for name, status in results:
        symbol = "[OK]" if status else "[FAIL]"
        print(f"{symbol} {name}")

    if all(status for _, status in results):
        print("\n" + "=" * 60)
        print("ALL CHECKS PASSED")
        print("=" * 60)
        print("\nYour disease detection AI is ready to use.")
        print("Upload an image from the Android app and it will be analyzed by Gemini.")
        print("Watch the backend console to see detailed logs.")
        return True

    print("\n" + "=" * 60)
    print("SETUP INCOMPLETE")
    print("=" * 60)
    print_fix_instructions()
    return False


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
