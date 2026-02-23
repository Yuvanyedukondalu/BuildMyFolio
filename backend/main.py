"""
AI Resume & Portfolio Builder - FastAPI Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from ml_engine import ResumeAIEngine

app = FastAPI(title="AI Resume Builder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_engine = ResumeAIEngine()

# ─── Pydantic Models ───────────────────────────────────────────────────────────

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    start_year: int
    end_year: Optional[int] = None
    gpa: Optional[float] = None
    achievements: Optional[List[str]] = []

class Experience(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: Optional[str] = "Present"
    description: str
    technologies: Optional[List[str]] = []

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    impact: Optional[str] = None

class StudentProfile(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    education: List[Education]
    experience: Optional[List[Experience]] = []
    projects: List[Project]
    skills: List[str]
    certifications: Optional[List[str]] = []
    target_role: str
    target_industry: str

class GenerateRequest(BaseModel):
    profile: StudentProfile
    generate_resume: bool = True
    generate_cover_letter: bool = True
    generate_portfolio: bool = True
    job_description: Optional[str] = None
    company_name: Optional[str] = None
    tone: str = "professional"  # professional, creative, technical

class ATSRequest(BaseModel):
    resume_text: str
    job_description: str

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Resume Builder API is running!", "version": "1.0.0"}

@app.post("/api/generate")
async def generate_documents(request: GenerateRequest):
    """Generate resume, cover letter, and portfolio from student profile."""
    try:
        result = {}

        if request.generate_resume:
            result["resume"] = ai_engine.generate_resume(
                request.profile.dict(),
                request.job_description,
                request.tone
            )

        if request.generate_cover_letter and request.company_name:
            result["cover_letter"] = ai_engine.generate_cover_letter(
                request.profile.dict(),
                request.company_name,
                request.job_description,
                request.tone
            )

        if request.generate_portfolio:
            result["portfolio"] = ai_engine.generate_portfolio_content(
                request.profile.dict()
            )

        result["skills_analysis"] = ai_engine.analyze_skills(
            request.profile.dict(),
            request.job_description
        )

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ats-score")
async def ats_score(request: ATSRequest):
    """Score resume against job description for ATS compatibility."""
    try:
        score = ai_engine.calculate_ats_score(
            request.resume_text,
            request.job_description
        )
        return {"success": True, "data": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enhance-summary")
async def enhance_summary(profile: StudentProfile):
    """Generate an enhanced professional summary."""
    try:
        summary = ai_engine.generate_professional_summary(profile.dict())
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggest-skills")
async def suggest_skills(profile: StudentProfile):
    """Suggest additional relevant skills based on profile."""
    try:
        suggestions = ai_engine.suggest_skills(profile.dict())
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates")
def get_templates():
    """Get available resume templates."""
    return {
        "templates": [
            {"id": "modern", "name": "Modern", "description": "Clean, contemporary design"},
            {"id": "technical", "name": "Technical", "description": "Optimized for tech roles"},
            {"id": "creative", "name": "Creative", "description": "Bold, artistic layout"},
            {"id": "executive", "name": "Executive", "description": "Professional corporate style"},
            {"id": "minimal", "name": "Minimal", "description": "Clean and simple"},
        ]
    }

@app.post("/api/improve-bullets")
async def improve_bullets(data: dict):
    """Improve bullet points using STAR method."""
    try:
        bullets = data.get("bullets", [])
        role = data.get("role", "")
        improved = ai_engine.improve_bullet_points(bullets, role)
        return {"success": True, "improved_bullets": improved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)