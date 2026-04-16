from typing import Optional
from pydantic import BaseModel


class CMInputs(BaseModel):
    """Input storage for the CollegeMaxxing AI service."""

    session_id: Optional[str] = None
    intended_university: Optional[str] = None
    user_essay: Optional[str] = None
    user_interview_response: Optional[str] = None
    essay_file_name: Optional[str] = None
    notes: Optional[str] = None
    sat_score: Optional[int] = None
    gpa: Optional[int] = None
    essay_pdf_bytes: Optional[bytes] = None
    result: Optional[str] = None
    