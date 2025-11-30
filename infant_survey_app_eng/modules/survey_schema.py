
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# Blueprint for individual questions
class Question(BaseModel):
    id: str
    # '...' means "This value is mandatory" (Error if missing)
    age: str = Field(..., description="Age Group")
    category: str = Field(..., description="Category")
    qtype: str = Field(..., description="Response Format")
    text: str = Field(..., description="Question Text")

    # Optional[...] = None means "This value is optional".
    # Prevents errors if these fields are empty in the source data.
    number: Optional[str] = None
    options: Optional[List[str]] = None
    help: Optional[str] = None
    criteria: Optional[str] = None
    actions: Optional[str] = None
    counseling: Optional[str] = None
    item_guide: Optional[str] = None
    positive_parenting: Optional[str] = None
    caution: Optional[str] = None
    caregiver_note: Optional[str] = None
    pe_item: Optional[str] = None
    pe_caution: Optional[str] = None
    judgment: Optional[str] = None
    edu_topic: Optional[str] = None

    # Space to store user answers within the app
    answer: Optional[Any] = None
    age_info: Optional[Dict[str, Any]] = None
    age_keys: Optional[List[str]] = None

# Blueprint for the entire Survey Pack
class SurveyPack(BaseModel):
    meta: Optional[Dict[str, Any]] = None
    questions: List[Question]  # List of Questions
