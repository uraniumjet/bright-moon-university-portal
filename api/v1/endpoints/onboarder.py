"""
The Bright Moon University - Advanced Multi-Tenant CRUD Onboarding Engine
File: api/v1/endpoints/onboarder.py
Description: Manages full CRUD operations for Students, Faculty, and Non-Academic Staff.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel import Session, select
from database.connection import get_session
from models.auth import UserAccount
from models.academic import StudentProfile, FacultyProfile, SupportStaffProfile
from core.security import hash_password
from typing import Optional

router = APIRouter(prefix="/onboard", tags=["Institutional CRUD Registry"])

# ---------------------------------------------------------
# GROUND-TRUTH CASCOADING STRUCTURE (INSTITUTIONAL ATLAS)
# ---------------------------------------------------------
FACULTY_DEPARTMENT_MAP = {
    "Faculty of Science & Engineering": [
        "Cyber Security & AI", "Software Engineering", "Data Science", 
        "Cloud Computing & DevOps", "Robotics & Automation"
    ],
    "Faculty of Management & Social Sciences": [
        "International Commerce", "Business Analytics", "Fintech & Financial Engineering", "Digital Marketing"
    ],
    "Faculty of Arts & Humanities": [
        "Mass Communication & Digital Media", "English Literature", "UI/UX Design & Creative Arts"
    ],
    "Faculty of Law & Juridical Studies": [
        "Corporate Law", "International Jurisprudence", "Cyber Law & Digital Forensics"
    ],
    "Faculty of Medical & Health Sciences": [
        "Health Informatics", "Nursing & Healthcare Management", "Biomedical Engineering"
    ]
}

@router.get("/faculties-map")
async def get_institutional_map():
    """Exposes the locked master list of faculties and departments for dropdown filters."""
    return FACULTY_DEPARTMENT_MAP

# ---------------------------------------------------------
# CREATE OPERATIONS (PROVISIONING WITH DEEP BIOMETRICS)
# ---------------------------------------------------------

@router.post("/student", status_code=status.HTTP_201_CREATED)
async def create_student_profile(
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...),
    faculty: str = Form(...),
    department: str = Form(...),
    level: str = Form(...), # "Diploma", "HND", "B.Sc.", "M.Sc.", etc.
    phone: str = Form(...),
    email: str = Form(...),
    guardian_name: str = Form(...),
    guardian_phone: str = Form(...),
    guardian_relation: str = Form(...),
    is_boarding: bool = Form(False),
    hostel_block: Optional[str] = Form(None),
    room_number: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    if faculty not in FACULTY_DEPARTMENT_MAP or department not in FACULTY_DEPARTMENT_MAP[faculty]:
        raise HTTPException(status_code=400, detail="Academic placement deviation: Department mismatch against Faculty cluster.")

    student_count = len(session.exec(select(StudentProfile)).all())
    generated_id = f"UR-2026-{1000 + student_count + 1}"
    
    default_pass = hash_password("Password123")
    account = UserAccount(username=generated_id, hashed_password=default_pass, role="student", requires_password_reset=True)
    
    profile = StudentProfile(
        student_id=generated_id, student_name=name, age=age, sex=sex,
        profile_pic=f"/storage/avatars/students/{generated_id}.jpg", # Standardized link format
        header_faculty=faculty, course_specialization=department, academic_level=level,
        phone_number=phone, email_address=email, guardian_name=guardian_name,
        guardian_phone=guardian_phone, guardian_relation=guardian_relation,
        is_boarding=is_boarding, hostel_block=hostel_block, room_number=room_number
    )
    
    session.add(account)
    session.add(profile)
    session.commit()
    return {"status": "Success", "generated_id": generated_id}


@router.post("/staff", status_code=status.HTTP_201_CREATED)
async def create_staff_profile(
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...),
    department: str = Form(...), # "Bursary", "Registry", "Security", etc.
    role: str = Form(...), # e.g., "Chief Accountant"
    cabin: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    session: Session = Depends(get_session)
):
    staff_count = len(session.exec(select(SupportStaffProfile)).all()) + len(session.exec(select(FacultyProfile)).all())
    generated_id = f"STAFF-2026-{500 + staff_count + 1}"
    
    user_role = "bursary" if department.lower() == "bursary" else "faculty" if department.lower() in [f.lower() for f in FACULTY_DEPARTMENT_MAP] else "non_academic"
    default_pass = hash_password("Password123")
    account = UserAccount(username=generated_id, hashed_password=default_pass, role=user_role, requires_password_reset=True)
    
    if user_role == "faculty":
        profile = FacultyProfile(
            faculty_id=generated_id, faculty_name=name, age=age, sex=sex,
            profile_pic=f"/storage/avatars/faculty/{generated_id}.jpg",
            department=department, academic_rank=role, office_cabin=cabin,
            phone_number=phone, email_address=email
        )
    else:
        profile = SupportStaffProfile(
            staff_id=generated_id, staff_name=name, age=age, sex=sex,
            profile_pic=f"/storage/avatars/staff/{generated_id}.jpg",
            department=department, assigned_role=role, office_cabin=cabin,
            phone_number=phone, email_address=email
        )
        
    session.add(account)
    session.add(profile)
    session.commit()
    return {"status": "Success", "generated_id": generated_id}

# ---------------------------------------------------------
# UPDATE & DELETE OPERATIONS (CRUD ADMINISTRATIVE OVERWRITE)
# ---------------------------------------------------------

@router.post("/update/student/{student_id}")
async def update_student_record(
    student_id: str,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    hostel_block: Optional[str] = Form(None),
    room_number: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """Allows immediate administrative corrections if mistakes occur."""
    profile = session.exec(select(StudentProfile).where(StudentProfile.student_id == student_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student target record not found.")
        
    profile.student_name = name
    profile.phone_number = phone
    profile.email_address = email
    profile.hostel_block = hostel_block
    profile.room_number = room_number
    
    session.add(profile)
    session.commit()
    return {"status": "Success", "message": f"Student record {student_id} updated successfully."}


@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
async def purge_user_account(user_id: str, session: Session = Depends(get_session)):
    """Completely deletes a user account and their profile row from the system database."""
    account = session.exec(select(UserAccount).where(UserAccount.username == user_id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Target user account does not exist.")
        
    # Delete from the profile tables based on role mapping types
    if account.role == "student":
        profile = session.exec(select(StudentProfile).where(StudentProfile.student_id == user_id)).first()
    elif account.role == "faculty":
        profile = session.exec(select(FacultyProfile).where(FacultyProfile.faculty_id == user_id)).first()
    else:
        profile = session.exec(select(SupportStaffProfile).where(SupportStaffProfile.staff_id == user_id)).first()
        
    if profile:
        session.delete(profile)
    session.delete(account)
    session.commit()
    return {"status": "Success", "message": f"Account {user_id} completely removed from institutional registry."}