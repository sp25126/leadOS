import requests
import time
import json
import os

BASE_URL = "http://localhost:8000/api/leads"
# API keys are now loaded from environment variables for security
API_KEY = os.getenv("LEAD_HUNTER_API_KEY", "saumyavishwam@gmail")  # Default fallback
GMAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

def run_search(business_type, location, headers=None):
    if headers is None:
        headers = {}
    headers["X-API-Key"] = API_KEY
    headers["Content-Type"] = "application/json"
    
    payload = {
        "business_type": business_type,
        "location": location,
        "radius_km": 5,
        "target_service": "digital marketing and website development"
    }
    
    # Start task
    print(f"\n[TESTING] Searching for {business_type} in {location}...")
    resp = requests.post(f"{BASE_URL}/search", headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"FAILED TO START SEARCH: {resp.text}")
        return []
    
    task_id = resp.json().get("task_id")
    print(f"Task ID: {task_id}. Waiting for completion...")
    
    # Poll for completion
    for _ in range(30): # 5 mins
        status_resp = requests.get(f"{BASE_URL}/search/status/{task_id}", headers=headers)
        status_data = status_resp.json()
        status = status_data.get("status")
        progress = status_data.get("progress", 0)
        
        if status == "completed":
            print(f"Task completed!")
            return status_data.get("result", {}).get("leads", [])
        elif status == "error":
            print(f"Task failed: {status_data.get('error')}")
            return []
        
        print(f"  Progress: {progress}% (Status: {status})")
        time.sleep(10)
    
    print("TIMEOUT")
    return []

def test_1_junk_filter():
    leads = run_search("cafe", "Pune")
    names = [l['name'] for l in leads]
    junk_keywords = ['canteen','hostel','police station','judicial','microbiology']
    leaked = [n for n in names if any(x in n.lower() for x in junk_keywords)]
    print(f"\n--- TEST 1: Junk Filter ---")
    print(f"Total leads: {len(leads)}")
    print(f"Junk leaked through: {leaked}")
    assert len(leaked) == 0, "Test 1 Failed: Junk leaked through"

def test_2_coverage():
    headers = {"X-Google-Maps-Key": GMAPS_KEY}
    leads = run_search("cafe", "Pune", headers=headers)
    phones = sum(1 for l in leads if l.get('phone'))
    emails = sum(1 for l in leads if l.get('email') and l.get('email_quality_score', 0) >= 2)
    print(f"\n--- TEST 2: Phone + Email Coverage ---")
    print(f"Total: {len(leads)}")
    if leads:
        print(f"Phone Coverage: {phones}/{len(leads)} ({100*phones//len(leads)}%)")
        print(f"Real Email (Score >= 2): {emails}")
    else:
        print("No leads found.")

def test_3_ai_scoring():
    headers = {"X-Groq-Key": GROQ_KEY}
    leads = run_search("cafe", "Pune", headers=headers)
    scores = [l.get('score', 5) for l in leads]
    all_five = all(s == 5 for s in scores)
    unique = set(scores)
    high = sum(1 for s in scores if s >= 8)
    
    print(f"\n--- TEST 3: AI Scoring Variance ---")
    print(f"All score=5 (broken): {all_five}")
    print(f"Unique scores: {sorted(list(unique))}")
    print(f"High priority (8+): {high}/{len(leads)}")
    
    if leads:
        print("Sample Openings:")
        for l in leads[:3]:
            print(f"  Opening: {l.get('suggested_opening', '')[:80]}...")

def test_4_gym_fix():
    leads = run_search("gym", "Ahmedabad")
    types = [l.get('types', '') for l in leads]
    wrong = [t for t in types if 'sports_centre' in str(t).lower() and 'fitness' not in str(t).lower()]
    print(f"\n--- TEST 4: Gym Fix ---")
    print(f"Total: {len(leads)}")
    print(f"Wrong type (sports_centre only): {len(wrong)}")
    if leads:
        print(f"Sample names: {[l['name'] for l in leads[:5]]}")

if __name__ == "__main__":
    try:
        test_1_junk_filter()
    except Exception as e: print(f"Test 1 failed with error: {e}")
    
    try:
        test_2_coverage()
    except Exception as e: print(f"Test 2 failed with error: {e}")
    
    try:
        test_3_ai_scoring()
    except Exception as e: print(f"Test 3 failed with error: {e}")
    
    try:
        test_4_gym_fix()
    except Exception as e: print(f"Test 4 failed with error: {e}")
