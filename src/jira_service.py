import logging
from typing import List, Optional, Dict, Any
from atlassian import Jira
from models import TestCase, JiraIssue
from config import settings

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self):
        self.jira = Jira(
            url=settings.jira_url,
            username=settings.jira_email,
            password=settings.jira_api_token,
            cloud=True
        )
        
    def _format_test_case_description(self, test_case: TestCase) -> str:
        """Format test case as Jira description."""
        description = f"*Description:* {test_case.description}\n\n"
        
        if test_case.preconditions:
            description += "*Preconditions:*\n"
            for precondition in test_case.preconditions:
                description += f"• {precondition}\n"
            description += "\n"
        
        if test_case.test_steps:
            description += "*Test Steps:*\n"
            for step in test_case.test_steps:
                description += f"{step.step_number}. {step.action}\n"
                description += f"   _Expected Result:_ {step.expected_result}\n\n"
        
        description += f"*Expected Outcome:* {test_case.expected_outcome}\n\n"
        
        if test_case.test_data:
            description += f"*Test Data:* {test_case.test_data}\n\n"
        
        description += f"*Test Type:* {test_case.test_type.value}\n"
        description += f"*Priority:* {test_case.priority.value}"
        
        return description

    def create_test_issue(self, test_case: TestCase, parent_key: Optional[str] = None) -> Optional[str]:
        """Create a test issue in Jira."""
        try:
            issue_data = {
                'project': {'key': settings.jira_project_key},
                'summary': test_case.title,
                'description': self._format_test_case_description(test_case),
                'issuetype': {'name': 'Test'},
                'priority': {'name': test_case.priority.value},
            }
            
            if test_case.labels:
                issue_data['labels'] = test_case.labels
            
            if parent_key:
                issue_data['parent'] = {'key': parent_key}
            
            issue = self.jira.create_issue(fields=issue_data)
            issue_key = issue['key']
            
            logger.info(f"Created test issue: {issue_key}")
            return issue_key
            
        except Exception as e:
            logger.error(f"Failed to create Jira issue: {e}")
            return None

    def link_issues(self, source_key: str, target_key: str, link_type: str = "Tests") -> bool:
        """Create a link between two Jira issues."""
        try:
            self.jira.create_issue_link(
                type=link_type,
                inwardIssue=source_key,
                outwardIssue=target_key
            )
            logger.info(f"Linked {source_key} to {target_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to link issues: {e}")
            return False

    def get_project_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Retrieve issues from Jira using JQL."""
        try:
            issues = self.jira.jql(jql)
            return issues.get('issues', [])
        except Exception as e:
            logger.error(f"Failed to retrieve issues: {e}")
            return []

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """Update an existing Jira issue."""
        try:
            self.jira.update_issue_field(issue_key, fields)
            logger.info(f"Updated issue: {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to update issue {issue_key}: {e}")
            return False
