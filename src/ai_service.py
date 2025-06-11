import json
import logging
from typing import List, Dict, Any
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from models import TestCase, UserStory, TestType, Priority
from config import settings

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

class AzureAIService:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=settings.azure_ai_endpoint,
            credential=AzureKeyCredential(settings.azure_ai_key)
        )
        
    def _get_test_case_prompt(self) -> str:
        return """
You are a Senior QA Engineer tasked with creating comprehensive test cases.

Given a user story, generate detailed test cases that cover:
1. Happy path scenarios
2. Edge cases and boundary conditions
3. Negative test scenarios
4. Integration points

For each test case, provide:
- Clear, descriptive title
- Detailed description
- Preconditions (if any)
- Numbered test steps with expected results
- Overall expected outcome
- Test data requirements
- Priority level (Critical/High/Medium/Low)
- Test type (Functional/Integration/Boundary/Negative/Edge Case)
- Relevant labels

Format your response as valid JSON with an array of test cases.
Each test case should follow this structure:
{
    "title": "Test case title",
    "description": "Detailed description",
    "preconditions": ["precondition 1", "precondition 2"],
    "test_steps": [
        {"step_number": 1, "action": "action description", "expected_result": "expected result"},
        {"step_number": 2, "action": "action description", "expected_result": "expected result"}
    ],
    "expected_outcome": "Overall expected outcome",
    "test_data": "Test data requirements or examples",
    "priority": "High",
    "test_type": "Functional",
    "labels": ["label1", "label2"]
}

Ensure test cases are:
- Comprehensive and cover all acceptance criteria
- Clear and actionable
- Include realistic test data examples
- Properly prioritized based on business impact
"""

    async def generate_test_cases(self, user_story: UserStory) -> List[TestCase]:
        """Generate test cases from a user story using Azure AI."""
        try:
            story_text = f"""
Title: {user_story.title}
Description: {user_story.description}
Acceptance Criteria: {' | '.join(user_story.acceptance_criteria)}
"""
            
            messages = [
                SystemMessage(content=self._get_test_case_prompt()),
                UserMessage(content=story_text)
            ]
            
            response = self.client.complete(
                messages=messages,
                model=settings.azure_ai_model,
                max_tokens=4000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            test_cases_data = json.loads(content)
            test_cases = []
            
            for tc_data in test_cases_data:
                test_case = TestCase(**tc_data)
                test_cases.append(test_case)
                
            logger.info(f"Generated {len(test_cases)} test cases for story: {user_story.title}")
            return test_cases
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            raise

    async def validate_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Validate a test case for completeness and quality."""
        validation_prompt = """
You are a QA Lead reviewing test cases for quality and completeness.

Evaluate the following test case and provide feedback on:
1. Clarity of test steps
2. Completeness of coverage
3. Realistic test data
4. Appropriate priority level
5. Missing elements

Respond with JSON format:
{
    "is_valid": true/false,
    "quality_score": 1-10,
    "feedback": "Detailed feedback",
    "suggestions": ["suggestion 1", "suggestion 2"]
}
"""
        
        try:
            messages = [
                SystemMessage(content=validation_prompt),
                UserMessage(content=test_case.model_dump_json(indent=2))
            ]
            
            response = self.client.complete(
                messages=messages,
                model=settings.azure_ai_model,
                max_tokens=1000,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error validating test case: {e}")
            return {"is_valid": True, "quality_score": 5, "feedback": "Validation failed", "suggestions": []}
