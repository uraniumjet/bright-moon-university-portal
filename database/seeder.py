"""
The Bright Moon University - Comprehensive System Core Seeder Engine
File: database/seeder.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session
from database.connection import engine, init_db
from core.security import hash_password
from models import (
    UserAccount, StudentProfile, FacultyProfile, SupportStaffProfile,
    Course, CourseAllocation, Enrollment, Grade, LmsResource, ServiceRequest
)

def seed_academic_ecosystem():
    print("⏳ Launching System Seeder Sequence for The Bright Moon University...")
    
    if os.path.exists("bright_moon.db"):
        os.remove("bright_moon.db")
        print("🗑️ Resetting existing database file layer...")
        
    init_db()
    
    with Session(engine) as session:
        print("🔐 Provisioning access credential accounts...")
        default_hash = hash_password("Password123")
        
        users = [
            UserAccount(username="ADMIN-001", hashed_password=default_hash, role="onboarder", requires_password_reset=False),
            UserAccount(username="UR-2026-0001", hashed_password=default_hash, role="student", requires_password_reset=True),
            UserAccount(username="FACULTY-001", hashed_password=default_hash, role="faculty", requires_password_reset=True),
            UserAccount(username="STAFF-001", hashed_password=default_hash, role="bursary", requires_password_reset=True),
            UserAccount(username="EXAM-OFFICE", hashed_password=default_hash, role="exam_office", requires_password_reset=False),
        ]
        session.add_all(users)
        
        print("👤 Instantiating deep profile entities...")
        
        # Extended Student Profile Seeding
        student_me = StudentProfile(
            student_id="UR-2026-0001",
            student_name="Yusuf Ahmad Shehu",
            age=24,
            sex="Male",
            profile_pic="/storage/avatars/students/ur-2026-0001.jpg",
            header_faculty="Faculty of Science & Engineering",
            course_specialization="Cyber Security & AI",
            academic_level="M.Sc.",
            current_semester=1,
            attendance_pct=88.5,
            phone_number="+2348012345678",
            email_address="yusuf@brightmoon.edu.ng",
            guardian_name="Alhaji Ahmad Shehu",
            guardian_phone="+2348098765432",
            guardian_relation="Father",
            is_boarding=True,
            hostel_block="Titanium Hall",
            room_number="Room-404"
        )
        
        # Extended Faculty Profile Seeding
        lecturer_dean = FacultyProfile(
            faculty_id="FACULTY-001",
            faculty_name="Dr. Abdullahi Sani Jibril",
            age=42,
            sex="Male",
            profile_pic="/storage/avatars/faculty/faculty-001.jpg",
            department="Cyber Security & AI",
            academic_rank="Dean of Engineering Informatics",
            office_cabin="TechHub-Block A",
            phone_number="+2347011223344",
            email_address="a.jibril@brightmoon.edu.ng"
        )
        
        # Extended Non-Academic / Bursary Profile Seeding
        bursar_staff = SupportStaffProfile(
            staff_id="STAFF-001",
            staff_name="Amina Abdullahi",
            age=35,
            sex="Female",
            profile_pic="/storage/avatars/staff/staff-001.jpg",
            department="Bursary",
            assigned_role="Chief Revenue Accountant",
            office_cabin="AdminBlock-Room 12",
            phone_number="+2349055667788",
            email_address="a.abdullahi@brightmoon.edu.ng"
        )
        
        session.add(student_me)
        session.add(lecturer_dean)
        session.add(bursar_staff)
        
        print("📚 Publishing comprehensive module options...")
        courses = [
            Course(course_code="CS-601", title="Advanced Cyber Security & Cryptography", credit_hours=4, academic_level="M.Sc."),
            Course(course_code="CS-301", title="Introduction to Computer Networks", credit_hours=3, academic_level="B.Sc.")
        ]
        session.add_all(courses)
        session.flush()
        
        enrollments = [
            Enrollment(student_id="UR-2026-0001", course_code="CS-601", semester=1)
        ]
        session.add_all(enrollments)
        session.flush()
        
        grade_1 = Grade(
            enrollment_id=enrollments[0].id,
            continuous_assessment=38.0,
            final_exam=56.5,
            total_score=94.5,
            letter_grade="A",
            is_released=True
        )
        session.add(grade_1)
        session.commit()
        print("🎉 Relational Academic Database Upgrade Seeded Successfully!")

if __name__ == "__main__":
    seed_academic_ecosystem()