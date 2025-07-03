from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()

# Input model
class ResumeRequest(BaseModel):
    resumeText: str

# Output model
class ResumeResponse(BaseModel):
    skills: List[str]
    titles: List[str]
    yearsExperience: int
    gaps: List[str]
    recommendations: List[str]

# Skill and title keyword banks
COMMON_SKILLS = [
    "Python", "Java", "SQL", "Figma", "UX", "Product Strategy", "Agile",
    "Scrum", "Roadmap", "User Research", "Metrics", "Data Analysis"
]

COMMON_TITLES = [
    "Product Manager", "Product Owner", "Business Analyst",
    "Associate Product Manager", "Senior Product Manager"
]

# Guess years of experience from patterns like '8 years'
def guess_years_experience(text: str) -> int:
    pattern = re.compile(r"(\d+)\s*(?:years|yrs)", re.IGNORECASE)
    matches = pattern.findall(text)
    if matches:
        return max(int(y) for y in matches if int(y) < 50)
    return 0

# Extract skills present in resume text
def extract_skills(text: str) -> List[str]:
    found = [skill for skill in COMMON_SKILLS if skill.lower() in text.lower()]
    return found

# Extract titles present in resume text
def extract_titles(text: str) -> List[str]:
    found = [title for title in COMMON_TITLES if title.lower() in text.lower()]
    return found

# Look for common gaps
def find_gaps(text: str) -> List[str]:
    gaps = []
    if "impact" not in text.lower() and "outcome" not in text.lower():
        gaps.append("Missing outcome-focused language")
    if "metric" not in text.lower():
        gaps.append("No metrics mentioned")
    if "lead" not in text.lower() and "led" not in text.lower():
        gaps.append("No leadership evidence")
    return gaps

# Recommend fixes for those gaps
def recommend_from_gaps(gaps: List[str]) -> List[str]:
    recs = []
    if "Missing outcome-focused language" in gaps:
        recs.append("Rewrite bullets to focus on outcomes, not tasks")
    if "No metrics mentioned" in gaps:
        recs.append("Add measurable metrics to your achievements")
    if "No leadership evidence" in gaps:
        recs.append("Show initiatives you owned or led")
    return recs
# FastAPI route
@app.post("/parse-resume", response_model=ResumeResponse)
async def analyze_resume(req: ResumeRequest):
    text = req.resumeText
    skills = extract_skills(text)
    titles = extract_titles(text)
    years_exp = guess_years_experience(text)
    gaps = find_gaps(text)
    recommendations = recommend_from_gaps(gaps)
    return ResumeResponse(
        skills=skills,
        titles=titles,
        yearsExperience=years_exp,
        gaps=gaps,
        recommendations=recommendations
    )

# ROOT route to satisfy Render health check
@app.get("/")
async def root():
    return {"message": "Resume Parser API is alive!"}
