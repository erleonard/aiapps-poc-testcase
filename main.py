import asyncio
import json
import logging
from typing import Dict, Any
from test_case_generator import TestCaseGenerator
from models import UserStory
from config import settings

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point."""
    generator = TestCaseGenerator()
    
    # Example user story
    sample_story = UserStory(
        title="User Login Functionality",
        description="As a user, I want to log into the system using my email and password so that I can access my account.",
        acceptance_criteria=[
            "User can enter email and password",
            "System validates credentials",
            "User is redirected to dashboard on successful login",
            "Error message is shown for invalid credentials",
            "Account is locked after 3 failed attempts"
        ]
    )
    
    # Process single story
    logger.info("Processing sample user story...")
    result = await generator.process_user_story(sample_story)
    
    print("\n=== PROCESSING RESULTS ===")
    print(json.dumps(result, indent=2))
    
    # Generate coverage report
    logger.info("Generating test coverage report...")
    coverage_report = generator.get_test_coverage_report(settings.jira_project_key)
    
    print("\n=== COVERAGE REPORT ===")
    print(json.dumps(coverage_report, indent=2))

def run_batch_example():
    """Example of batch processing multiple stories."""
    generator = TestCaseGenerator()
    
    stories_data = [
        {
            'story': {
                'title': 'User Registration',
                'description': 'As a new user, I want to create an account',
                'acceptance_criteria': [
                    'User can enter registration details',
                    'Email validation is performed',
                    'Confirmation email is sent'
                ]
            },
            'parent_key': 'PROJ-123'  # Optional parent story key
        },
        {
            'story': {
                'title': 'Password Reset',
                'description': 'As a user, I want to reset my forgotten password',
                'acceptance_criteria': [
                    'User can request password reset',
                    'Reset link is sent via email',
                    'User can set new password'
                ]
            }
        }
    ]
    
    async def process_batch():
        results = await generator.batch_process_stories(stories_data)
        print("\n=== BATCH PROCESSING RESULTS ===")
        for result in results:
            print(json.dumps(result, indent=2))
            print("-" * 50)
    
    asyncio.run(process_batch())

if __name__ == "__main__":
    print("Azure AI Foundry + Jira Test Case Generator")
    print("===========================================")
    
    # Run main example
    asyncio.run(main())
    
    # Uncomment to run batch processing example
    # run_batch_example()
