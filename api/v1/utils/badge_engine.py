"""
The Bright Moon University - Centralized Identity Resolution Matrix
File: api/v1/utils/badge_engine.py
Description: Safely extracts profile properties across different tenant models for UI & PDF layouts.
"""

from sqlmodel import Session, select
from database.connection import engine
from models.academic import StudentProfile, FacultyProfile, SupportStaffProfile

def get_clean_badge_context(user_id: str):
    """
    Queries the database across multi-tenant profile tables 
    and sanitizes the field names into a unified output schema.
    """
    with Session(engine) as session:
        # 1. Resolve Student Matrix Link
        if "UR-" in user_id:
            profile = session.exec(select(StudentProfile).where(StudentProfile.student_id == user_id)).first()
            if profile:
                return {
                    "id": profile.student_id,
                    "name": profile.student_name,
                    "role": f"STUDENT ({profile.academic_level})",
                    "department": profile.course_specialization,
                    "pic": profile.profile_pic or "/static/assets/default_avatar.png"
                }
        
        # 2. Resolve Teaching Faculty Matrix Link
        if "FAC-" in user_id:
            profile = session.exec(select(FacultyProfile).where(FacultyProfile.faculty_id == user_id)).first()
            if profile:
                return {
                    "id": profile.faculty_id,
                    "name": profile.faculty_name,
                    "role": profile.academic_rank.upper(),
                    "department": profile.department,
                    "pic": profile.profile_pic or "/static/assets/default_avatar.png"
                }
                
        # 3. Fallback: Resolve Support / Bursary / Non-Academic Staff
        profile = session.exec(select(SupportStaffProfile).where(SupportStaffProfile.staff_id == user_id)).first()
        if profile:
            return {
                "id": profile.staff_id,
                "name": profile.staff_name,
                "role": profile.assigned_role.upper(),
                "department": profile.department,
                "pic": profile.profile_pic or "/static/assets/default_avatar.png"
            }
            
        # Default safety fallback state
        return {
            "id": user_id, 
            "name": "UNKNOWN IDENTITY", 
            "role": "NOT SPECIFIED", 
            "department": "GENERAL", 
            "pic": "/static/assets/default_avatar.png"
        }