import os
import json
from typing import Dict, List

class ResumeTailor:
    def __init__(self):
        """Initialize resume tailor with AI capabilities"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    def tailor_resume(self, base_resume: str, job_description: str) -> str:
        """
        Tailor resume based on job description using AI
        
        Args:
            base_resume: Original resume content
            job_description: Job posting description
            
        Returns:
            Tailored resume content
        """
        # For now, return a placeholder
        # In production, integrate with OpenAI/Claude API
        
        prompt = f"""
        Please tailor the following resume for this job posting.
        Highlight relevant skills and experience that match the job requirements.
        Keep the format professional and ensure all information is truthful.
        
        Base Resume:
        {base_resume}
        
        Job Description:
        {job_description}
        
        Return only the tailored resume content without explanations.
        """
        
        tailored = self._call_ai_api(prompt)
        return tailored if tailored else base_resume
    
    def extract_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description"""
        keywords = []
        
        # Common tech keywords
        tech_keywords = [
            'python', 'javascript', 'java', 'c++', 'react', 'nodejs', 'sql',
            'aws', 'docker', 'kubernetes', 'git', 'agile', 'rest api',
            'machine learning', 'data science', 'devops', 'cloud'
        ]
        
        job_desc_lower = job_description.lower()
        for keyword in tech_keywords:
            if keyword in job_desc_lower:
                keywords.append(keyword)
        
        return keywords
    
    def score_match(self, resume: str, job_description: str) -> float:
        """
        Calculate resume-job match score (0-100)
        
        Args:
            resume: Resume content
            job_description: Job description
            
        Returns:
            Match score as percentage
        """
        keywords = self.extract_keywords(job_description)
        resume_lower = resume.lower()
        
        matched_keywords = sum(1 for kw in keywords if kw in resume_lower)
        
        if not keywords:
            return 50.0  # Default score if no keywords found
        
        match_score = (matched_keywords / len(keywords)) * 100
        return min(match_score, 100.0)
    
    def _call_ai_api(self, prompt: str) -> str:
        """
        Call AI API (OpenAI/Claude) for resume tailoring
        Implement with your preferred AI service
        """
        # TODO: Implement with OpenAI or Claude API
        try:
            # Example with OpenAI (requires OPENAI_API_KEY)
            import openai
            
            if not self.api_key:
                print("Warning: OPENAI_API_KEY not set. Using default response.")
                return ""
            
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return ""
