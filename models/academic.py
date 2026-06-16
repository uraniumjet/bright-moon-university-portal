"""
The Bright Moon University - Core Academic Relational Blueprint
File: models/academic.py
Description: Maps Students, Faculties, Courses, Enrollments, and Grade Approval matrices.
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class StudentProfile(SQLModel, table=True):
    """Primary identity matrix for matriculated student candidates."""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(unique=True, index=True) # Maps directly to UserAccount.username
    student_name: str
    faculty_name: str # e.g., "Science & Engineering"
    course_specialization: str # e.g., "Cyber Security & AI"
    academic_level: str # e.g., "B.Sc.", "M.Sc."
    current_semester: int = Field(default=1)
    attendance_pct: float = Field(default=100.0) # Background data stream for Pandas risk checks

class FacultyProfile(SQLModel, table=True):
    """Identity matrix for appointed lecturing staff."""
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: str = Field(unique=True, index=True) # Maps directly to UserAccount.username
    faculty_name: str
    department: str
    academic_rank: str # e.g., "Professor", "Senior Lecturer"

class Course(SQLModel, table=True):
    """Unified school catalog specifying weighted modules."""
    id: Optional[int] = Field(default=None, primary_key=True)
    course_code: str = Field(unique=True, index=True) # e.g., "CS-601"
    title: str
    credit_hours: int
    academic_level: str # Match filtering for B.Sc. or M.Sc. tracks

class CourseAllocation(SQLModel, table=True):
    """
    Decoupled Cross-Level Routing Bridge.
    Maps a FacultyProfile to multiple Courses across different academic levels.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: str = Field(foreign_key="facultyprofile.faculty_id", index=True)
    course_code: str = Field(foreign_key="course.course_code", index=True)
    semester: int

class Enrollment(SQLModel, table=True):
    """Relational bridge connecting a single Student to a single Course for a targeted term."""
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
    continuous_assessment: float = Field(default=0.0) # Max 40
    final_exam: float = Field(default=0.0) # Max 60
    total_score: float = Field(default=0.0) # Max 100
    letter_grade: str = Field(default="Not Graded")
    
    # EXAM OFFICE GATES: If False, student sees "Awaiting Board Release" placeholder layout
    is_released: bool = Field(default=False)