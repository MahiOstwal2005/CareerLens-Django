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
    
    # Build a dummy comprehensive report to satisfy the new UI
    comprehensive_report = {
        "resumeScore": final_score,
        "careerReadiness": "Good" if final_score > 70 else "Needs Work",
        "strengths": ["Found some technical skills"] if keyword_score > 20 else [],
        "improvements": [
            {"title": "Add Achievements", "description": "Add more quantifiable achievements.", "priority": "High"} if not has_experience else {"title": "Update Skills", "description": "Ensure your skills are up to date.", "priority": "Low"},
            {"title": "Add Summary", "description": "Include a strong professional summary.", "priority": "High"} if not has_objective else {"title": "Refine Summary", "description": "Make sure your summary is impactful.", "priority": "Low"}
        ],
        "atsOptimization": {
            "score": keyword_score,
            "missingKeywords": missing[:5],
            "matchedKeywords": matched,
            "suggestions": ["Include more industry-standard keywords from the job description."]
        },
        "skillGaps": [
            {"skill": kw, "priority": "Medium", "reason": "Commonly requested in this field."} for kw in missing[:3]
        ],
        "jobRecommendations": [
            {"role": "Software Developer", "matchPercentage": final_score, "reason": "Based on your technical keywords."}
        ],
        "learningRecommendations": [
            {"skill": "Cloud Computing (AWS/Docker)", "reason": "Highly demanded in tech right now.", "priority": "Medium"}
        ],
        "interviewPreparation": {
            "technicalTopics": ["Data Structures", "System Design"],
            "questions": ["Can you describe a challenging project?", "How do you handle conflict?"]
        },
        "roadmap": {
            "days30": ["Update resume", "Practice coding challenges"],
            "days60": ["Apply for roles", "Do mock interviews"],
            "days90": ["Evaluate offers", "Prepare for onboarding"]
        },
        "nextBestActions": [
            "Add missing keywords to your resume.",
            "Start applying for junior/mid-level roles."
        ]
    }
    
    return {
        "score": final_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "feedback": "Your resume was analyzed across 5 crucial dimensions (Fallback algorithm).",
        "comprehensive_report": comprehensive_report
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
  "resumeScore": <int between 0 and 100>,
  "careerReadiness": "Excellent" | "Good" | "Fair" | "Needs Work",
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "improvements": [
    {{
      "title": "Short title",
      "description": "Actionable description",
      "priority": "High" | "Medium" | "Low"
    }}
  ],
  "atsOptimization": {{
    "score": <int 0-100>,
    "missingKeywords": ["keyword1", "keyword2"],
    "matchedKeywords": ["keyword3", "keyword4"],
    "suggestions": ["suggestion1", "suggestion2"]
  }},
  "skillGaps": [
    {{
      "skill": "skill name",
      "priority": "High" | "Medium" | "Low",
      "reason": "Why this is needed"
    }}
  ],
  "jobRecommendations": [
    {{
      "role": "Job Title",
      "matchPercentage": <int 0-100>,
      "reason": "Why it matches"
    }}
  ],
  "learningRecommendations": [
    {{
      "skill": "Topic to learn",
      "reason": "Why to learn it",
      "priority": "High" | "Medium" | "Low"
    }}
  ],
  "interviewPreparation": {{
    "technicalTopics": ["topic1", "topic2"],
    "questions": ["Question 1", "Question 2"]
  }},
  "roadmap": {{
    "days30": ["action 1", "action 2"],
    "days60": ["action 3", "action 4"],
    "days90": ["action 5", "action 6"]
  }},
  "nextBestActions": [
    "action 1",
    "action 2"
  ]
}}

Analyze this document text and provide personalized, actionable career suggestions. 
Avoid generic advice. Be concise and prioritize actionable recommendations over explanations.
Do not invent experience.
---
{text[:5000]}
---
"""
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract json using regex if there's markdown
        import re
        json_match = re.search(r'\{.*\}', response_text.strip(), re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
            
        result_json = json.loads(response_text)
        
        # Map back to old expected format for ATSResult, and save the full new format in detailed_report
        ats_score = result_json.get('resumeScore', 0)
        ats_opt = result_json.get('atsOptimization', {})
        matched = ats_opt.get('matchedKeywords', [])
        missing = ats_opt.get('missingKeywords', [])
        
        feedback = f"Career Readiness: {result_json.get('careerReadiness', 'Unknown')}. "
        if result_json.get('strengths'):
            feedback += f"Strengths: {', '.join(result_json['strengths'][:2])}. "
            
        return {
            "score": ats_score,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "feedback": feedback,
            "comprehensive_report": result_json
        }
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return _fallback_calculate_ats_score(text)
