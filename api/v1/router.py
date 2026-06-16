"""
The Bright Moon University - Centralized Application Router Compiler
File: api/v1/router.py
Description: Aggregates separate endpoint modules into a single unified API pipeline.
"""

from fastapi import APIRouter
from api.v1.endpoints.onboarder import router as onboard_router
from api.v1.endpoints.students import router as student_router
from api.v1.endpoints.faculty import router as faculty_router
from api.v1.endpoints.exam_office import router as exam_router
from api.v1.endpoints.analytics import router as analytics_router

# Central aggregator router
api_router = APIRouter(prefix="/api/v1")

# Mount separate user-role processing sub-routers
api_router.include_router(onboard_router)
api_router.include_router(student_router)
api_router.include_router(faculty_router)
api_router.include_router(exam_router)
api_router.include_router(analytics_router)