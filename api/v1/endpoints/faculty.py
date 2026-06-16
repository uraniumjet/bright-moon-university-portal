"""
The Bright Moon University - Faculty Core Operations Router
File: api/v1/endpoints/faculty.py
Description: Processes attendance sheets, curriculum document loads, and grade reports compilation.
"""

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlmodel import Session, select
from database.connection import get_session
from models.academic import Grade, Enrollment

router = APIRouter(prefix="/faculty", tags=["Faculty Evaluation Desk"])

@router.post("/submit-grade/{enrollment_id}")
async def process_grade_entry(
    enrollment_id: int,
    ca_score: float = Form(...),
    exam_score: float = Form(...),
    session: Session = Depends(get_session)
):
    total = ca_score + exam_score
    if total >= 80: letter = "A"
    elif total >= 70: letter = "B"
    elif total >= 60: letter = "C"
    elif total >= 50: letter = "D"
    else: letter = "F"
    
    stmt = select(Grade).where(Grade.enrollment_id == enrollment_id)
    grade_entry = session.exec(stmt).first()
    
    if grade_entry:
        if grade_entry.is_released:
            raise HTTPException(status_code=403, detail="Grading Sheet is locked. Released scores cannot be modified without Exam Office clearance.")
        grade_entry.continuous_assessment = ca_score
        grade_entry.final_exam = exam_score
        grade_entry.total_score = total
        grade_entry.letter_grade = letter
    else:
        grade_entry = Grade(
            enrollment_id=enrollment_id, continuous_assessment=ca_score,
            final_exam=exam_score, total_score=total, letter_grade=letter, is_released=False
        )
    
    session.add(grade_entry)
    session.commit()
    return {"status": "Grade saved locally. Pending compilation delivery to Exam Office."}