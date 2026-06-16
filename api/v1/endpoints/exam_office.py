"""
The Bright Moon University - Examination Office Operations Control
File: api/v1/endpoints/exam_office.py
Description: Handles mass grade approvals and student visibility release toggles.
"""

from fastapi import APIRouter, Depends, Form, status
from sqlmodel import Session, select
from database.connection import get_session
from models.academic import Grade, Enrollment

router = APIRouter(prefix="/exam-office", tags=["Examination Office Clearance Board"])

@router.post("/release-course/{course_code}")
async def approve_and_release_term_report(
    course_code: str,
    session: Session = Depends(get_session)
):
    """
    Finds all grade records tied to an active course code and flips their 
    is_released status boolean flag to True, instantly updating the student transcripts.
    """
    statement = select(Grade).join(Enrollment, Enrollment.id == Grade.enrollment_id).where(Enrollment.course_code == course_code)
    grades_to_release = session.exec(statement).all()
    
    for grade in grades_to_release:
        grade.is_released = True
        session.add(grade)
        
    session.commit()
    return {"status": "Success", "message": f"All grade evaluation lines for module {course_code} are officially released campus-wide."}