import msal
import requests
from config import Config

class OutlookService:
    def __init__(self):
        self.client_id = Config.OUTLOOK_CLIENT_ID
        self.client_secret = Config.OUTLOOK_CLIENT_SECRET
        self.authority = Config.OUTLOOK_AUTHORITY
        self.scope = Config.OUTLOOK_SCOPE
        self.token = None
    
    def get_auth_url(self, redirect_uri):
        app = msal.ConfidentialClientApplication(self.client_id, authority=self.authority, client_credential=self.client_secret)
        return app.get_authorization_request_url(self.scope, redirect_uri=redirect_uri)
    
    def get_token_from_code(self, code, redirect_uri):
        app = msal.ConfidentialClientApplication(self.client_id, authority=self.authority, client_credential=self.client_secret)
        result = app.acquire_token_by_authorization_code(code, scopes=self.scope, redirect_uri=redirect_uri)
        if "access_token" in result:
            self.token = result["access_token"]
            return True
        return False
    
    def search_customer_emails(self, customer_name, days=90):
        if not self.token:
            return self._mock_email_data(customer_name)
        try:
            headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
            search_query = f"$search=\"{customer_name}\"&$top=50"
            url = f"https://graph.microsoft.com/v1.0/me/messages?{search_query}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                emails = response.json().get('value', [])
                topics = []
                for email in emails[:20]:
                    topics.append({
                        'subject': email.get('subject', ''),
                        'from': email.get('from', {}).get('emailAddress', {}).get('name', ''),
                        'received': email.get('receivedDateTime', ''),
                        'preview': email.get('bodyPreview', '')[:200]
                    })
                return topics
            else:
                return self._mock_email_data(customer_name)
        except Exception as e:
            print(f"Outlook API error: {e}")
            return self._mock_email_data(customer_name)
    
    def _mock_email_data(self, customer_name):
        return [
            {'subject': f'Re: {customer_name} - Q1 Architecture Review', 'from': 'Customer CTO',
             'received': '2026-02-15', 'preview': 'Planning to migrate monolith to microservices, need guidance on ECS vs EKS...'},
            {'subject': f'{customer_name} - Cost optimization', 'from': 'Customer CFO',
             'received': '2026-02-10', 'preview': 'AWS costs increased 30% this quarter. Can we review optimization opportunities?'},
            {'subject': f'Re: {customer_name} RDS Performance', 'from': 'Customer DevOps Lead',
             'received': '2026-02-08', 'preview': 'RDS instance experiencing slow queries during peak hours. Opened support case...'}
        ]
