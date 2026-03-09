# Quick Gemini verification
import os, sys
from pathlib import Path

# Load env
p = Path('.env')
if p.exists():
    with open(p, encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

sys.path.insert(0, str(Path(__file__).parent))

print("Gemini Connection Verification")
print("=" * 50)
print(f"Model: {os.getenv('GEMINI_MODEL', 'not set')}")
print(f"API Key: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print()

try:
    from core.ai.gemini_client import is_gemini_available, get_gemini_client
    
    if is_gemini_available():
        print("[OK] Gemini client is available")
        client = get_gemini_client()
        if client:
            print(f"[OK] Client initialized: {client.model_name}")
            print("\nTesting API call (this may take a few seconds)...")
            try:
                resp = client.get_ai_response_sync(
                    user_message="Say OK",
                    user_context={"user": {"id": "test"}},
                    user_id="test"
                )
                if resp and resp.get("response"):
                    print("[SUCCESS] API call successful!")
                    print(f"Response: {resp.get('response', '')[:80]}")
                else:
                    print("[WARNING] Got response but format unexpected")
            except Exception as e:
                print(f"[ERROR] API call failed: {e}")
        else:
            print("[ERROR] Failed to create client")
    else:
        print("[ERROR] Gemini client not available")
        print("Check your API key and network connection")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
