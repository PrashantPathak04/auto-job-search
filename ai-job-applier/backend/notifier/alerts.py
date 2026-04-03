import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import os
from datetime import datetime

class AlertNotifier:
    def __init__(self):
        """Initialize alert notifier"""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
    
    def send_application_alert(self, recipient_email: str, job_title: str, company: str, url: str) -> bool:
        """
        Send email alert when application is submitted
        
        Args:
            recipient_email: Recipient email address
            job_title: Job title
            company: Company name
            url: Job posting URL
            
        Returns:
            True if email was sent successfully
        """
        subject = f"✓ Application Submitted - {job_title} at {company}"
        
        body = f"""
        <html>
            <body>
                <h2>Application Submitted Successfully!</h2>
                <p><strong>Job Title:</strong> {job_title}</p>
                <p><strong>Company:</strong> {company}</p>
                <p><strong>Applied On:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><a href="{url}">View Job Posting</a></p>
                <hr>
                <p><em>This is an automated notification from AI Job Applier</em></p>
            </body>
        </html>
        """
        
        return self._send_email(recipient_email, subject, body)
    
    def send_daily_summary(self, recipient_email: str, applications: List[dict]) -> bool:
        """
        Send daily summary of job applications
        
        Args:
            recipient_email: Recipient email address
            applications: List of application dictionaries
                - job_title: str
                - company: str
                - status: str
                
        Returns:
            True if email was sent successfully
        """
        subject = f"Daily Job Application Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        applications_html = ""
        for app in applications:
            status_color = "green" if app.get('status') == 'applied' else "orange"
            applications_html += f"""
                <tr>
                    <td>{app.get('job_title', 'N/A')}</td>
                    <td>{app.get('company', 'N/A')}</td>
                    <td><span style="color: {status_color};">{app.get('status', 'N/A')}</span></td>
                </tr>
            """
        
        body = f"""
        <html>
            <body>
                <h2>Daily Job Application Summary</h2>
                <p>Total Applications Today: <strong>{len(applications)}</strong></p>
                
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <th style="padding: 10px;">Job Title</th>
                        <th style="padding: 10px;">Company</th>
                        <th style="padding: 10px;">Status</th>
                    </tr>
                    {applications_html}
                </table>
                
                <hr>
                <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            </body>
        </html>
        """
        
        return self._send_email(recipient_email, subject, body)
    
    def send_error_alert(self, recipient_email: str, error_message: str) -> bool:
        """
        Send alert for application errors
        
        Args:
            recipient_email: Recipient email address
            error_message: Error message details
            
        Returns:
            True if email was sent successfully
        """
        subject = "⚠ AI Job Applier - Error Alert"
        
        body = f"""
        <html>
            <body>
                <h2>Application Error</h2>
                <p>An error occurred in your job application process:</p>
                <p><code>{error_message}</code></p>
                <p>Please check your account and settings.</p>
                <hr>
                <p><em>Error occurred on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            </body>
        </html>
        """
        
        return self._send_email(recipient_email, subject, body)
    
    def _send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Send email using SMTP
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body (HTML)
            
        Returns:
            True if email was sent successfully
        """
        try:
            if not self.sender_email or not self.sender_password:
                print("SMTP credentials not configured. Email not sent.")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Add HTML content
            part = MIMEText(body, "html")
            message.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            print(f"Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
