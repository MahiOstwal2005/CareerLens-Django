import re
import os
import json
from google import genai

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
    experience_keywords = ['experience', 'years', 'led', 'managed', 'developed', 'created', 'achieved', 'architected', 'scaled']
    exp_matched = [kw for kw in experience_keywords if kw in text_lower]
    has_experience = len(exp_matched) >= 2
    
    # Education Checks
    edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'certification']
    edu_matched = [kw for kw in edu_keywords if kw in text_lower]
    has_education = len(edu_matched) >= 1
    
    # Soft Skills
    soft_keywords = ['leadership', 'teamwork', 'communication', 'problem solving', 'agile', 'scrum', 'collaboration']
    soft_matched = [kw for kw in soft_keywords if kw in text_lower]
    
    # Objectives
    obj_keywords = ['objective', 'summary', 'seeking', 'professional', 'profile', 'vision']
    has_objective = any(kw in text_lower for kw in obj_keywords)
    
    # Score calculation
    keyword_score = int((len(matched) / len(CORE_KEYWORDS)) * 50)
    exp_score = 20 if has_experience else 5
    edu_score = 10 if has_education else 0
    soft_score = int((len(soft_matched) / len(soft_keywords)) * 10) if soft_keywords else 0
    obj_score = 10 if has_objective else 0
    
    final_score = min(keyword_score + exp_score + edu_score + soft_score + obj_score, 100)
    
    # Build a dummy comprehensive report to satisfy the new UI, but highly professional
    comprehensive_report = {
        "resumeScore": final_score,
        "careerReadiness": "Strong Candidate" if final_score > 70 else "Requires Refinement",
        "strengths": ["Demonstrates baseline technical vocabulary", "Clear attempt at structuring professional narrative"] if keyword_score > 10 else ["Basic structural elements present"],
        "improvements": [
            {"title": "Quantify Business Impact", "description": "FAANG recruiters look for metrics (e.g., 'Scaled system to handle 10k RPS'). Convert responsibilities into measurable achievements.", "priority": "High"} if not has_experience else {"title": "Modernize Tech Stack", "description": "Ensure your featured skills align with current enterprise industry standards.", "priority": "Medium"},
            {"title": "Executive Summary", "description": "Transform your objective into a high-impact executive summary detailing your engineering philosophy.", "priority": "High"} if not has_objective else {"title": "Refine Value Proposition", "description": "Sharpen your summary to immediately communicate your unique engineering value.", "priority": "Medium"}
        ],
        "atsOptimization": {
            "score": keyword_score,
            "missingKeywords": missing[:5],
            "matchedKeywords": matched,
            "suggestions": ["Integrate missing enterprise-grade keywords contextually within bullet points, avoiding keyword stuffing."]
        },
        "skillGaps": [
            {"skill": kw, "priority": "High", "reason": "Critical prerequisite for senior/mid-level engineering roles."} for kw in missing[:3]
        ],
        "jobRecommendations": [
            {"role": "Enterprise Software Engineer", "matchPercentage": final_score, "reason": "Alignment with core foundational technologies."}
        ],
        "learningRecommendations": [
            {"skill": "System Design & Scalability", "reason": "Essential for passing rigorous technical interviews at top-tier tech companies.", "priority": "High"}
        ],
        "interviewPreparation": {
            "technicalTopics": ["Distributed Systems", "Data Structures & Algorithms", "Microservices Architecture"],
            "questions": ["Walk me through a time you had to architect a system for high availability.", "How do you approach debugging a production incident at scale?"]
        },
        "roadmap": {
            "days30": ["Rewrite bullet points using the STAR method (Situation, Task, Action, Result).", "Audit portfolio for UX/UI inconsistencies."],
            "days60": ["Complete 20 advanced LeetCode problems.", "Conduct mock system design interviews."],
            "days90": ["Begin strategic outreach to engineering managers.", "Prepare for behavioral leadership rounds."]
        },
        "nextBestActions": [
            "Inject quantifiable metrics (%, $, scale) into your work experience.",
            "Elevate the technical depth of your project descriptions."
        ]
    }
    
    return {
        "score": final_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "feedback": "Executive Analysis: Document parsed using heuristic fallback. Found baseline formatting, but lacks deep quantifiable impact required for top-tier roles.",
        "comprehensive_report": comprehensive_report
    }

def calculate_ats_score(text, doc_type='resume'):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment. Using fallback algorithm.")
        return _fallback_calculate_ats_score(text)
        
    try:
        client = genai.Client(api_key=api_key)
        
        if doc_type == 'portfolio':
            prompt_context = "SOFTWARE ENGINEERING PORTFOLIO (projects, system architecture, UX/UI, technical depth, live links)"
        else:
            prompt_context = "SOFTWARE ENGINEER RESUME"

        prompt = f"""
You are an elite Principal Engineer and a Senior Technical Recruiter at a FAANG company.
You are evaluating this candidate's {prompt_context}. Provide a brutally honest, highly professional, enterprise-grade analysis.
Do NOT wrap the response in markdown blocks like ```json. Return ONLY valid, raw JSON.

The JSON MUST exactly match this structure:
{{
  "resumeScore": <int between 0 and 100 based on rigorous FAANG standards>,
  "careerReadiness": "Exceptional" | "Strong" | "Requires Refinement" | "Junior Level",
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "improvements": [
    {{
      "title": "Short title (e.g., Quantify Impact)",
      "description": "Harsh but professional actionable description",
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
      "reason": "Why this is a red flag for senior roles"
    }}
  ],
  "jobRecommendations": [
    {{
      "role": "Specific Job Title",
      "matchPercentage": <int 0-100>,
      "reason": "Why they fit this echelon"
    }}
  ],
  "learningRecommendations": [
    {{
      "skill": "Advanced Topic (e.g., Distributed Systems)",
      "reason": "Why to learn it",
      "priority": "High" | "Medium" | "Low"
    }}
  ],
  "interviewPreparation": {{
    "technicalTopics": ["topic1", "topic2"],
    "questions": ["Extremely difficult FAANG interview question 1", "Question 2"]
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

Analyze this document text and provide personalized, actionable, top-tier engineering feedback. Focus heavily on system design, quantifiable metrics, business impact, and modern tech stacks.
---
{text[:6000]}
---
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Extract json using regex if there's markdown
        import re
        json_match = re.search(r'\{.*\}', response_text.strip(), re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
            
        result_json = json.loads(response_text)
        
        ats_score = result_json.get('resumeScore', 0)
        ats_opt = result_json.get('atsOptimization', {})
        matched = ats_opt.get('matchedKeywords', [])
        missing = ats_opt.get('missingKeywords', [])
        
        feedback = f"Executive Analysis: {result_json.get('careerReadiness', 'Unknown')}. "
        if result_json.get('strengths'):
            feedback += f"Key Strengths: {', '.join(result_json['strengths'][:2])}. "
            
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
