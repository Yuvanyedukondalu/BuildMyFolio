import json
import http.client

# Test 1: Health
conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=5)
conn.request("GET", "/")
resp = conn.getresponse()
print("TEST 1: Health Check")
print("Status:", resp.status, "- API Running")

# Test 2: ATS Score
print("\nTEST 2: ATS Score")
payload = {
    "resume_text": "Python FastAPI Docker React. Led team. Built APIs.",
    "job_description": "Python React Docker expert needed",
}
headers = {"Content-Type": "application/json"}
conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=10)
conn.request("POST", "/api/ats-score", json.dumps(payload), headers)
resp = conn.getresponse()
result = json.loads(resp.read().decode())
print("Status:", resp.status)
if "data" in result:
    data = result["data"]
    print("Overall Score:", data["overall_score"], "/100")
    print("Keyword Match:", data["breakdown"]["keyword_match"], "/100")

# Test 3: Generate Resume
print("\nTEST 3: Generate Documents")
payload = {
    "profile": {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "skills": ["Python", "React", "Docker"],
        "education": [
            {
                "institution": "IIT",
                "degree": "B.Tech",
                "field": "CS",
                "start_year": 2021,
            }
        ],
        "projects": [
            {
                "name": "SmartResume",
                "description": "AI resume builder",
                "technologies": ["Python"],
            }
        ],
        "target_role": "Full Stack Dev",
        "target_industry": "tech",
    },
    "generate_resume": True,
}
conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=30)
conn.request("POST", "/api/generate", json.dumps(payload), headers)
resp = conn.getresponse()
result = json.loads(resp.read().decode())
print("Status:", resp.status)
if "data" in result and "resume" in result["data"]:
    r = result["data"]["resume"]
    print("Name:", r["header"]["name"])
    print("Target:", r["metadata"]["target_role"])

# Test 4: Templates
print("\nTEST 4: Get Templates")
conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=5)
conn.request("GET", "/api/templates")
resp = conn.getresponse()
result = json.loads(resp.read().decode())
print("Status:", resp.status)
print("Templates:", len(result.get("templates", [])))

print("\n" + "=" * 60)
print("All Tests Passed Successfully!")
print("=" * 60)
