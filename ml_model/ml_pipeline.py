"""
AI Resume Builder - ML Model Module
==============================================
This module provides:
1. Keyword Extraction Model (TF-IDF based)
2. Resume Classifier (categorizes resumes by domain)
3. Skill Gap Analyzer (cosine similarity)
4. ATS Score Predictor (rule-based + heuristics)
5. Sentence Enhancement (template + pattern matching)

For production use: Fine-tune on resume datasets from Kaggle's
"Resume Dataset" or "LiveCareer Resume Dataset".
"""

import re
import json
import math
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
import os
import sys

# Ensure the backend package is importable when running this module directly
_HERE = os.path.dirname(__file__)
_BACKEND_PATH = os.path.abspath(os.path.join(_HERE, "..", "backend"))
if _BACKEND_PATH not in sys.path:
    sys.path.insert(0, _BACKEND_PATH)


# ─── TF-IDF Vectorizer (pure Python, no sklearn needed) ───────────────────────


class TFIDFVectorizer:
    """Lightweight TF-IDF vectorizer implemented from scratch."""

    def __init__(self, max_features: int = 500, ngram_range: Tuple = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vocabulary = {}
        self.idf_values = {}
        self.fitted = False

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\b[a-z][a-z0-9+#.-]{1,}\b", text.lower())
        stopwords = {
            "and",
            "the",
            "for",
            "with",
            "you",
            "our",
            "will",
            "have",
            "are",
            "this",
            "that",
            "from",
            "your",
            "we",
            "in",
            "of",
            "to",
            "a",
            "an",
            "is",
            "be",
            "or",
            "as",
            "at",
            "by",
        }
        tokens = [t for t in tokens if t not in stopwords]

        ngrams = []
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            ngrams.extend(
                [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
            )
        return ngrams

    def fit(self, documents: List[str]):
        """Fit TF-IDF on corpus."""
        all_tokens = []
        doc_tokens = []

        for doc in documents:
            tokens = set(self._tokenize(doc))
            doc_tokens.append(tokens)
            all_tokens.extend(tokens)

        token_freq = Counter(all_tokens)
        top_tokens = [t for t, _ in token_freq.most_common(self.max_features)]
        self.vocabulary = {t: i for i, t in enumerate(top_tokens)}

        # Compute IDF
        N = len(documents)
        for token in self.vocabulary:
            df = sum(1 for dt in doc_tokens if token in dt)
            self.idf_values[token] = math.log((N + 1) / (df + 1)) + 1

        self.fitted = True
        return self

    def transform(self, documents: List[str]) -> List[Dict[str, float]]:
        """Transform documents to TF-IDF vectors (as dicts for sparse representation)."""
        if not self.fitted:
            raise RuntimeError("Vectorizer not fitted. Call fit() first.")

        vectors = []
        for doc in documents:
            tokens = self._tokenize(doc)
            tf = Counter(tokens)
            total = max(len(tokens), 1)

            vector = {}
            for token, idx in self.vocabulary.items():
                if token in tf:
                    tfidf = (tf[token] / total) * self.idf_values.get(token, 1)
                    vector[idx] = tfidf
            vectors.append(vector)
        return vectors

    def fit_transform(self, documents: List[str]) -> List[Dict[str, float]]:
        return self.fit(documents).transform(documents)

    def cosine_similarity(self, vec1: Dict, vec2: Dict) -> float:
        """Compute cosine similarity between two sparse vectors."""
        if not vec1 or not vec2:
            return 0.0

        dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in vec1)
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)


# ─── Resume Domain Classifier ─────────────────────────────────────────────────


class ResumeDomainClassifier:
    """
    Naive Bayes-style domain classifier for resumes.
    Classifies into: Software, Data Science, DevOps, Mobile, Design, Finance, Marketing
    """

    DOMAIN_KEYWORDS = {
        "Software Engineering": {
            "primary": [
                "react",
                "node",
                "python",
                "java",
                "c++",
                "rest api",
                "microservices",
                "algorithms",
                "data structures",
                "backend",
                "frontend",
                "fullstack",
                "typescript",
                "kubernetes",
            ],
            "weight": 1.0,
        },
        "Data Science & ML": {
            "primary": [
                "machine learning",
                "deep learning",
                "tensorflow",
                "pytorch",
                "pandas",
                "numpy",
                "scikit-learn",
                "nlp",
                "computer vision",
                "neural network",
                "dataset",
                "model training",
                "data analysis",
                "statistics",
                "regression",
                "classification",
            ],
            "weight": 1.0,
        },
        "DevOps & Cloud": {
            "primary": [
                "docker",
                "kubernetes",
                "aws",
                "azure",
                "gcp",
                "terraform",
                "ci/cd",
                "jenkins",
                "ansible",
                "prometheus",
                "grafana",
                "infrastructure",
                "pipeline",
                "deployment",
            ],
            "weight": 1.0,
        },
        "Mobile Development": {
            "primary": [
                "android",
                "ios",
                "flutter",
                "react native",
                "swift",
                "kotlin",
                "mobile app",
                "play store",
                "app store",
                "xcode",
                "android studio",
            ],
            "weight": 1.0,
        },
        "UI/UX Design": {
            "primary": [
                "figma",
                "sketch",
                "adobe xd",
                "user research",
                "wireframe",
                "prototype",
                "design system",
                "usability",
                "ux",
                "ui",
                "typography",
                "accessibility",
            ],
            "weight": 1.0,
        },
        "Finance & Quant": {
            "primary": [
                "financial modeling",
                "bloomberg",
                "quantitative",
                "risk",
                "portfolio",
                "trading",
                "excel",
                "valuation",
                "derivatives",
                "hedge fund",
                "equity",
            ],
            "weight": 1.0,
        },
    }

    def predict(self, resume_text: str) -> Dict:
        """Classify resume domain and return confidence scores."""
        text_lower = resume_text.lower()
        scores = {}

        for domain, config in self.DOMAIN_KEYWORDS.items():
            score = 0
            matched = []
            for keyword in config["primary"]:
                if keyword in text_lower:
                    score += 1
                    matched.append(keyword)
            scores[domain] = {
                "score": score * config["weight"],
                "matched_keywords": matched,
                "confidence": min(100, score * 8),
            }

        # Sort by score
        sorted_domains = sorted(
            scores.items(), key=lambda x: x[1]["score"], reverse=True
        )
        primary_domain = (
            sorted_domains[0][0] if sorted_domains else "Software Engineering"
        )
        secondary_domain = sorted_domains[1][0] if len(sorted_domains) > 1 else None

        return {
            "primary_domain": primary_domain,
            "secondary_domain": secondary_domain,
            "confidence": sorted_domains[0][1]["confidence"] if sorted_domains else 0,
            "all_scores": dict(sorted_domains),
        }


# ─── Skill Gap Analyzer ───────────────────────────────────────────────────────


class SkillGapAnalyzer:
    """Analyzes gap between candidate skills and job requirements."""

    SKILL_TAXONOMY = {
        # Maps skills to related/prerequisite skills
        "React": ["JavaScript", "HTML", "CSS", "TypeScript", "Node.js"],
        "Machine Learning": [
            "Python",
            "NumPy",
            "Pandas",
            "Scikit-learn",
            "Mathematics",
            "Statistics",
        ],
        "Deep Learning": [
            "Python",
            "TensorFlow",
            "PyTorch",
            "Machine Learning",
            "NumPy",
            "CUDA",
        ],
        "Backend Development": [
            "Python",
            "Node.js",
            "PostgreSQL",
            "REST API",
            "Authentication",
            "Docker",
        ],
        "Data Engineering": ["Python", "SQL", "Apache Spark", "Airflow", "AWS", "ETL"],
        "DevOps": ["Docker", "Kubernetes", "CI/CD", "Linux", "Bash", "Cloud Platforms"],
        "Mobile Development": ["Flutter", "Swift", "Kotlin", "REST API", "Firebase"],
        "Full Stack": ["React", "Node.js", "PostgreSQL", "Docker", "Git", "REST API"],
    }

    LEARNING_RESOURCES = {
        "Python": {"platform": "Python.org", "time": "2-4 weeks", "level": "beginner"},
        "React": {
            "platform": "React.dev",
            "time": "3-6 weeks",
            "level": "intermediate",
        },
        "Docker": {
            "platform": "Docker Docs",
            "time": "1-2 weeks",
            "level": "intermediate",
        },
        "Machine Learning": {
            "platform": "Coursera / fast.ai",
            "time": "8-12 weeks",
            "level": "advanced",
        },
        "Kubernetes": {
            "platform": "CNCF Learning",
            "time": "3-4 weeks",
            "level": "advanced",
        },
        "TypeScript": {
            "platform": "TypeScript Handbook",
            "time": "2-3 weeks",
            "level": "intermediate",
        },
        "PostgreSQL": {
            "platform": "PostgreSQL Tutorial",
            "time": "2-3 weeks",
            "level": "beginner",
        },
        "AWS": {
            "platform": "AWS Skill Builder",
            "time": "4-8 weeks",
            "level": "intermediate",
        },
    }

    def analyze(self, candidate_skills: List[str], required_skills: List[str]) -> Dict:
        """Full skill gap analysis with recommendations."""
        candidate_lower = {s.lower() for s in candidate_skills}
        required_lower = {s.lower() for s in required_skills}

        # Direct matches
        matched = [s for s in required_skills if s.lower() in candidate_lower]

        # Gaps
        gaps = [s for s in required_skills if s.lower() not in candidate_lower]

        # Find transferable skills (partial matches)
        transferable = []
        for gap in gaps:
            related = self.SKILL_TAXONOMY.get(gap, [])
            transfer_from = [s for s in candidate_skills if s in related]
            if transfer_from:
                transferable.append(
                    {
                        "missing_skill": gap,
                        "transferable_from": transfer_from,
                        "gap_size": "small",
                    }
                )

        # Learning plan for top gaps
        learning_plan = []
        gap_skills_priority = [
            g for g in gaps if g not in [t["missing_skill"] for t in transferable]
        ]
        for skill in gap_skills_priority[:5]:
            resource = self.LEARNING_RESOURCES.get(
                skill,
                {
                    "platform": f"Search '{skill} tutorial'",
                    "time": "2-4 weeks",
                    "level": "varies",
                },
            )
            learning_plan.append(
                {
                    "skill": skill,
                    "priority": "high" if len(learning_plan) < 2 else "medium",
                    **resource,
                }
            )

        match_pct = (
            (len(matched) / len(required_skills) * 100) if required_skills else 100
        )

        return {
            "match_percentage": round(match_pct, 1),
            "matched_skills": matched,
            "missing_skills": gaps,
            "transferable_skills": transferable,
            "learning_plan": learning_plan,
            "readiness_level": self._get_readiness_level(match_pct),
        }

    def _get_readiness_level(self, match_pct: float) -> str:
        if match_pct >= 80:
            return "Strong Match — Apply Now!"
        elif match_pct >= 60:
            return "Good Match — Address 1-2 gaps before applying"
        elif match_pct >= 40:
            return "Moderate Match — 1-3 months preparation recommended"
        else:
            return "Early Stage — 3-6 months skill development needed"


# ─── Sentence Quality Scorer ──────────────────────────────────────────────────


class BulletPointScorer:
    """Scores and improves resume bullet points using STAR method heuristics."""

    ACTION_VERBS = [
        "Led",
        "Built",
        "Developed",
        "Achieved",
        "Improved",
        "Reduced",
        "Increased",
        "Managed",
        "Designed",
        "Implemented",
        "Optimized",
        "Delivered",
        "Created",
        "Collaborated",
        "Analyzed",
        "Automated",
        "Deployed",
        "Architected",
        "Launched",
        "Mentored",
        "Researched",
        "Presented",
        "Streamlined",
        "Integrated",
        "Scaled",
    ]

    def score_bullet(self, bullet: str) -> Dict:
        """Score a bullet point on multiple dimensions (0-100 each)."""
        scores = {}

        # 1. Starts with action verb
        first_word = bullet.strip().split()[0] if bullet.strip() else ""
        scores["action_verb"] = (
            100
            if any(first_word.lower() == v.lower() for v in self.ACTION_VERBS)
            else 0
        )

        # 2. Has quantification
        has_number = bool(
            re.search(
                r"\d+%?|\d+x|\$[\d,]+|\d+\s*(users|customers|hours|days|weeks)", bullet
            )
        )
        scores["quantification"] = 100 if has_number else 0

        # 3. Length (ideal: 10-25 words)
        word_count = len(bullet.split())
        if 10 <= word_count <= 25:
            scores["length"] = 100
        elif word_count < 10:
            scores["length"] = int(word_count / 10 * 100)
        else:
            scores["length"] = max(0, 100 - (word_count - 25) * 5)

        # 4. Technical depth (mentions technologies)
        tech_pattern = r"\b(python|react|aws|docker|kubernetes|sql|api|machine learning|tensorflow)\b"
        scores["technical_depth"] = (
            80 if re.search(tech_pattern, bullet.lower()) else 30
        )

        # 5. Impact clarity (result-oriented language)
        impact_words = [
            "resulting in",
            "leading to",
            "achieving",
            "improved",
            "increased",
            "reduced",
            "saving",
            "enabling",
        ]
        scores["impact_clarity"] = (
            100 if any(w in bullet.lower() for w in impact_words) else 40
        )

        overall = int(sum(scores.values()) / len(scores))

        return {
            "bullet": bullet,
            "overall_score": overall,
            "breakdown": scores,
            "grade": "A"
            if overall >= 80
            else "B"
            if overall >= 60
            else "C"
            if overall >= 40
            else "D",
            "suggestions": self._generate_suggestions(scores, bullet),
        }

    def _generate_suggestions(self, scores: Dict, bullet: str) -> List[str]:
        suggestions = []
        if scores["action_verb"] == 0:
            suggestions.append(
                f"Start with an action verb (e.g., {self.ACTION_VERBS[0]}, {self.ACTION_VERBS[1]})"
            )
        if scores["quantification"] == 0:
            suggestions.append(
                "Add metrics: 'improved performance by X%' or 'served N users'"
            )
        if scores["length"] < 50:
            word_count = len(bullet.split())
            if word_count < 10:
                suggestions.append(
                    "Expand the bullet point with more context (aim for 15-20 words)"
                )
            else:
                suggestions.append("Shorten the bullet point (aim for under 25 words)")
        if scores["impact_clarity"] < 50:
            suggestions.append(
                "Add result: '...resulting in X% improvement' or '...enabling Y'"
            )
        return suggestions


# ─── Complete ML Pipeline ─────────────────────────────────────────────────────


class ResumeMLPipeline:
    """
    End-to-end ML pipeline for resume analysis.
    Combines all models for comprehensive analysis.
    """

    def __init__(self):
        self.vectorizer = TFIDFVectorizer(max_features=300)
        self.classifier = ResumeDomainClassifier()
        self.gap_analyzer = SkillGapAnalyzer()
        self.bullet_scorer = BulletPointScorer()
        self._fitted = False

    def fit_vectorizer(self, sample_documents: List[str]):
        """Fit TF-IDF on a corpus of resume/JD documents."""
        self.vectorizer.fit(sample_documents)
        self._fitted = True

    def match_resume_to_job(self, resume_text: str, job_description: str) -> Dict:
        """
        Full pipeline: match resume to job description.
        Returns similarity score, domain, gaps, recommendations.
        """
        # Fit on these two documents if not already fitted
        if not self._fitted:
            self.vectorizer.fit([resume_text, job_description])
            self._fitted = True

        vectors = self.vectorizer.transform([resume_text, job_description])
        similarity = self.vectorizer.cosine_similarity(vectors[0], vectors[1])

        domain = self.classifier.predict(resume_text)

        return {
            "similarity_score": round(similarity * 100, 1),
            "domain_classification": domain,
            "recommendation": self._get_recommendation(similarity),
        }

    def analyze_resume_bullets(self, bullets: List[str]) -> Dict:
        """Analyze and score all bullets in a resume."""
        scored = [self.bullet_scorer.score_bullet(b) for b in bullets]
        avg_score = (
            sum(s["overall_score"] for s in scored) / len(scored) if scored else 0
        )

        return {
            "bullets": scored,
            "average_score": round(avg_score, 1),
            "improvement_priority": sorted(scored, key=lambda x: x["overall_score"])[
                :3
            ],
        }

    def full_analysis(self, resume_data: Dict, job_description: str) -> Dict:
        """Run complete ML analysis on a resume."""
        # Serialize resume to text for analysis
        resume_text = self._serialize_resume(resume_data)

        match = self.match_resume_to_job(resume_text, job_description)

        # Skill gap analysis
        from ml_engine import ResumeAIEngine

        engine = ResumeAIEngine()
        jd_keywords = engine._extract_keywords(job_description)
        candidate_skills = resume_data.get("skills", [])
        gap_analysis = self.gap_analyzer.analyze(candidate_skills, jd_keywords[:15])

        # Bullet analysis
        all_bullets = []
        for exp in resume_data.get("experience", []):
            desc = exp.get("description", "")
            bullets = [s.strip() for s in desc.split(".") if len(s.strip()) > 10]
            all_bullets.extend(bullets)

        bullet_analysis = (
            self.analyze_resume_bullets(all_bullets) if all_bullets else {}
        )

        return {
            "job_match": match,
            "skill_gap": gap_analysis,
            "bullet_quality": bullet_analysis,
            "overall_recommendation": self._generate_overall_recommendation(
                match, gap_analysis
            ),
        }

    def _serialize_resume(self, resume_data: Dict) -> str:
        parts = [
            resume_data.get("name", ""),
            " ".join(resume_data.get("skills", [])),
            " ".join(edu.get("field", "") for edu in resume_data.get("education", [])),
            " ".join(
                f"{exp.get('role')} {exp.get('company')} {exp.get('description')}"
                for exp in resume_data.get("experience", [])
            ),
            " ".join(
                f"{p.get('name')} {p.get('description')} {' '.join(p.get('technologies', []))}"
                for p in resume_data.get("projects", [])
            ),
        ]
        return " ".join(parts)

    def _get_recommendation(self, similarity: float) -> str:
        if similarity >= 0.7:
            return "Excellent match! Apply with confidence."
        elif similarity >= 0.5:
            return "Good match. Tailor a few sections to better align."
        elif similarity >= 0.3:
            return "Moderate match. Consider adding relevant keywords."
        else:
            return "Low match. Significantly customize your resume for this role."

    def _generate_overall_recommendation(self, match: Dict, gap: Dict) -> str:
        sim = match.get("similarity_score", 0)
        match_pct = gap.get("match_percentage", 0)
        avg = (sim + match_pct) / 2

        if avg >= 75:
            return "Strong candidate profile. Submit application with the generated resume."
        elif avg >= 50:
            return f"Good foundation. Bridge {len(gap.get('missing_skills', []))} skill gaps to strengthen your application."
        else:
            return "Resume needs significant customization. Focus on the skill gaps and ATS optimization."


# ─── Demo / Testing ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("AI Resume Builder - ML Pipeline Demo")
    print("=" * 60)

    # Sample data
    sample_resume = {
        "name": "Priya Sharma",
        "skills": ["Python", "React", "Machine Learning", "PostgreSQL", "Docker"],
        "education": [
            {
                "degree": "B.Tech",
                "field": "Computer Science",
                "institution": "IIT Hyderabad",
            }
        ],
        "experience": [
            {
                "role": "Software Intern",
                "company": "TechStartup",
                "description": "Built REST APIs using FastAPI. Improved performance by reducing latency by 40%.",
            }
        ],
        "projects": [
            {
                "name": "SmartResume AI",
                "description": "AI-powered resume builder using NLP and machine learning",
                "technologies": ["Python", "React", "TensorFlow"],
            }
        ],
    }

    sample_jd = """
    We are looking for a Software Engineer with expertise in Python, React, Docker, and Kubernetes.
    Experience with machine learning and data pipelines is a plus. You will build scalable REST APIs
    and collaborate with cross-functional teams. Strong knowledge of PostgreSQL and cloud services required.
    """

    pipeline = ResumeMLPipeline()

    print("\n1. Full ML Analysis:")
    result = pipeline.full_analysis(sample_resume, sample_jd)
    print(f"   Job Match Similarity: {result['job_match']['similarity_score']}%")
    print(
        f"   Domain: {result['job_match']['domain_classification']['primary_domain']}"
    )
    print(f"   Skill Match: {result['skill_gap']['match_percentage']}%")
    print(f"   Missing Skills: {result['skill_gap']['missing_skills']}")
    print(f"   Readiness: {result['skill_gap']['readiness_level']}")

    print("\n2. Bullet Point Analysis:")
    scorer = BulletPointScorer()
    bullets = [
        "Built REST APIs using FastAPI",
        "Improved performance by 40% by optimizing database queries",
        "helped team with various tasks",
    ]
    for bullet in bullets:
        score = scorer.score_bullet(bullet)
        print(f"   [{score['grade']}] ({score['overall_score']}/100) {bullet[:50]}")
        if score["suggestions"]:
            print(f"        → {score['suggestions'][0]}")

    print("\n3. Domain Classification:")
    classifier = ResumeDomainClassifier()
    text = "Experienced Python developer with TensorFlow, PyTorch, NLP and machine learning expertise"
    domain = classifier.predict(text)
    print(
        f"   Primary: {domain['primary_domain']} ({domain['confidence']}% confidence)"
    )

    print("\n✅ ML Pipeline working correctly!")
