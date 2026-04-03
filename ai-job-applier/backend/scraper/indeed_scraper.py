import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from urllib.parse import urljoin

class IndeedScraper:
    def __init__(self):
        self.base_url = "https://www.indeed.com/jobs"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_jobs(self, keywords: str, location: str = "", num_results: int = 25) -> List[Dict]:
        """Search for jobs on Indeed"""
        jobs = []
        
        params = {
            'q': keywords,
            'l': location,
            'start': 0
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for job_card in job_cards[:num_results]:
                    job = self.parse_job_card(job_card)
                    if job:
                        jobs.append(job)
                        
                print(f"Found {len(jobs)} jobs on Indeed")
            else:
                print(f"Failed to fetch Indeed page: {response.status_code}")
                
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def parse_job_card(self, job_card) -> Dict:
        """Parse individual job card from Indeed"""
        try:
            job = {}
            
            # Extract job title
            title_elem = job_card.find('h2', class_='jobTitle')
            job['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
            
            # Extract company name
            company_elem = job_card.find('span', class_='companyName')
            job['company'] = company_elem.get_text(strip=True) if company_elem else 'N/A'
            
            # Extract location
            location_elem = job_card.find('div', class_='companyLocation')
            job['location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Extract salary if available
            salary_elem = job_card.find('div', class_='salary-snippet')
            job['salary'] = salary_elem.get_text(strip=True) if salary_elem else 'Not specified'
            
            # Extract job URL
            link_elem = job_card.find('a', class_='jcs-JobTitle')
            job['url'] = urljoin(self.base_url, link_elem['href']) if link_elem else ''
            
            # Extract job description snippet
            desc_elem = job_card.find('ul', class_='jobCardReqList')
            job['description'] = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
            
            job['platform'] = 'indeed'
            
            return job
            
        except Exception as e:
            print(f"Error parsing Indeed job card: {e}")
            return None
