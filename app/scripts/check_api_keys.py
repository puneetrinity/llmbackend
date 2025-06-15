# scripts/check_api_keys.py
"""Script to validate API keys"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def check_brave_api():
    """Test Brave Search API"""
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        return False, "API key not found"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
            params = {"q": "test", "count": 1}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return True, "OK"
                else:
                    return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)

async def check_bing_api():
    """Test Bing Search API"""
    api_key = os.getenv("BING_SEARCH_API_KEY")
    if not api_key:
        return False, "API key not found"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": api_key}
            params = {"q": "test", "count": 1}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return True, "OK"
                else:
                    return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)

async def check_zenrows_api():
    """Test ZenRows API"""
    api_key = os.getenv("ZENROWS_API_KEY")
    if not api_key:
        return False, "API key not found"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.zenrows.com/v1/"
            params = {
                "url": "https://httpbin.org/html",
                "apikey": api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return True, "OK"
                else:
                    return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)

async def check_ollama():
    """Test Ollama connection"""
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_host}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    return True, f"Available models: {models}"
                else:
                    return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)

async def main():
    """Check all API connections"""
    print("🔍 Checking API Keys and Connections...\n")
    
    checks = [
        ("Brave Search API", check_brave_api()),
        ("Bing Search API", check_bing_api()),
        ("ZenRows API", check_zenrows_api()),
        ("Ollama Service", check_ollama())
    ]
    
    results = await asyncio.gather(*[check[1] for check in checks])
    
    for i, (name, _) in enumerate(checks):
        success, message = results[i]
        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")
    
    all_good = all(result[0] for result in results)
    
    print(f"\n{'🎉 All APIs are working!' if all_good else '⚠️  Some APIs need attention'}")
    
    if not all_good:
        print("\n💡 Tips:")
        print("- Check your .env file for correct API keys")
        print("- Ensure Ollama is running: ollama serve")
        print("- Pull required model: ollama pull llama2:7b")

if __name__ == "__main__":
    asyncio.run(main())
