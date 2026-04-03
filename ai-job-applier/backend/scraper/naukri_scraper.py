import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from urllib.parse import urljoin

class NaukriScraper:
    def __init__(self):
        self.base_url = "https://www.naukri.com"
        self.search_url = "https://www.naukri.com/jobs"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_jobs(self, keywords: str, location: str = "", num_results: int = 25) -> List[Dict]:
        """Search for jobs on Naukri"""
        jobs = []
        
        # Naukri search URL format
        search_url = f"{self.search_url}-{keywords}-in-{location}" if location else f"{self.search_url}-{keywords}"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('article', class_='jobTuple')
                
                for job_card in job_cards[:num_results]:
                    job = self.parse_job_card(job_card)
                    if job:
                        jobs.append(job)
                        
                print(f"Found {len(jobs)} jobs on Naukri")
            else:
                print(f"Failed to fetch Naukri page: {response.status_code}")
                
        except Exception as e:
            print(f"Error scraping Naukri: {e}")
        
        return jobs
    
    def parse_job_card(self, job_card) -> Dict:
        """Parse individual job card from Naukri"""
        try:
            job = {}
            
            # Extract job title
            title_elem = job_card.find('a', class_='titleAnc')
            job['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
            job['url'] = title_elem['href'] if title_elem else ''
            
            # Extract company name
            company_elem = job_card.find('a', class_='subTitle')
            job['company'] = company_elem.get_text(strip=True) if company_elem else 'N/A'
            
            # Extract location
            location_elem = job_card.find('span', class_='locStr')
            job['location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Extract salary if available
            salary_elem = job_card.find('span', class_='salaryText')
            job['salary'] = salary_elem.get_text(strip=True) if salary_elem else 'Not specified'
            
            # Extract job description/experience
            desc_elem = job_card.find('ul', class_='jobBDesc')
            job['description'] = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
            
            job['platform'] = 'naukri'
            
            return job
            
        except Exception as e:
            print(f"Error parsing Naukri job card: {e}")
            return None
