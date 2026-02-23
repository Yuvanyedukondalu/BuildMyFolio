"""
AI Resume Builder - ML Engine
Uses rule-based NLP + template generation + keyword analysis.
For production, swap prompt_builder calls to OpenAI/Gemini/Claude API.
"""

import re
import json
from typing import Dict, List, Optional, Any
from collections import Counter
import math


class ResumeAIEngine:
    """
    Core AI engine for resume and portfolio generation.
    Uses keyword analysis, NLP heuristics, and structured template generation.
    For production: integrate with OpenAI GPT-4 or Anthropic Claude API.
    """

    def __init__(self):
        self.action_verbs = {
            "leadership": ["Led", "Managed", "Directed", "Coordinated", "Supervised", "Spearheaded", "Orchestrated"],
            "development": ["Built", "Developed", "Engineered", "Architected", "Implemented", "Deployed", "Designed"],
            "achievement": ["Achieved", "Delivered", "Exceeded", "Surpassed", "Accomplished", "Attained"],
            "improvement": ["Optimized", "Enhanced", "Streamlined", "Improved", "Reduced", "Increased", "Boosted"],
            "collaboration": ["Collaborated", "Partnered", "Contributed", "Supported", "Assisted", "Facilitated"],
            "research": ["Researched", "Analyzed", "Investigated", "Evaluated", "Assessed", "Studied"],
            "communication": ["Presented", "Communicated", "Authored", "Published", "Documented", "Trained"],
        }

        self.skill_categories = {
            "languages": ["Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin", "R", "MATLAB", "PHP", "Ruby", "Scala"],
            "frameworks": ["React", "Next.js", "Vue", "Angular", "FastAPI", "Django", "Flask", "Spring", "Express", "Node.js", "TensorFlow", "PyTorch", "Scikit-learn", "Keras"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "Cassandra", "DynamoDB", "Firebase"],
            "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Terraform", "Jenkins"],
            "tools": ["Git", "GitHub", "Jira", "Figma", "VS Code", "Linux", "Bash", "REST API", "GraphQL"],
            "soft_skills": ["Problem-solving", "Communication", "Teamwork", "Leadership", "Adaptability", "Critical Thinking"],
        }

        self.industry_keywords = {
            "software": ["agile", "scrum", "microservices", "API", "scalable", "distributed", "full-stack", "backend", "frontend"],
            "data": ["machine learning", "deep learning", "data pipeline", "ETL", "analytics", "visualization", "statistical", "model"],
            "product": ["user experience", "product roadmap", "A/B testing", "metrics", "KPI", "stakeholder", "cross-functional"],
            "finance": ["financial modeling", "risk analysis", "portfolio", "quantitative", "regulatory", "compliance"],
            "marketing": ["SEO", "content strategy", "campaign", "ROI", "conversion", "analytics", "brand"],
        }

    # ─── Resume Generation ─────────────────────────────────────────────────────

    def generate_resume(self, profile: Dict, job_description: Optional[str] = None, tone: str = "professional") -> Dict:
        """Generate a structured, ATS-optimized resume."""

        # Extract keywords from job description if provided
        jd_keywords = self._extract_keywords(job_description) if job_description else []

        # Build resume sections
        resume = {
            "header": self._build_header(profile),
            "summary": self._generate_summary(profile, jd_keywords, tone),
            "skills": self._organize_skills(profile.get("skills", []), jd_keywords),
            "experience": self._enhance_experience(profile.get("experience", []), jd_keywords, tone),
            "projects": self._enhance_projects(profile.get("projects", []), jd_keywords),
            "education": self._format_education(profile.get("education", [])),
            "certifications": profile.get("certifications", []),
            "ats_keywords_used": jd_keywords[:20] if jd_keywords else [],
            "metadata": {
                "target_role": profile.get("target_role"),
                "target_industry": profile.get("target_industry"),
                "tone": tone,
            }
        }

        return resume

    def _build_header(self, profile: Dict) -> Dict:
        return {
            "name": profile.get("name", ""),
            "email": profile.get("email", ""),
            "phone": profile.get("phone", ""),
            "location": profile.get("location", ""),
            "linkedin": profile.get("linkedin", ""),
            "github": profile.get("github", ""),
            "website": profile.get("website", ""),
        }

    def _generate_summary(self, profile: Dict, keywords: List[str], tone: str) -> str:
        """Generate a tailored professional summary."""
        name = profile.get("name", "Professional")
        target_role = profile.get("target_role", "Software Developer")
        target_industry = profile.get("target_industry", "technology")
        skills = profile.get("skills", [])[:5]
        education = profile.get("education", [{}])
        degree = education[0].get("degree", "Bachelor's") if education else "Bachelor's"
        field = education[0].get("field", "Computer Science") if education else "Computer Science"
        years_exp = len(profile.get("experience", []))

        # Tone-specific openers
        openers = {
            "professional": f"Results-driven {target_role} with a {degree} in {field}",
            "creative": f"Innovative and passionate {target_role} with a {degree} in {field}",
            "technical": f"Technical {target_role} with expertise in {field} and a {degree} degree",
        }
        opener = openers.get(tone, openers["professional"])

        # Build experience clause
        if years_exp == 0:
            exp_clause = "and strong academic foundation"
        elif years_exp == 1:
            exp_clause = f"and {years_exp} year of hands-on experience"
        else:
            exp_clause = f"and {years_exp}+ years of hands-on experience"

        # Skills highlight
        skills_str = ", ".join(skills[:4]) if skills else target_industry + " technologies"

        # Match keywords from JD
        keyword_match = ""
        if keywords:
            top_kw = [k for k in keywords[:3] if k.lower() not in skills_str.lower()]
            if top_kw:
                keyword_match = f" Experienced with {', '.join(top_kw)}."

        summary = (
            f"{opener} {exp_clause} in the {target_industry} industry. "
            f"Proficient in {skills_str}, with a proven track record of delivering impactful solutions. "
            f"Seeking to leverage technical expertise and problem-solving abilities as a {target_role}.{keyword_match}"
        )

        return summary

    def _organize_skills(self, skills: List[str], jd_keywords: List[str]) -> Dict:
        """Organize and prioritize skills, highlighting JD matches."""
        categorized = {cat: [] for cat in self.skill_categories}
        categorized["other"] = []

        # Boost JD keyword skills to top
        priority_skills = []
        regular_skills = []

        for skill in skills:
            if any(kw.lower() in skill.lower() or skill.lower() in kw.lower() for kw in jd_keywords):
                priority_skills.append(skill)
            else:
                regular_skills.append(skill)

        all_skills = priority_skills + regular_skills

        for skill in all_skills:
            placed = False
            for cat, cat_skills in self.skill_categories.items():
                if any(s.lower() == skill.lower() or skill.lower() in s.lower() for s in cat_skills):
                    categorized[cat].append(skill)
                    placed = True
                    break
            if not placed:
                categorized["other"].append(skill)

        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}

    def _enhance_experience(self, experiences: List[Dict], keywords: List[str], tone: str) -> List[Dict]:
        """Enhance experience bullet points with action verbs and quantification."""
        enhanced = []
        for exp in experiences:
            enhanced_exp = exp.copy()
            description = exp.get("description", "")

            # Generate enhanced bullets
            bullets = self._generate_experience_bullets(
                description, exp.get("role", ""), exp.get("technologies", []), keywords, tone
            )
            enhanced_exp["bullets"] = bullets
            enhanced_exp["technologies_highlighted"] = [
                tech for tech in exp.get("technologies", [])
                if any(kw.lower() in tech.lower() for kw in keywords)
            ]
            enhanced.append(enhanced_exp)

        return enhanced

    def _generate_experience_bullets(self, description: str, role: str, technologies: List[str], keywords: List[str], tone: str) -> List[str]:
        """Generate STAR-format bullet points from description."""
        # Split description into sentences
        sentences = re.split(r'[.;,\n]', description)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        bullets = []
        verb_category = "development" if "develop" in role.lower() or "engineer" in role.lower() else "achievement"
        verbs = self.action_verbs.get(verb_category, self.action_verbs["development"])

        for i, sentence in enumerate(sentences[:5]):
            # Check if sentence already starts with action verb
            first_word = sentence.split()[0] if sentence.split() else ""
            already_has_verb = any(
                first_word.lower() == v.lower()
                for vlist in self.action_verbs.values()
                for v in vlist
            )

            if not already_has_verb and verbs:
                verb = verbs[i % len(verbs)]
                # Lowercase first word of original sentence
                words = sentence.split()
                if words:
                    words[0] = words[0].lower()
                    sentence = f"{verb} {' '.join(words)}"

            # Add metric suggestion if missing
            has_metric = bool(re.search(r'\d+%?|\d+x|million|thousand', sentence))
            if not has_metric and i < 2:
                sentence += " (quantify impact with metrics)"

            bullets.append(sentence)

        # If description was short, add technology bullet
        if technologies and len(bullets) < 3:
            tech_str = ", ".join(technologies[:4])
            bullets.append(f"Utilized {tech_str} to build scalable and maintainable solutions")

        return bullets

    def _enhance_projects(self, projects: List[Dict], keywords: List[str]) -> List[Dict]:
        """Enhance project descriptions for resume."""
        enhanced = []
        for proj in projects:
            enhanced_proj = proj.copy()
            # Check keyword relevance
            proj_text = (proj.get("description", "") + " ".join(proj.get("technologies", []))).lower()
            relevance_score = sum(1 for kw in keywords if kw.lower() in proj_text)
            enhanced_proj["relevance_score"] = relevance_score
            enhanced_proj["highlight"] = relevance_score > 2

            # Generate impact statement
            impact = proj.get("impact", "")
            if not impact:
                tech_count = len(proj.get("technologies", []))
                enhanced_proj["generated_impact"] = f"Implemented using {tech_count} technologies, demonstrating full-stack development capabilities"
            enhanced.append(enhanced_proj)

        # Sort by relevance
        enhanced.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return enhanced

    def _format_education(self, education: List[Dict]) -> List[Dict]:
        formatted = []
        for edu in education:
            formatted_edu = edu.copy()
            gpa = edu.get("gpa")
            if gpa and gpa >= 3.5:
                formatted_edu["highlight_gpa"] = True
            formatted.append(formatted_edu)
        return formatted

    # ─── Cover Letter Generation ───────────────────────────────────────────────

    def generate_cover_letter(self, profile: Dict, company: str, job_description: Optional[str], tone: str) -> Dict:
        """Generate a personalized cover letter."""
        name = profile.get("name", "Candidate")
        target_role = profile.get("target_role", "Software Developer")
        skills = profile.get("skills", [])[:6]
        projects = profile.get("projects", [])
        experience = profile.get("experience", [])
        education = profile.get("education", [{}])

        degree = education[0].get("degree", "Bachelor's") if education else "Bachelor's"
        field = education[0].get("field", "") if education else ""

        # Extract JD keywords
        jd_keywords = self._extract_keywords(job_description) if job_description else []

        # Find best matching project
        best_project = None
        if projects:
            for proj in projects:
                proj_text = proj.get("description", "") + " ".join(proj.get("technologies", []))
                if any(kw.lower() in proj_text.lower() for kw in jd_keywords):
                    best_project = proj
                    break
            if not best_project:
                best_project = projects[0]

        # Find best matching experience
        best_exp = experience[0] if experience else None

        # Tone adjustments
        tone_phrases = {
            "professional": {"opener": "I am writing to express my strong interest", "closing": "I look forward to discussing how my skills align"},
            "creative": {"opener": "I was thrilled to discover", "closing": "I'm excited about the possibility of bringing my unique perspective"},
            "technical": {"opener": "I am applying for the position of", "closing": "I would welcome the opportunity to discuss my technical background"},
        }
        phrases = tone_phrases.get(tone, tone_phrases["professional"])

        # Build cover letter paragraphs
        intro = (
            f"{phrases['opener']} in the {target_role} position at {company}. "
            f"With a {degree} in {field} and hands-on experience in {', '.join(skills[:3])}, "
            f"I am confident in my ability to make a meaningful contribution to your team."
        )

        body1 = ""
        if best_exp:
            body1 = (
                f"In my role as {best_exp.get('role')} at {best_exp.get('company')}, "
                f"I {best_exp.get('description', 'developed strong technical skills')[:100]}... "
                f"This experience strengthened my expertise in {', '.join(best_exp.get('technologies', skills[:2])[:3])}."
            )
        else:
            body1 = (
                f"Through my academic projects and self-directed learning, I have developed proficiency in "
                f"{', '.join(skills[:5])}. My coursework has given me a solid theoretical foundation "
                f"that I am eager to apply in a professional setting."
            )

        body2 = ""
        if best_project:
            proj_techs = ", ".join(best_project.get("technologies", [])[:4])
            body2 = (
                f"One of my key projects, {best_project.get('name')}, involved {best_project.get('description', '')[:120]}. "
                f"Built using {proj_techs}, this project demonstrates my ability to deliver end-to-end solutions. "
            )
            if best_project.get("impact"):
                body2 += f"{best_project.get('impact')}."

        # JD-specific paragraph
        jd_para = ""
        if jd_keywords:
            matching_skills = [s for s in skills if any(kw.lower() in s.lower() for kw in jd_keywords)]
            if matching_skills:
                jd_para = (
                    f"I noticed {company} is looking for expertise in {', '.join(jd_keywords[:3])}. "
                    f"My experience with {', '.join(matching_skills[:3])} makes me particularly well-suited for this role."
                )

        closing = (
            f"{phrases['closing']} with the {company} team. "
            f"I am particularly drawn to {company}'s work and believe my background in {', '.join(skills[:2])} "
            f"would enable me to contribute effectively from day one. "
            f"Thank you for considering my application."
        )

        return {
            "recipient": f"Hiring Manager, {company}",
            "subject": f"Application for {target_role} Position",
            "paragraphs": [intro, body1, body2, jd_para, closing],
            "signature": name,
            "word_count": len(" ".join([intro, body1, body2, jd_para, closing]).split()),
        }

    # ─── Portfolio Generation ──────────────────────────────────────────────────

    def generate_portfolio_content(self, profile: Dict) -> Dict:
        """Generate structured portfolio content."""
        name = profile.get("name", "Developer")
        skills = profile.get("skills", [])
        projects = profile.get("projects", [])
        target_role = profile.get("target_role", "")

        # Generate tagline
        taglines = [
            f"Building tomorrow's solutions with {skills[0] if skills else 'code'}",
            f"Turning ideas into {target_role.lower()} reality",
            f"Passionate {target_role} • Problem Solver • Innovator",
            f"Code. Create. Impact.",
        ]
        tagline = taglines[len(name) % len(taglines)]

        # Categorize projects for portfolio
        featured_projects = []
        for proj in projects[:6]:
            portfolio_proj = {
                **proj,
                "tags": proj.get("technologies", [])[:4],
                "category": self._categorize_project(proj),
                "card_color": self._assign_card_color(proj),
            }
            featured_projects.append(portfolio_proj)

        # Generate skill visualization data
        skill_chart_data = self._generate_skill_chart(skills)

        # Generate stats
        stats = {
            "projects_built": len(projects),
            "technologies": len(set(skills)),
            "years_coding": max(1, len(profile.get("experience", []))) + 1,
            "certifications": len(profile.get("certifications", [])),
        }

        # Bio sections
        bio = {
            "headline": f"{target_role} & Problem Solver",
            "tagline": tagline,
            "about": self._generate_about_section(profile),
            "interests": self._infer_interests(skills, projects),
        }

        return {
            "bio": bio,
            "featured_projects": featured_projects,
            "skills_visualization": skill_chart_data,
            "stats": stats,
            "contact": self._build_header(profile),
            "testimonial_prompt": f"Ask colleagues to highlight your work on {projects[0].get('name', 'your key projects') if projects else 'your projects'}",
        }

    def _categorize_project(self, project: Dict) -> str:
        techs = [t.lower() for t in project.get("technologies", [])]
        desc = project.get("description", "").lower()

        if any(t in techs for t in ["react", "vue", "angular", "html", "css", "next.js"]):
            return "Web Development"
        elif any(t in techs for t in ["tensorflow", "pytorch", "sklearn", "pandas", "ml", "ai"]):
            return "Machine Learning"
        elif any(t in techs for t in ["android", "ios", "flutter", "react native", "swift"]):
            return "Mobile App"
        elif any(t in techs for t in ["docker", "kubernetes", "aws", "gcp", "azure"]):
            return "DevOps / Cloud"
        elif "api" in desc or any(t in techs for t in ["fastapi", "django", "flask", "express"]):
            return "Backend / API"
        else:
            return "Software Engineering"

    def _assign_card_color(self, project: Dict) -> str:
        colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#3b82f6", "#ef4444"]
        idx = len(project.get("name", "")) % len(colors)
        return colors[idx]

    def _generate_skill_chart(self, skills: List[str]) -> List[Dict]:
        chart_data = []
        for cat, cat_skills in self.skill_categories.items():
            matching = [s for s in skills if any(cs.lower() in s.lower() or s.lower() in cs.lower() for cs in cat_skills)]
            if matching:
                # Proficiency heuristic based on order in skills list
                proficiency = max(40, 100 - skills.index(matching[0]) * 5) if matching[0] in skills else 60
                chart_data.append({
                    "category": cat.replace("_", " ").title(),
                    "skills": matching[:5],
                    "proficiency": min(95, proficiency),
                    "count": len(matching),
                })
        return chart_data

    def _generate_about_section(self, profile: Dict) -> str:
        name = profile.get("name", "I")
        target_role = profile.get("target_role", "developer")
        skills = profile.get("skills", [])[:4]
        education = profile.get("education", [{}])
        degree = education[0].get("degree", "") if education else ""
        field = education[0].get("field", "") if education else ""
        projects_count = len(profile.get("projects", []))

        return (
            f"Hi, I'm {name} — a {target_role} passionate about building impactful software. "
            f"I hold a {degree} in {field} and have built {projects_count}+ projects "
            f"using technologies like {', '.join(skills)}. "
            f"I thrive at the intersection of technical excellence and creative problem-solving, "
            f"always looking for opportunities to learn and grow. "
            f"When I'm not coding, I'm exploring new technologies and contributing to open-source projects."
        )

    def _infer_interests(self, skills: List[str], projects: List[Dict]) -> List[str]:
        interests = []
        skill_lower = [s.lower() for s in skills]
        if any(s in skill_lower for s in ["tensorflow", "pytorch", "ml", "ai"]):
            interests.append("Artificial Intelligence")
        if any(s in skill_lower for s in ["react", "vue", "frontend", "ui"]):
            interests.append("UI/UX Design")
        if any(s in skill_lower for s in ["aws", "docker", "kubernetes"]):
            interests.append("Cloud Architecture")
        if any(s in skill_lower for s in ["blockchain", "web3", "solidity"]):
            interests.append("Blockchain Technology")
        interests.extend(["Open Source", "Tech Innovation"])
        return interests[:5]

    # ─── ATS Score ────────────────────────────────────────────────────────────

    def calculate_ats_score(self, resume_text: str, job_description: str) -> Dict:
        """Calculate ATS compatibility score."""
        jd_keywords = self._extract_keywords(job_description)
        resume_lower = resume_text.lower()

        # Keyword matching
        matched = [kw for kw in jd_keywords if kw.lower() in resume_lower]
        missed = [kw for kw in jd_keywords if kw.lower() not in resume_lower]
        keyword_score = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0

        # Format checks
        format_checks = {
            "has_email": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)),
            "has_phone": bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', resume_text)),
            "has_linkedin": "linkedin" in resume_lower,
            "has_github": "github" in resume_lower,
            "word_count_ok": 400 <= len(resume_text.split()) <= 800,
            "no_tables": "<table" not in resume_text.lower(),
            "has_summary": any(w in resume_lower for w in ["summary", "objective", "profile"]),
            "has_education": "education" in resume_lower or "university" in resume_lower,
            "has_experience": "experience" in resume_lower or "work" in resume_lower,
            "has_skills": "skill" in resume_lower,
        }

        format_score = sum(format_checks.values()) / len(format_checks) * 100

        # Action verbs check
        all_verbs = [v for vlist in self.action_verbs.values() for v in vlist]
        verbs_used = sum(1 for v in all_verbs if v.lower() in resume_lower)
        verb_score = min(100, verbs_used * 10)

        # Quantification check
        numbers_count = len(re.findall(r'\d+%?|\d+x', resume_text))
        quant_score = min(100, numbers_count * 15)

        total_score = int(keyword_score * 0.4 + format_score * 0.25 + verb_score * 0.2 + quant_score * 0.15)

        return {
            "overall_score": total_score,
            "breakdown": {
                "keyword_match": round(keyword_score, 1),
                "format_score": round(format_score, 1),
                "action_verbs": round(verb_score, 1),
                "quantification": round(quant_score, 1),
            },
            "matched_keywords": matched[:15],
            "missing_keywords": missed[:10],
            "format_checks": format_checks,
            "recommendations": self._generate_ats_recommendations(keyword_score, format_checks, verb_score, missed),
        }

    def _generate_ats_recommendations(self, kw_score, format_checks, verb_score, missed) -> List[str]:
        recs = []
        if kw_score < 60:
            recs.append(f"Add more keywords from the job description: {', '.join(missed[:5])}")
        if not format_checks.get("has_linkedin"):
            recs.append("Add your LinkedIn profile URL")
        if not format_checks.get("word_count_ok"):
            recs.append("Aim for 400-800 words in your resume")
        if not format_checks.get("has_summary"):
            recs.append("Add a professional summary section")
        if verb_score < 50:
            recs.append("Use more action verbs (Led, Built, Achieved, Optimized...)")
        recs.append("Quantify your achievements with numbers and percentages")
        return recs

    # ─── Skills Analysis ───────────────────────────────────────────────────────

    def analyze_skills(self, profile: Dict, job_description: Optional[str]) -> Dict:
        skills = profile.get("skills", [])
        jd_keywords = self._extract_keywords(job_description) if job_description else []

        matching = [s for s in skills if any(kw.lower() in s.lower() or s.lower() in kw.lower() for kw in jd_keywords)]
        gaps = [kw for kw in jd_keywords if not any(kw.lower() in s.lower() for s in skills)][:8]

        return {
            "total_skills": len(skills),
            "matching_skills": matching,
            "skill_gaps": gaps,
            "match_percentage": round(len(matching) / len(jd_keywords) * 100, 1) if jd_keywords else 100,
            "top_skills": skills[:8],
            "learning_suggestions": [f"Consider learning {gap}" for gap in gaps[:3]],
        }

    def suggest_skills(self, profile: Dict) -> List[Dict]:
        """Suggest skills based on existing skills and target role."""
        target_role = profile.get("target_role", "").lower()
        current_skills = [s.lower() for s in profile.get("skills", [])]

        role_skill_map = {
            "frontend": ["TypeScript", "React", "Next.js", "Tailwind CSS", "GraphQL", "Webpack", "Jest"],
            "backend": ["Docker", "PostgreSQL", "Redis", "Kubernetes", "Kafka", "gRPC", "Terraform"],
            "fullstack": ["TypeScript", "Docker", "PostgreSQL", "Redis", "GraphQL", "Jest", "CI/CD"],
            "data": ["PySpark", "Airflow", "DBT", "Snowflake", "Tableau", "BigQuery", "MLflow"],
            "ml": ["PyTorch", "Hugging Face", "MLflow", "LangChain", "ONNX", "Triton", "Ray"],
            "devops": ["Terraform", "Ansible", "Prometheus", "Grafana", "ArgoCD", "Helm", "Vault"],
        }

        suggestions = []
        for role_key, role_skills in role_skill_map.items():
            if role_key in target_role:
                for skill in role_skills:
                    if skill.lower() not in current_skills:
                        suggestions.append({
                            "skill": skill,
                            "reason": f"Commonly required for {target_role} roles",
                            "priority": "high" if len(suggestions) < 3 else "medium",
                        })

        # Generic suggestions if role not found
        if not suggestions:
            generic = ["Docker", "Git", "PostgreSQL", "REST API", "Unit Testing", "CI/CD", "Agile"]
            for skill in generic:
                if skill.lower() not in current_skills:
                    suggestions.append({"skill": skill, "reason": "Widely used across all roles", "priority": "medium"})

        return suggestions[:8]

    def generate_professional_summary(self, profile: Dict) -> str:
        return self._generate_summary(profile, [], "professional")

    def improve_bullet_points(self, bullets: List[str], role: str) -> List[str]:
        improved = []
        for bullet in bullets:
            words = bullet.strip().split()
            first_word = words[0] if words else ""
            all_verbs = [v for vlist in self.action_verbs.values() for v in vlist]

            if not any(first_word.lower() == v.lower() for v in all_verbs):
                category = "development" if "engineer" in role.lower() or "develop" in role.lower() else "achievement"
                verb = self.action_verbs[category][len(improved) % len(self.action_verbs[category])]
                words[0] = words[0].lower()
                bullet = f"{verb} {' '.join(words)}"

            # Add quantification prompt if missing
            if not re.search(r'\d+', bullet):
                bullet += " — [Add specific metric: X%, $Y, N users]"

            improved.append(bullet)
        return improved

    # ─── Utilities ─────────────────────────────────────────────────────────────

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text using frequency + tech-term detection."""
        if not text:
            return []

        # Known tech terms (preserve casing)
        tech_terms = set()
        all_skills = [s for sl in self.skill_categories.values() for s in sl]
        for term in all_skills:
            if term.lower() in text.lower():
                tech_terms.add(term)

        # Extract n-grams and filter stopwords
        stopwords = {"and", "the", "for", "with", "you", "our", "will", "have", "are", "this",
                    "that", "from", "your", "we", "in", "of", "to", "a", "an", "is", "be",
                    "or", "as", "at", "by", "it", "on", "if", "no", "up", "do", "so"}
        words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.-]{2,}\b', text)
        word_freq = Counter(w.lower() for w in words if w.lower() not in stopwords)

        top_words = [w for w, _ in word_freq.most_common(30)]

        # Combine tech terms + frequent words
        keywords = list(tech_terms) + [w for w in top_words if w not in [t.lower() for t in tech_terms]]
        return keywords[:25]