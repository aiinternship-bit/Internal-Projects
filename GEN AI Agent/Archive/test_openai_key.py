#!/usr/bin/env python3
"""
Quick test to validate OpenAI API key
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("OPENAI API KEY TEST")
print("=" * 60)
print(f"\nKey found: {bool(api_key)}")
print(f"Key length: {len(api_key) if api_key else 0} characters")
print(f"Key starts with: {api_key[:10] if api_key else 'N/A'}...")
print(f"Key ends with: ...{api_key[-10:] if api_key else 'N/A'}")

if not api_key:
    print("\n❌ No API key found in .env file")
    exit(1)

# Check format
if not api_key.startswith("sk-"):
    print(f"\n⚠️  WARNING: Key doesn't start with 'sk-'")
    print("   Standard OpenAI keys start with 'sk-proj-' or 'sk-'")
    print("   Your key might be:")
    print("   - From the wrong service (Azure, etc.)")
    print("   - Copied incorrectly")
    print("   - Not an OpenAI API key")

# Test the key
print("\n" + "=" * 60)
print("Testing key with OpenAI API...")
print("=" * 60)

try:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("\nSending request to: https://api.openai.com/v1/models")
    response = requests.get(
        "https://api.openai.com/v1/models",
        headers=headers,
        timeout=10
    )

    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        print("\n✅ SUCCESS! Your OpenAI API key is valid!")
        models = response.json()
        print(f"Available models: {len(models.get('data', []))}")
    elif response.status_code == 401:
        print("\n❌ FAILED: 401 Unauthorized")
        print("\nThis means:")
        print("  1. The key is invalid or incorrect")
        print("  2. The key has been revoked")
        print("  3. This is not an OpenAI API key")
        print("\nResponse body:")
        print(response.text)
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")
        print("Response:")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\n❌ Network error: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
print("How to get a valid OpenAI API key:")
print("=" * 60)
print("1. Go to: https://platform.openai.com/api-keys")
print("2. Click 'Create new secret key'")
print("3. Copy the key (starts with 'sk-proj-' or 'sk-')")
print("4. Paste into .env file WITHOUT quotes")
print("   OPENAI_API_KEY=sk-proj-abc123...")
print("=" * 60)
