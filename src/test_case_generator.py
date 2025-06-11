import asyncio
import logging
from typing import List, Optional, Dict, Any
from ai_service import AzureAIService
from jira_service import JiraService
from models import UserStory, TestCase, JiraIssue
from config import settings

logger = logging.getLogger(__name__)

class TestCaseGenerator:
    def __init__(self):
        self.ai_service = AzureAIService()
        self.jira_service = JiraService()
        
    async def process_user_story(self, user_story: UserStory, parent_story_key: Optional[str] = None) -> Dict[str, Any]:
        """Process a user story and generate test cases in Jira."""
        results = {
            'user_story': user_story.title,
            'generated_test_cases': 0,
            'created_jira_issues': 0,
            'failed_issues': 0,
            'test_case_keys': [],
            'errors': []
        }
        
        try:
            # Generate test cases using AI
            logger.info(f"Generating test cases for: {user_story.title}")
            test_cases = await self.ai_service.generate_test_cases(user_story)
            results['generated_test_cases'] = len(test_cases)
            
            if not test_cases:
                results['errors'].append("No test cases generated")
                return results
            
            # Create Jira issues for each test case
            for test_case in test_cases:
                try:
                    # Validate test case quality
                    validation = await self.ai_service.validate_test_case(test_case)
                    
                    if validation.get('quality_score', 0) < 6:
                        logger.warning(f"Low quality test case: {test_case.title}")
                        logger.warning(f"Feedback: {validation.get('feedback')}")
                    
                    # Create Jira issue
                    issue_key = self.jira_service.create_test_issue(test_case, parent_story_key)
                    
                    if issue_key:
                        results['test_case_keys'].append(issue_key)
                        results['created_jira_issues'] += 1
                        
                        # Link to parent story if provided
                        if parent_story_key:
                            self.jira_service.link_issues(issue_key, parent_story_key, "Tests")
                            
                    else:
                        results['failed_issues'] += 1
                        results['errors'].append(f"Failed to create issue for: {test_case.title}")
                        
                except Exception as e:
                    results['failed_issues'] += 1
                    results['errors'].append(f"Error processing test case '{test_case.title}': {str(e)}")
                    
            logger.info(f"Completed processing. Created {results['created_jira_issues']} test issues.")
            
        except Exception as e:
            results['errors'].append(f"Error processing user story: {str(e)}")
            logger.error(f"Error processing user story: {e}")
            
        return results

    async def batch_process_stories(self, stories_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple user stories in batch."""
        results = []
        
        for story_data in stories_data:
            try:
                user_story = UserStory(**story_data['story'])
                parent_key = story_data.get('parent_key')
                
                result = await self.process_user_story(user_story, parent_key)
                results.append(result)
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                error_result = {
                    'user_story': story_data.get('story', {}).get('title', 'Unknown'),
                    'errors': [f"Failed to process story: {str(e)}"],
                    'generated_test_cases': 0,
                    'created_jira_issues': 0,
                    'failed_issues': 0,
                    'test_case_keys': []
                }
                results.append(error_result)
                
        return results

    def get_test_coverage_report(self, project_key: str) -> Dict[str, Any]:
        """Generate a test coverage report for a project."""
        try:
            # Get all stories in the project
            stories_jql = f"project = {project_key} AND issuetype = Story"
            stories = self.jira_service.get_project_issues(stories_jql)
            
            # Get all test issues
            tests_jql = f"project = {project_key} AND issuetype = Test"
            tests = self.jira_service.get_project_issues(tests_jql)
            
            # Calculate coverage metrics
            total_stories = len(stories)
            total_tests = len(tests)
            
            # Count stories with linked tests
            stories_with_tests = 0
            for story in stories:
                story_key = story['key']
                linked_tests = [t for t in tests if self._is_linked(story_key, t)]
                if linked_tests:
                    stories_with_tests += 1
            
            coverage_percentage = (stories_with_tests / total_stories * 100) if total_stories > 0 else 0
            
            report = {
                'project_key': project_key,
                'total_stories': total_stories,
                'total_tests': total_tests,
                'stories_with_tests': stories_with_tests,
                'coverage_percentage': round(coverage_percentage, 2),
                'tests_per_story_avg': round(total_tests / total_stories, 2) if total_stories > 0 else 0
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating coverage report: {e}")
            return {}

    def _is_linked(self, story_key: str, test_issue: Dict[str, Any]) -> bool:
        """Check if a test issue is linked to a story."""
        # This is a simplified check - in practice, you'd check issue links
        # For now, we'll check if the story key is mentioned in test description
        description = test_issue.get('fields', {}).get('description', '')
        return story_key in description
