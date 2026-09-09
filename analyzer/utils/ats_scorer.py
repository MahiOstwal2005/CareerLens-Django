import re
import os
import json
import google.generativeai as genai

# A basic list of common software engineering / general tech keywords
CORE_KEYWORDS = [
    "python", "java", "c++", "javascript", "react", "django", "node", "sql", "nosql",
    "mongodb", "aws", "docker", "kubernetes", "agile", "scrum", "git", "linux", "api",
    "rest", "graphql", "machine learning", "data analysis", "leadership", "teamwork",
    "problem solving", "communication", "project management", "html", "css", "bootstrap"
]

def _fallback_calculate_ats_score(text):
    text_lower = text.lower()
    
    matched = []
    missing = []
    
    for kw in CORE_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            matched.append(kw)
        else:
            missing.append(kw)
            
    # Technical Skills
    tech_score = len([kw for kw in matched if kw not in ['leadership', 'teamwork', 'problem solving', 'communication', 'project management']])
    
    # Experience Checks
    experience_keywords = ['experience', 'years', 'led', 'managed', 'developed', 'created', 'achieved']
    exp_matched = [kw for kw in experience_keywords if kw in text_lower]
    has_experience = len(exp_matched) >= 2
    
    # Education Checks
    edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
    edu_matched = [kw for kw in edu_keywords if kw in text_lower]
    has_education = len(edu_matched) >= 1
    
    # Soft Skills
    soft_keywords = ['leadership', 'teamwork', 'communication', 'problem solving', 'agile', 'scrum']
    soft_matched = [kw for kw in soft_keywords if kw in text_lower]
    
    # Objectives
    obj_keywords = ['objective', 'summary', 'seeking', 'professional', 'profile']
    has_objective = any(kw in text_lower for kw in obj_keywords)
    
    # Score calculation
    keyword_score = int((len(matched) / len(CORE_KEYWORDS)) * 50)
    exp_score = 20 if has_experience else 5
    edu_score = 10 if has_education else 0
    soft_score = int((len(soft_matched) / len(soft_keywords)) * 10) if soft_keywords else 0
    obj_score = 10 if has_objective else 0
    
    final_score = min(keyword_score + exp_score + edu_score + soft_score + obj_score, 100)
    
    detailed_report = {
        'experience': {
            'score': exp_score,
            'max_score': 20,
            'feedback': "Great use of action verbs and quantifiable experience." if has_experience else "Lack of experience highlighted. Try adding quantifiable achievements.",
            'status': 'success' if has_experience else 'danger'
        },
        'education': {
            'score': edu_score,
            'max_score': 10,
            'feedback': "Education/Knowledge section detected." if has_education else "Missing clear education indicators.",
            'status': 'success' if has_education else 'warning'
        },
        'technical_skills': {
            'score': keyword_score,
            'max_score': 50,
            'feedback': f"Found {tech_score} technical keywords.",
            'status': 'success' if keyword_score > 30 else 'warning'
        },
        'soft_skills': {
            'score': soft_score,
            'max_score': 10,
            'feedback': f"Found {len(soft_matched)} soft skills." if len(soft_matched) > 2 else "Lacking soft skills.",
            'status': 'success' if len(soft_matched) > 2 else 'danger'
        },
        'objectives': {
            'score': obj_score,
            'max_score': 10,
            'feedback': "Professional summary/objective found." if has_objective else "Missing a professional summary.",
            'status': 'success' if has_objective else 'danger'
        }
    }
    
    return {
        "score": final_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "feedback": "Your resume was analyzed across 5 crucial dimensions (Fallback algorithm).",
        "detailed_report": detailed_report
    }

def calculate_ats_score(text, doc_type='resume'):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment. Using fallback algorithm.")
        return _fallback_calculate_ats_score(text)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if doc_type == 'portfolio':
            prompt_context = "PORTFOLIO text (projects, case studies, technical depth, live links)"
            feedback_context = "portfolio's strengths and weaknesses"
            schema_experience = "Detailed feedback on their projects, case studies, and impact."
            schema_education = "Feedback on continuous learning, certifications, or depth of case studies."
            schema_objectives = "Feedback on overall presentation, UI/UX, and clarity."
        else:
            prompt_context = "resume text"
            feedback_context = "resume's strengths and weaknesses"
            schema_experience = "Detailed feedback on their work experience."
            schema_education = "Feedback on education."
            schema_objectives = "Feedback on professional summary."

        prompt = f"""
You are an expert ATS (Applicant Tracking System) algorithm and a Senior Technical Recruiter.
Analyze the following {prompt_context} and provide a highly accurate, structured JSON evaluation.
Do NOT wrap the response in markdown blocks like ```json. Return ONLY valid, raw JSON.

The JSON MUST exactly match this structure:
{{
    "score": <int between 0 and 100 based on overall quality>,
    "matched_keywords": ["list", "of", "found", "industry", "skills"],
    "missing_keywords": ["list", "of", "important", "skills", "they", "lack"],
    "feedback": "A short, actionable 2-sentence summary of the {feedback_context}.",
    "detailed_report": {{
        "experience": {{
            "score": <int 0-20>,
            "max_score": 20,
            "feedback": "{schema_experience}",
            "status": "success" | "warning" | "danger"
        }},
        "education": {{
            "score": <int 0-10>,
            "max_score": 10,
            "feedback": "{schema_education}",
            "status": "success" | "warning" | "danger"
        }},
        "technical_skills": {{
            "score": <int 0-50>,
            "max_score": 50,
            "feedback": "Feedback on technical skills and what is missing.",
            "status": "success" | "warning" | "danger"
        }},
        "soft_skills": {{
            "score": <int 0-10>,
            "max_score": 10,
            "feedback": "Feedback on soft skills and communication.",
            "status": "success" | "warning" | "danger"
        }},
        "objectives": {{
            "score": <int 0-10>,
            "max_score": 10,
            "feedback": "{schema_objectives}",
            "status": "success" | "warning" | "danger"
        }}
    }}
}}

Analyze this document text and be brutally honest but constructive:
---
{text[:5000]}
---
"""
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up markdown if the AI includes it anyway
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        result_json = json.loads(response_text.strip())
        return result_json
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return _fallback_calculate_ats_score(text)
