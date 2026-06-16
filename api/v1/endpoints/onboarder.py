"""
The Bright Moon University - Identity Provisioning Admin Endpoints
File: api/v1/endpoints/onboarder.py
Description: Extensible processing controls for onboarding students and faculty profiles.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel import Session, select
from database.connection import get_session
from models.auth import UserAccount
from models.academic import StudentProfile, FacultyProfile
from core.security import hash_password

router = APIRouter(prefix="/onboard", tags=["Identity Provisioning Engine"])

@router.post("/student", status_code=status.HTTP_201_CREATED)
async def onboard_new_student(
    name: str = Form(...),
    faculty: str = Form(...),
    specialization: str = Form(...),
    level: str = Form(...),  # "B.Sc." or "M.Sc."
    session: Session = Depends(get_session)
):
    # Calculate a unique sequential metric based on current records size
    student_count = len(session.exec(select(StudentProfile)).all())
    generated_id = f"UR-2026-{1000 + student_count + 1}"
    
    # Check for safety conflicts
    if session.exec(select(UserAccount).where(UserAccount.username == generated_id)).first():
        raise HTTPException(status_code=400, detail="Generated matriculation key collision encountered.")
        
    # Generate credential baseline account
    default_pass = hash_password("Password123")
    account = UserAccount(username=generated_id, hashed_password=default_pass, role="student", requires_password_reset=True)
    
    # Establish the student biometric data row
    profile = StudentProfile(
        student_id=generated_id, student_name=name, faculty_name=faculty,
        course_specialization=specialization, academic_level=level
    )
    
    session.add(account)
    session.add(profile)
    session.commit()
    
    return {"status": "Success", "generated_id": generated_id, "temporary_password": "Password123"}


@router.post("/faculty", status_code=status.HTTP_201_CREATED)
async def onboard_new_faculty(
    name: str = Form(...),
    department: str = Form(...),
    rank: str = Form(...),
    session: Session = Depends(get_session)
):
    faculty_count = len(session.exec(select(FacultyProfile)).all())
    generated_id = f"FACULTY-{100 + faculty_count + 1}"
    
    default_pass = hash_password("Password123")
    account = UserAccount(username=generated_id, hashed_password=default_pass, role="faculty", requires_password_reset=True)
    
    profile = FacultyProfile(
        faculty_id=generated_id, faculty_name=name, department=department, academic_rank=rank
    )
    
    session.add(account)
    session.add(profile)
    session.commit()
    
    return {"status": "Success", "generated_id": generated_id, "temporary_password": "Password123"}