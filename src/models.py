from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TestType(str, Enum):
    FUNCTIONAL = "Functional"
    INTEGRATION = "Integration"
    BOUNDARY = "Boundary"
    NEGATIVE = "Negative"
    EDGE_CASE = "Edge Case"

class Priority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TestStep(BaseModel):
    step_number: int
    action: str
    expected_result: str

class TestCase(BaseModel):
    title: str
    description: str
    preconditions: List[str] = []
    test_steps: List[TestStep] = []
    expected_outcome: str
    test_data: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    test_type: TestType = TestType.FUNCTIONAL
    labels: List[str] = []

class UserStory(BaseModel):
    title: str
    description: str
    acceptance_criteria: List[str] = []
    story_points: Optional[int] = None
    epic_link: Optional[str] = None

class JiraIssue(BaseModel):
    key: Optional[str] = None
    summary: str
    description: str
    issue_type: str = "Test"
    priority: str = "Medium"
    labels: List[str] = []
    parent_key: Optional[str] = None
