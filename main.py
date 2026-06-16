"""
The Bright Moon University - Central Portal Bootstrapper
File: main.py
Description: App entry point, session engine state controller, and UI rendering layer.
"""

from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database.connection import init_db, engine
from api.v1.router import api_router
from core.security import verify_password, hash_password
from models import (
    UserAccount, StudentProfile, FacultyProfile, 
    Course, Enrollment, Grade, LmsResource, ServiceRequest, CourseAllocation
)

# Instantiate the FastAPI engine application core
app = FastAPI(title="The Bright Moon University Portal System")

# Mount our decoupled API backend routes pipeline
app.include_router(api_router)

# Setup the Jinja2 viewport layout views compiler directory
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    """Triggers when the system kicks off to spin up missing table spaces."""
    init_db()

# ---------------------------------------------------------
# CENTRAL SECURITY PORTAL GATEWAY ROUTES (LOGIN/ROUTING)
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def central_login_gateway(request: Request):
    """Renders the standard landing unified login screen."""
    return templates.TemplateResponse(request=request, name="index.html", context={"error": None})


@app.post("/login")
async def process_portal_authentication(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Evaluates institutional login requests and switches user focus 
    directly over to their targeted system role dashboard.
    """
    with Session(engine) as session:
        # Check if user account exists
        user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return templates.TemplateResponse(
                request=request, name="index.html", context={"error": "Invalid Institutional ID or Secure Access Token key entry."}
            )
            
        # Check if onboarding credentials requirement activation state flag is raised
        if user.requires_password_reset:
            return templates.TemplateResponse(
                request=request, name="index.html", 
                context={"requires_reset": True, "username": username, "msg": "First-time security check validation required."}
            )
            
        # Multi-Tenant Workspace Session Router Dispatcher Matrix
        if user.role == "onboarder":
            return RedirectResponse(url=f"/portal/onboarder?user={username}", status_code=303)
        elif user.role == "student":
            return RedirectResponse(url=f"/portal/student?user={username}", status_code=303)
        elif user.role == "faculty":
            return RedirectResponse(url=f"/portal/faculty?user={username}", status_code=303)
        elif user.role == "exam_office":
            return RedirectResponse(url=f"/portal/exam-office?user={username}", status_code=303)
            
    return RedirectResponse(url="/", status_code=303)


@app.post("/force-password-reset")
async def handle_onboarding_password_update(
    username: str = Form(...),
    new_password: str = Form(...)
):
    """Allows freshly onboarded entries to update their temporary credentials seamlessly."""
    with Session(engine) as session:
        user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()
        if user:
            user.hashed_password = hash_password(new_password)
            user.requires_password_reset = False
            session.add(user)
            session.commit()
    return RedirectResponse(url="/?msg=Security+Credentials+Activated+Successfully", status_code=303)

# ---------------------------------------------------------
# MULTI-TENANT UI WORKSPACE DESKS RENDERING RENDER PIPELINES
# ---------------------------------------------------------

@app.get("/portal/student", response_class=HTMLResponse)
async def render_student_workspace(request: Request, user: str):
    """Queries and renders the student complete profile workspace."""
    with Session(engine) as session:
        student = session.exec(select(StudentProfile).where(StudentProfile.student_id == user)).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student structural profile entity not found.")
            
        # Query course modules enrollments and zip them cleanly with evaluation grade status
        enrollments = session.exec(select(Enrollment).where(Enrollment.student_id == user)).all()
        report_card = []
        
        for e in enrollments:
            course = session.exec(select(Course).where(Course.course_code == e.course_code)).first()
            grade = session.exec(select(Grade).where(Grade.enrollment_id == e.id)).first()
            
            # Read curriculum resources paths
            resources = session.exec(select(LmsResource).where(LmsResource.course_code == e.course_code)).all()
            
            report_card.append({
                "code": e.course_code,
                "title": course.title if course else "Unknown Core Module Title",
                "credits": course.credit_hours if course else 0,
                "ca": grade.continuous_assessment if (grade and grade.is_released) else "--",
                "exam": grade.final_exam if (grade and grade.is_released) else "--",
                "total": grade.total_score if (grade and grade.is_released) else "--",
                "letter": grade.letter_grade if (grade and grade.is_released) else "Awaiting Board Release",
                "resources": resources
            })
            
        # Gather student service utilities logs
        services = session.exec(select(ServiceRequest).where(ServiceRequest.student_id == user)).all()
        
        # Pull system-wide faculty contact tables lists data rows
        faculty_directory = session.exec(select(FacultyProfile)).all()
        
    return templates.TemplateResponse(
        request=request, name="students/dashboard.html", 
        context={"student": student, "report_card": report_card, "services": services, "faculty_directory": faculty_directory}
    )


@app.get("/portal/faculty", response_class=HTMLResponse)
async def render_faculty_dashboard(request: Request, user: str, active_class: str = None):
    """Loads cross-level course routing panels assigned to the teacher."""
    with Session(engine) as session:
        faculty = session.exec(select(FacultyProfile).where(FacultyProfile.faculty_id == user)).first()
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty record profile missing.")
            
        # Pull allocated classes paths mapping arrays
        allocations = session.exec(select(CourseAllocation).where(CourseAllocation.faculty_id == user)).all()
        
        roster_data = []
        selected_course_title = ""
        
        # If a specific cross-level course block is focused via the sidebar links matrix
        if active_class:
            course_meta = session.exec(select(Course).where(Course.course_code == active_class)).first()
            if course_meta:
                selected_course_title = course_meta.title
                
            # Grab all student enrollment blocks matching that specific class path code
            enrollments = session.exec(select(Enrollment).where(Enrollment.course_code == active_class)).all()
            
            for e in enrollments:
                st_profile = session.exec(select(StudentProfile).where(StudentProfile.student_id == e.student_id)).first()
                grade = session.exec(select(Grade).where(Grade.enrollment_id == e.id)).first()
                
                roster_data.append({
                    "enrollment_id": e.id,
                    "student_id": e.student_id,
                    "student_name": st_profile.student_name if st_profile else "Candidate Unknown",
                    "level": st_profile.academic_level if st_profile else "--",
                    "ca": grade.continuous_assessment if grade else 0.0,
                    "exam": grade.final_exam if grade else 0.0,
                    "total": grade.total_score if grade else 0.0,
                    "letter": grade.letter_grade if grade else "Not Graded",
                    "is_released": grade.is_released if grade else False
                })
                
    return templates.TemplateResponse(
        request=request, name="faculty/dashboard.html",
        context={
            "faculty": faculty, "allocations": allocations, 
            "active_class": active_class, "course_title": selected_course_title, "roster": roster_data
        }
    )


@app.get("/portal/onboarder", response_class=HTMLResponse)
async def render_onboarder_dashboard(request: Request, user: str):
    """Loads identity provisioning workspace for onboarding actions."""
    return templates.TemplateResponse(request=request, name="onboarder/dashboard.html", context={"admin_id": user})


@app.get("/portal/exam-office", response_class=HTMLResponse)
async def render_exam_office_dashboard(request: Request, user: str):
    """Loads evaluation gate clearance boards tracking unreleased grades reports sheets."""
    with Session(engine) as session:
        # Aggregates courses matching unreleased grades metrics profiles
        statement = select(Course.course_code, Course.title).join(Enrollment, Enrollment.course_code == Course.course_code).join(Grade, Grade.enrollment_id == Enrollment.id).where(Grade.is_released == False).distinct()
        pending_courses = session.exec(statement).all()
        
        courses_list = [{"code": row[0], "title": row[1]} for row in pending_courses]
        
    return templates.TemplateResponse(request=request, name="exam_office/dashboard.html", context={"admin_id": user, "pending_courses": courses_list})