"""
The Bright Moon University - Extensible Campus Services Ledger
File: models/auxiliary.py
Description: Tracks Learning Management documents and Student service requests.
"""

from typing import Optional
from sqlmodel import SQLModel, Field

class LmsResource(SQLModel, table=True):
    """Tracks structured file metadata for static classroom document delivery."""
    id: Optional[int] = Field(default=None, primary_key=True)
    course_code: str = Field(foreign_key="course.course_code", index=True)
    document_title: str # e.g., "Lecture_Slides_01.pptx"
    document_type: str # e.g., "pptx", "pdf", "docx"
    file_path: str # Pointer address on system hard drive

class ServiceRequest(SQLModel, table=True):
    """
    Unified Campus Utilities Request Tracker.
    Handles allocations for i-Hostels, ii-Bus Transports, and iii-Library Cards.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(foreign_key="studentprofile.student_id", index=True)
    service_type: str = Field(index=True) # "hostel", "bus", "library"
    description: str # Specific text detail or requested amenity
    status: str = Field(default="Pending Review") # "Pending Review", "Approved", "Denied"