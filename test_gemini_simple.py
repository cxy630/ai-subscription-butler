# -*- coding: utf-8 -*-
"""测试Gemini模型连接"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载.env
env_path = project_root / '.env'
if env_path.exists():
    print("Loading .env file...")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

print("=" * 60)
print("Gemini Model Connection Test")
print("=" * 60)
print()

api_key = os.getenv('GEMINI_API_KEY', '')
model_name = os.getenv('GEMINI_MODEL', 'gemini-3-flash')

print("Configuration:")
print(f"  Model: {model_name}")
print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: NOT SET")
print()

if not api_key:
    print("ERROR: GEMINI_API_KEY not set")
    sys.exit(1)

print("Step 1: Importing Gemini client...")
try:
    from core.ai.gemini_client import get_gemini_client, is_gemini_available
    print("  OK: Module imported")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

print("\nStep 2: Checking client availability...")
if not is_gemini_available():
    print("  ERROR: Client not available")
    sys.exit(1)
print("  OK: Client available")

print("\nStep 3: Initializing client...")
try:
    client = get_gemini_client()
    if client is None:
        print("  ERROR: Failed to create client")
        sys.exit(1)
    print(f"  OK: Client initialized (model: {client.model_name})")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

print("\nStep 4: Sending test request...")
print(f"  Message: 'Hello, please reply OK'")
print(f"  Model: {model_name}")
print()

try:
    response = client.get_ai_response_sync(
        user_message="Hello, please reply OK",
        user_context={"user": {"id": "test_user"}},
        user_id="test_user"
    )
    
    if response and response.get("response"):
        print("=" * 60)
        print("SUCCESS: Connection test passed!")
        print("=" * 60)
        print()
        print("Model Response:")
        print("-" * 60)
        print(response.get("response", ""))
        print("-" * 60)
        print()
        print("Response Details:")
        print(f"  Intent: {response.get('intent', 'N/A')}")
        print(f"  Confidence: {response.get('confidence', 'N/A')}")
        print(f"  Model: {response.get('model', 'N/A')}")
        if 'tokens_used' in response:
            print(f"  Tokens: {response.get('tokens_used', 0)}")
        print()
        print("Gemini model connection is working correctly!")
    else:
        print("WARNING: Received response but format is abnormal")
        print(f"  Response: {response}")
        
except Exception as e:
    print("=" * 60)
    print("FAILED: Connection test failed")
    print("=" * 60)
    print()
    print(f"Error: {str(e)}")
    print()
    print("Possible causes:")
    print("  1. Invalid or expired API key")
    print("  2. Incorrect model name (current: " + model_name + ")")
    print("  3. Network connection issue")
    print("  4. API quota exceeded")
    print("  5. Model not available or requires special permissions")
    print()
    sys.exit(1)

print("=" * 60)
