import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Azure AI Configuration
    azure_ai_endpoint: str = os.getenv("AZURE_AI_ENDPOINT", "")
    azure_ai_key: str = os.getenv("AZURE_AI_KEY", "")
    azure_ai_model: str = os.getenv("AZURE_AI_MODEL", "gpt-4")
    
    # Jira Configuration
    jira_url: str = os.getenv("JIRA_URL", "")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")
    jira_project_key: str = os.getenv("JIRA_PROJECT_KEY", "TEST")
    
    # Application Settings
    max_retries: int = 3
    timeout: int = 30
    log_level: str = "INFO"

settings = Settings()
