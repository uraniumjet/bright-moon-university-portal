"""
Expose database models to ensure smooth engine initialization.
"""
from .auth import UserAccount
from .academic import StudentProfile, FacultyProfile, Course, CourseAllocation, Enrollment, Grade
from .auxiliary import LmsResource, ServiceRequest