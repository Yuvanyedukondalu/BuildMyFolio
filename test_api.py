#!/usr/bin/env python3
"""
API Integration Test Suite for AI Resume Builder
Tests all major endpoints with realistic sample data
"""

import json
import http.client


def test_health():
    """Test 1: Health Check"""
    print("=" * 70)
    print("TEST 1: Health Check (GET /)")
    print("=" * 70)
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=5)
    conn.request("GET", "/")
    resp = conn.getresponse()
    print(f"Status: {resp.status}")
    body = resp.read().decode()
    print(f"Response: {body}\n")
    return resp.status == 200


def test_templates():
    """Test 2: Get Templates"""
    print("=" * 70)
    print("TEST 2: Get Templates (GET /api/templates)")
    print("=" * 70)
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=5)
    conn.request("GET", "/api/templates")
    resp = conn.getresponse()
    print(f"Status: {resp.status}")
    body = resp.read().decode()
    templates = json.loads(body)
    print(json.dumps(templates, indent=2))
    print()
    return resp.status == 200


def test_generate():
    """Test 3: Generate Documents"""
    print("=" * 70)
    print("TEST 3: Generate Documents (POST /api/generate)")
    print("=" * 70)

    payload = {
        "profile": {
            "name": "Priya Sharma",
            "email": "priya@example.com",
            "phone": "+91-9876543210",
            "location": "Bangalore, India",
            "linkedin": "https://linkedin.com/in/priyasharma",
            "github": "https://github.com/priyasharma",
            "website": "https://priya-portfolio.dev",
            "summary": "Full-stack developer passionate about building scalable systems",
            "skills": [
                "Python",
                "React",
                "FastAPI",
                "Docker",
                "PostgreSQL",
                "Machine Learning",
                "TypeScript",
                "AWS",
            ],
            "education": [
                {
                    "institution": "IIT Hyderabad",
                    "degree": "B.Tech",
                    "field": "Computer Science",
                    "start_year": 2021,
                    "end_year": 2025,
                    "gpa": 8.5,
                    "achievements": ["Merit scholarship", "Best Project Award"],
                }
            ],
            "experience": [
                {
                    "company": "TechStartup Inc",
                    "role": "Software Engineer Intern",
                    "start_date": "2024-06-01",
                    "end_date": "2024-08-31",
                    "description": "Built REST APIs using FastAPI. Optimized database queries resulting in 40% latency reduction. Deployed microservices to Kubernetes.",
                    "technologies": [
                        "Python",
                        "FastAPI",
                        "PostgreSQL",
                        "Docker",
                        "Kubernetes",
                    ],
                }
            ],
            "projects": [
                {
                    "name": "SmartResume AI",
                    "description": "AI-powered resume builder using NLP and machine learning techniques for keyword extraction and optimization",
                    "technologies": [
                        "Python",
                        "React",
                        "TensorFlow",
                        "FastAPI",
                        "PostgreSQL",
                    ],
                    "github_url": "https://github.com/priyasharma/smartresume-ai",
                    "impact": "Achieved 85% ATS match accuracy on test resumes",
                },
                {
                    "name": "Real-time Analytics Dashboard",
                    "description": "Built real-time data dashboard using React and WebSockets",
                    "technologies": ["React", "Node.js", "WebSocket", "MongoDB"],
                    "live_url": "https://analytics-demo.example.com",
                },
            ],
            "certifications": [
                "AWS Solutions Architect",
                "TensorFlow Developer Certificate",
            ],
            "target_role": "Full Stack Developer",
            "target_industry": "technology",
        },
        "generate_resume": True,
        "generate_cover_letter": True,
        "generate_portfolio": True,
        "job_description": "We seek a Full Stack Developer with expertise in Python, React, Docker. Experience with machine learning is a plus.",
        "company_name": "Google",
        "tone": "professional",
    }

    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload)

    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=30)
    conn.request("POST", "/api/generate", body, headers)
    resp = conn.getresponse()
    print(f"Status: {resp.status}")
    result = json.loads(resp.read().decode())

    # Print resume summary
    if "data" in result and "resume" in result["data"]:
        resume = result["data"]["resume"]
        print(f"\n✅ Resume Generated:")
        print(f"   Name: {resume['header']['name']}")
        print(f"   Target: {resume['metadata']['target_role']}")
        print(f"   Summary: {resume['summary'][:120]}...")
        print(f"   Skills categories: {len(resume['skills'])} found")
        print(f"   ATS keywords used: {resume['ats_keywords_used'][:5]}")

    # Print cover letter summary
    if "data" in result and "cover_letter" in result["data"]:
        cl = result["data"]["cover_letter"]
        print(f"\n✅ Cover Letter Generated:")
        print(f"   Recipient: {cl['recipient']}")
        print(f"   Subject: {cl['subject']}")
        print(f"   Word count: {cl['word_count']}")

    # Print portfolio summary
    if "data" in result and "portfolio" in result["data"]:
        portfolio = result["data"]["portfolio"]
        print(f"\n✅ Portfolio Generated:")
        print(f"   Featured projects: {len(portfolio['featured_projects'])}")
        print(f"   Stats: {portfolio['stats']}")

    # Print skills analysis
    if "data" in result and "skills_analysis" in result["data"]:
        analysis = result["data"]["skills_analysis"]
        print(f"\n✅ Skills Analysis:")
        print(f"   Match %: {analysis['match_percentage']}%")
        print(f"   Matching skills: {analysis['matching_skills']}")
        print(f"   Gaps: {analysis['skill_gaps'][:3]}")

    print()
    return resp.status == 200


def test_ats_score():
    """Test 4: ATS Score"""
    print("=" * 70)
    print("TEST 4: ATS Score (POST /api/ats-score)")
    print("=" * 70)

    resume_text = """
Priya Sharma
priya@example.com | +91-9876543210 | Bangalore, India
GitHub: github.com/priyasharma | LinkedIn: linkedin.com/in/priyasharma

SUMMARY
Full-stack software engineer with expertise in Python, React, FastAPI, and Machine Learning. 
Built and deployed 5+ production systems. Strong problem-solver with proven track record.

EXPERIENCE
Software Engineer Intern, TechStartup Inc (Jun 2024 - Aug 2024)
- Built REST APIs using FastAPI resulting in 40% latency improvement
- Deployed microservices to Kubernetes cluster
- Optimized database queries using PostgreSQL indexing

PROJECTS
SmartResume AI: AI-powered resume builder using TensorFlow and React (85% ATS accuracy)
Real-time Analytics Dashboard: Real-time data visualization using React and WebSockets

SKILLS
Languages: Python, JavaScript, TypeScript
Frameworks: React, FastAPI, Django
Databases: PostgreSQL, MongoDB
Tools & Platforms: Docker, Kubernetes, AWS, Git
"""

    ats_payload = {
        "resume_text": resume_text,
        "job_description": "We seek a Full Stack Developer with expertise in Python, React, Docker, and Machine Learning knowledge a plus.",
    }

    headers = {"Content-Type": "application/json"}
    ats_body = json.dumps(ats_payload)
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=10)
    conn.request("POST", "/api/ats-score", ats_body, headers)
    resp = conn.getresponse()
    print(f"Status: {resp.status}")
    ats_result = json.loads(resp.read().decode())

    if "data" in ats_result:
        score_data = ats_result["data"]
        print(f"\n✅ ATS Analysis Results:")
        print(f"   Overall Score: {score_data['overall_score']}/100")
        print(f"   Keyword Match: {score_data['breakdown']['keyword_match']}/100")
        print(f"   Format Score: {score_data['breakdown']['format_score']}/100")
        print(f"   Action Verbs: {score_data['breakdown']['action_verbs']}/100")
        print(f"   Matched Keywords: {score_data['matched_keywords'][:5]}")
        print(f"   Recommendations: {score_data['recommendations'][:2]}")

    print()
    return resp.status == 200


if __name__ == "__main__":
    results = []

    results.append(("Health Check", test_health()))
    results.append(("Templates", test_templates()))
    results.append(("Generate", test_generate()))
    results.append(("ATS Score", test_ats_score()))

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {name}")

    all_passed = all(r[1] for r in results)
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
