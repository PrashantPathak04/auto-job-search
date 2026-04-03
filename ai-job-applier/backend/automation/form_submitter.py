from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List, Optional
import time

class FormSubmitter:
    def __init__(self, headless: bool = False):
        """Initialize form submitter with Selenium"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def apply_to_job(self, job_url: str, application_data: Dict) -> bool:
        """
        Apply to a job by filling and submitting the form
        
        Args:
            job_url: URL of the job posting
            application_data: Dictionary with application information
                - first_name: str
                - last_name: str
                - email: str
                - phone: str
                - resume_path: str
                - cover_letter: str (optional)
        
        Returns:
            True if application was successful, False otherwise
        """
        try:
            self.driver.get(job_url)
            time.sleep(2)  # Wait for page to load
            
            # Click apply button
            apply_button = self._find_apply_button()
            if apply_button:
                apply_button.click()
                time.sleep(1)
            
            # Fill form fields
            self._fill_form(application_data)
            
            # Submit application
            submit_button = self._find_submit_button()
            if submit_button:
                submit_button.click()
                time.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error applying to job: {e}")
            return False
    
    def _find_apply_button(self):
        """Find and return the apply button"""
        try:
            # Common button text patterns
            button_texts = ['Apply', 'Apply Now', 'Easy Apply', 'Submit Application']
            
            for text in button_texts:
                try:
                    button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                    return button
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Error finding apply button: {e}")
            return None
    
    def _fill_form(self, data: Dict):
        """Fill form with application data"""
        try:
            # Try to find and fill common form fields
            
            # First name
            if 'first_name' in data:
                self._fill_input_field('first_name', data['first_name'])
                self._fill_input_field('firstName', data['first_name'])
                self._fill_input_field('fname', data['first_name'])
            
            # Last name
            if 'last_name' in data:
                self._fill_input_field('last_name', data['last_name'])
                self._fill_input_field('lastName', data['last_name'])
                self._fill_input_field('lname', data['last_name'])
            
            # Email
            if 'email' in data:
                self._fill_input_field('email', data['email'])
            
            # Phone
            if 'phone' in data:
                self._fill_input_field('phone', data['phone'])
            
            # Resume upload
            if 'resume_path' in data:
                self._upload_file(data['resume_path'])
            
            # Cover letter
            if 'cover_letter' in data:
                self._fill_input_field('message', data['cover_letter'])
                self._fill_input_field('cover_letter', data['cover_letter'])
            
        except Exception as e:
            print(f"Error filling form: {e}")
    
    def _fill_input_field(self, field_id_or_name: str, value: str):
        """Fill input field by id or name"""
        try:
            # Try by id
            try:
                input_field = self.driver.find_element(By.ID, field_id_or_name)
                input_field.clear()
                input_field.send_keys(value)
                return
            except:
                pass
            
            # Try by name
            try:
                input_field = self.driver.find_element(By.NAME, field_id_or_name)
                input_field.clear()
                input_field.send_keys(value)
                return
            except:
                pass
            
            # Try by xpath with placeholder or label
            input_field = self.driver.find_element(
                By.XPATH, 
                f"//input[@placeholder='{field_id_or_name}' or @id='{field_id_or_name}']"
            )
            input_field.clear()
            input_field.send_keys(value)
            
        except Exception as e:
            print(f"Could not fill field {field_id_or_name}: {e}")
    
    def _upload_file(self, file_path: str):
        """Upload file to the form"""
        try:
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(file_path)
        except Exception as e:
            print(f"Could not upload file: {e}")
    
    def _find_submit_button(self):
        """Find and return the submit button"""
        try:
            submit_texts = ['Submit', 'Send', 'Apply', 'Confirm', 'Apply Now']
            
            for text in submit_texts:
                try:
                    button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                    return button
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Error finding submit button: {e}")
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
