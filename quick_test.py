# Quick Gemini connection test
import os
import sys
from pathlib import Path

# Load .env safely
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]

sys.path.insert(0, str(Path(__file__).parent))

print("Testing Gemini connection...")
print("Model:", os.getenv('GEMINI_MODEL', 'not set'))
print("API Key:", os.getenv('GEMINI_API_KEY', 'not set')[:20] + '...' if os.getenv('GEMINI_API_KEY') else 'not set')
print()

try:
    from core.ai.gemini_client import is_gemini_available, get_gemini_client
    
    print("Step 1: Check availability...")
    if is_gemini_available():
        print("  PASS: Gemini client is available")
    else:
        print("  FAIL: Gemini client not available")
        sys.exit(1)
    
    print("\nStep 2: Get client instance...")
    client = get_gemini_client()
    if client:
        print(f"  PASS: Client created (model: {client.model_name})")
    else:
        print("  FAIL: Could not create client")
        sys.exit(1)
    
    print("\nStep 3: Test API call...")
    print("  Sending: 'Say OK'")
    response = client.get_ai_response_sync(
        user_message="Say OK",
        user_context={"user": {"id": "test"}},
        user_id="test"
    )
    
    if response and response.get("response"):
        print("  PASS: Got response from model")
        print(f"  Response: {response.get('response', '')[:100]}")
        print("\nSUCCESS: Gemini connection is working!")
    else:
        print("  FAIL: No valid response")
        sys.exit(1)
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
