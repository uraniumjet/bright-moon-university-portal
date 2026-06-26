"""
Bright Moon University
Executive Analytics & Reporting Engine
"""

from fastapi import APIRouter
from sqlmodel import Session, select

from database.connection import engine

from models.academic import (
    StudentProfile,
    FacultyProfile,
    SupportStaffProfile,
    Course,
    Enrollment,
    Grade,
    Invoice,
    Payment,
    FinancialClearance,
    ServiceRequest,
    LmsResource
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics Engine"]
)


# ==========================================================
# UNIVERSITY OVERVIEW DASHBOARD
# ==========================================================
@router.get("/overview")
async def institution_overview():

    with Session(engine) as session:

        students = len(
            session.exec(
                select(StudentProfile)
            ).all()
        )

        faculty = len(
            session.exec(
                select(FacultyProfile)
            ).all()
        )

        staff = len(
            session.exec(
                select(SupportStaffProfile)
            ).all()
        )

        courses = len(
            session.exec(
                select(Course)
            ).all()
        )

        enrollments = len(
            session.exec(
                select(Enrollment)
            ).all()
        )

        grades = len(
            session.exec(
                select(Grade)
            ).all()
        )

        return {

            "students": students,

            "faculty": faculty,

            "staff": staff,

            "courses": courses,

            "enrollments": enrollments,

            "grades": grades
        }

# ==========================================================
# ACADEMIC ANALYTICS
# ==========================================================
@router.get("/academic")
async def academic_analytics():

    with Session(engine) as session:

        total_courses = len(
            session.exec(
                select(Course)
            ).all()
        )

        total_enrollments = len(
            session.exec(
                select(Enrollment)
            ).all()
        )

        released_results = len(
            session.exec(
                select(Grade)
                .where(
                    Grade.is_released == True
                )
            ).all()
        )

        pending_results = len(
            session.exec(
                select(Grade)
                .where(
                    Grade.is_released == False
                )
            ).all()
        )

        return {

            "courses": total_courses,

            "enrollments": total_enrollments,

            "released_results": released_results,

            "pending_results": pending_results
        }

# ==========================================================
# FINANCIAL ANALYTICS
# ==========================================================
@router.get("/financial")
async def financial_analytics():

    with Session(engine) as session:

        invoices = session.exec(
            select(Invoice)
        ).all()

        payments = session.exec(
            select(Payment)
        ).all()

        total_billed = sum(
            invoice.amount_due
            for invoice in invoices
        )

        total_collected = sum(
            payment.amount_paid
            for payment in payments
        )

        outstanding = (
            total_billed - total_collected
        )

        return {

            "total_billed": total_billed,

            "total_collected": total_collected,

            "outstanding_balance": outstanding
        }


# ==========================================================
# STUDENT CLEARANCE ANALYTICS
# ==========================================================
@router.get("/clearance")
async def clearance_analytics():

    with Session(engine) as session:

        cleared = len(
            session.exec(
                select(FinancialClearance)
                .where(
                    FinancialClearance.is_cleared == True
                )
            ).all()
        )

        uncleared = len(
            session.exec(
                select(FinancialClearance)
                .where(
                    FinancialClearance.is_cleared == False
                )
            ).all()
        )

        return {

            "cleared_students": cleared,

            "uncleared_students": uncleared
        }


# ==========================================================
# SERVICE DESK ANALYTICS
# ==========================================================
@router.get("/service-desk")
async def service_desk_analytics():

    with Session(engine) as session:

        pending = len(
            session.exec(
                select(ServiceRequest)
                .where(
                    ServiceRequest.status == "Pending"
                )
            ).all()
        )

        processing = len(
            session.exec(
                select(ServiceRequest)
                .where(
                    ServiceRequest.status == "Processing"
                )
            ).all()
        )

        completed = len(
            session.exec(
                select(ServiceRequest)
                .where(
                    ServiceRequest.status == "Completed"
                )
            ).all()
        )

        return {

            "pending": pending,

            "processing": processing,

            "completed": completed
        }


# ==========================================================
# LMS ANALYTICS
# ==========================================================
@router.get("/lms")
async def lms_analytics():

    with Session(engine) as session:

        resources = len(
            session.exec(
                select(LmsResource)
            ).all()
        )

        visible = len(
            session.exec(
                select(LmsResource)
                .where(
                    LmsResource.is_visible == True
                )
            ).all()
        )

        hidden = len(
            session.exec(
                select(LmsResource)
                .where(
                    LmsResource.is_visible == False
                )
            ).all()
        )

        return {

            "resources": resources,

            "visible": visible,

            "hidden": hidden
        }

