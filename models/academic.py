"""
The Bright Moon University - Expanded Academic & Institutional Relational Blueprint
File: models/academic.py
Description: Models expanded with deep biometrics, diverse degree options, and staff definitions.
"""

from typing import Optional
from sqlmodel import SQLModel, Field

class StudentProfile(SQLModel, table=True):
    """Deep structural identity matrix for matriculated student candidates."""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(unique=True, index=True) # Unified login link reference
    student_name: str
    age: int
    sex: str # "Male" or "Female"
    profile_pic: str # Storage target: /storage/avatars/students/id.jpg
    
    # Academic Placement Blocks
    header_faculty: str # e.g., "Faculty of Science & Engineering"
    course_specialization: str # e.g., "Cyber Security & AI"
    academic_level: str # "Diploma", "HND", "B.Sc.", "B.Eng.", "B.A.", "M.Sc.", "Ph.D."
    current_semester: int = Field(default=1)
    attendance_pct: float = Field(default=100.0)
    
    # Communications Ledgers
    phone_number: str
    email_address: str
    
    # Emergency Ledger / Next of Kin
    guardian_name: str
    guardian_phone: str
    guardian_relation: str # e.g., "Father", "Sponsor"
    
    # Integrated Residential Architecture Parameters
    is_boarding: bool = Field(default=False)
    hostel_block: Optional[str] = Field(default=None) 
    room_number: Optional[str] = Field(default=None)   


class FacultyProfile(SQLModel, table=True):
    """Deep identity matrix for appointed instructional lecturing staff."""
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: str = Field(unique=True, index=True) 
    faculty_name: str
    age: int
    sex: str
    profile_pic: str # Target: /storage/avatars/faculty/id.jpg
    
    # Institutional Placements
    department: str # e.g., "Cyber Security & AI"
    academic_rank: str # e.g., "Associate Professor", "Senior Lecturer"
    office_cabin: str # e.g., "TechHub-Cabin 4B"
    
    # Communications Deck
    phone_number: str
    email_address: str


class SupportStaffProfile(SQLModel, table=True):
    """
    Identity matrix for Non-Academic & Bursary Staff.
    Keeps the database extensible without modifying Student or Faculty logic.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    staff_id: str = Field(unique=True, index=True) # Unified login link reference
    staff_name: str
    age: int
    sex: str
    profile_pic: str # Target: /storage/avatars/staff/id.jpg
    
    # Operational Placement
    department: str # "Bursary", "Registry", "Security", "Maintenance", "IT Support"
    assigned_role: str # e.g., "Chief Accountant", "Network Administrator"
    office_cabin: str
    
    # Communications Deck
    phone_number: str
    email_address: str


# =========================================================================
# CORE ACADEMIC MODULES & EVALUATION MATRIX STRUCTURES
# =========================================================================

class Course(SQLModel, table=True):
    """Unified university catalog specifying weighted academic modules."""
    id: Optional[int] = Field(default=None, primary_key=True)
    course_code: str = Field(unique=True, index=True) # e.g., "CS-601"
    title: str
    credit_hours: int
    academic_level: str # Match filtering for B.Sc., M.Sc., Diploma, HND tracks


class CourseAllocation(SQLModel, table=True):
    """
    Decoupled Cross-Level Routing Bridge.
    Maps a FacultyProfile instructor to multiple Courses across domains.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: str = Field(foreign_key="facultyprofile.faculty_id", index=True)
    course_code: str = Field(foreign_key="course.course_code", index=True)
    semester: int


class Enrollment(SQLModel, table=True):
    """Relational bridge connecting a single Student to a single Course."""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(foreign_key="studentprofile.student_id", index=True)
    course_code: str = Field(foreign_key="course.course_code", index=True)
    semester: int


class Grade(SQLModel, table=True):
    """
    Institutional Evaluation Sheet.
    Bound 1-to-1 with an Enrollment ID. Features the Exam Office visibility pipeline.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    enrollment_id: int = Field(foreign_key="enrollment.id", unique=True, index=True)
    continuous_assessment: float = Field(default=0.0) 
    final_exam: float = Field(default=0.0) 
    total_score: float = Field(default=0.0) 
    letter_grade: str = Field(default="Not Graded")
    
    # EXAM OFFICE GATES: Control flag for board verification clearance
    is_released: bool = Field(default=False)