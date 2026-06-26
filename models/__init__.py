"""
Expose database models to ensure smooth engine initialization.
"""
from .auth import UserAccount
from .academic import StudentProfile, FacultyProfile, SupportStaffProfile, Course, CourseAllocation, Enrollment, Grade, LmsResource, ServiceRequest