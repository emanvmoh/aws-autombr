import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_PROFILE = os.getenv('AWS_PROFILE', 'default')
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
    
    OUTLOOK_CLIENT_ID = os.getenv('OUTLOOK_CLIENT_ID')
    OUTLOOK_CLIENT_SECRET = os.getenv('OUTLOOK_CLIENT_SECRET')
    OUTLOOK_TENANT_ID = os.getenv('OUTLOOK_TENANT_ID')
    OUTLOOK_AUTHORITY = f"https://login.microsoftonline.com/{os.getenv('OUTLOOK_TENANT_ID', 'common')}"
    OUTLOOK_SCOPE = ["https://graph.microsoft.com/Mail.Read"]
    
    ALLOWED_EXTENSIONS = {'pptx', 'pdf', 'txt', 'docx'}
