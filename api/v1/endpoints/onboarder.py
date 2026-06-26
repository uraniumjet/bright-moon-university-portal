"""
Bright Moon University
File: onboarder.py

Central Identity Provisioning Engine

Responsibilities
----------------
- Student onboarding
- Faculty onboarding
- Support staff onboarding
- Authentication account creation
- Safe ID generation
- Duplicate protection
- Rollback-safe database transactions
"""

import datetime

from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select

from database.connection import engine
from core.security import hash_password

from models.auth import UserAccount

from models.academic import (
    StudentProfile,
    FacultyProfile,
    SupportStaffProfile
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/onboard",
    tags=["Identity Provisioning"]
)


# ==========================================================
# FORM HELPERS
# ==========================================================

def get_scalar(form_data, key, default=""):
    """
    Safely extracts one value from multipart form data.
    Prevents list-related bugs.
    """
    values = form_data.getlist(key)

    if not values:
        return default  

    return values[0]


# ==========================================================
# ID GENERATORS
# ==========================================================

def generate_student_id(session: Session) -> str:
    """
    Example:
        UR-2026-1001
    """

    current_year = datetime.datetime.now().year

    records = session.exec(select(StudentProfile)).all()

    if not records:
        return f"UR-{current_year}-1001"

    highest = max(
        int(record.student_id.split("-")[-1])
        for record in records
    )

    return f"UR-{current_year}-{highest+1}"


def generate_faculty_id(session: Session) -> str:
    """
    Example:
        FAC-2026-501
    """

    current_year = datetime.datetime.now().year

    records = session.exec(select(FacultyProfile)).all()

    if not records:
        return f"FAC-{current_year}-501"

    highest = max(
        int(record.faculty_id.split("-")[-1])
        for record in records
    )

    return f"FAC-{current_year}-{highest+1}"


def generate_staff_id(session: Session) -> str:
    """
    Example:
        STAFF-2026-601
    """

    current_year = datetime.datetime.now().year

    records = session.exec(select(SupportStaffProfile)).all()

    if not records:
        return f"STAFF-{current_year}-601"

    highest = max(
        int(record.staff_id.split("-")[-1])
        for record in records
    )

    return f"STAFF-{current_year}-{highest+1}"


# ==========================================================
# ACCOUNT CREATION
# ==========================================================

def create_user_account(
        session: Session,
        username: str,
        role: str):

    existing = session.exec(
        select(UserAccount)
        .where(UserAccount.username == username)
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"{username} already exists."
        )

    temp_password = f"Pass_BrightMoon_{username.split('-')[-1]}"

    account = UserAccount(
        username=username,
        hashed_password=hash_password(temp_password),
        role=role,
        requires_password_reset=True
    )

    session.add(account)


# ==========================================================
# SUCCESS RESPONSE
# ==========================================================


def build_success_response(
        generated_id,
        name,
        department,
        passport_b64,
        level=""):

    return {
        "generated_id": generated_id,
        "name": name,
        "department": department,
        "passport_b64": passport_b64,
        "level": level
    }

# ==========================================================
# STUDENT REGISTRATION
# ==========================================================

@router.post(
    "/student",
    status_code=status.HTTP_201_CREATED
)
async def create_student_profile(request: Request):
    """
    Creates:

        1. UserAccount
        2. StudentProfile

    Automatically generates:

        - Institutional ID
        - Temporary password
        - First-login password reset requirement
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            # --------------------------------------------------
            # Generate ID
            # --------------------------------------------------
            generated_id = generate_student_id(session)

            # --------------------------------------------------
            # Resolve passport image
            # --------------------------------------------------
            passport_b64 = get_scalar(
                form_data,
                "passport_b64"
            )

            # --------------------------------------------------
            # Create authentication account
            # --------------------------------------------------
            create_user_account(
                session=session,
                username=generated_id,
                role="student"
            )

            # --------------------------------------------------
            # Create profile object
            # --------------------------------------------------
            student = StudentProfile(

                student_id=generated_id,

                student_name=get_scalar(
                    form_data,
                    "name",
                    "Unnamed Student"
                ),

                age=int(
                    get_scalar(
                        form_data,
                        "age",
                        "18"
                    )
                ),

                sex=get_scalar(
                    form_data,
                    "sex",
                    "Male"
                ),

                profile_pic=passport_b64,

                header_faculty=get_scalar(
                    form_data,
                    "faculty"
                ),

                course_specialization=get_scalar(
                    form_data,
                    "department"
                ),

                academic_level=get_scalar(
                    form_data,
                    "level"
                ),

                phone_number=get_scalar(
                    form_data,
                    "phone"
                ),

                email_address=get_scalar(
                    form_data,
                    "email"
                ),

                guardian_name=get_scalar(
                    form_data,
                    "guardian_name"
                ),

                guardian_phone=get_scalar(
                    form_data,
                    "guardian_phone"
                ),

                guardian_relation=get_scalar(
                    form_data,
                    "guardian_relation"
                ),

                is_boarding=False,

                hostel_block=get_scalar(
                    form_data,
                    "hostel_block"
                ),

                room_number=get_scalar(
                    form_data,
                    "room_number"
                )
            )

            # --------------------------------------------------
            # Stage object
            # --------------------------------------------------
            session.add(student)

            # --------------------------------------------------
            # Commit transaction
            # --------------------------------------------------
            session.commit()

            # --------------------------------------------------
            # Refresh object
            # --------------------------------------------------
            session.refresh(student)

            return build_success_response(
                generated_id=generated_id,
                name=student.student_name,
                department=student.course_specialization,
                passport_b64=student.profile_pic,
                level=student.academic_level
            )

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Student registration failed: {str(e)}"
            )
# ==========================================================
# STUDENT DIRECTORY
# ==========================================================
@router.get("/student")
async def get_student_directory():
    """
    Retrieves all students.

    Used by:

        • Dashboard tables
        • Search panels
        • Enrollment engine
        • Transcript engine
    """

    with Session(engine) as session:

        students = session.exec(
            select(StudentProfile)
        ).all()

        return students

# ==========================================================
# STUDENT PROFILE LOOKUP
# ==========================================================
@router.get("/student/{student_id}")
async def get_student_profile(
        student_id: str):
    """
    Retrieves a single student profile.
    """

    with Session(engine) as session:

        student = session.exec(
            select(StudentProfile)
            .where(
                StudentProfile.student_id == student_id
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student profile not found."
            )

        return student

# ==========================================================
# STUDENT DELETION
# ==========================================================
@router.delete("/student/{student_id}")
async def delete_student_profile(
        student_id: str):
    """
    Deletes:

        • StudentProfile
        • UserAccount

    Transaction safe.
    """

    with Session(engine) as session:

        try:

            # ------------------------------------------
            # Locate student record
            # ------------------------------------------
            student = session.exec(
                select(StudentProfile)
                .where(
                    StudentProfile.student_id == student_id
                )
            ).first()

            if not student:
                raise HTTPException(
                    status_code=404,
                    detail="Student profile not found."
                )

            # ------------------------------------------
            # Locate login account
            # ------------------------------------------
            account = session.exec(
                select(UserAccount)
                .where(
                    UserAccount.username == student_id
                )
            ).first()

            # ------------------------------------------
            # Delete profile
            # ------------------------------------------
            session.delete(student)

            # ------------------------------------------
            # Delete account if present
            # ------------------------------------------
            if account:
                session.delete(account)

            # ------------------------------------------
            # Commit transaction
            # ------------------------------------------
            session.commit()

            return {
                "message":
                f"{student_id} deleted successfully."
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Deletion failed: {str(e)}"
            )

# ==========================================================
# STUDENT PROFILE UPDATE
# ==========================================================
@router.put("/student/{student_id}")
async def update_student_profile(
        student_id: str,
        request: Request):
    """
    Updates mutable student fields.

    Preserves:

        • Student ID
        • UserAccount
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            student = session.exec(
                select(StudentProfile)
                .where(
                    StudentProfile.student_id == student_id
                )
            ).first()

            if not student:
                raise HTTPException(
                    status_code=404,
                    detail="Student profile not found."
                )

            # ----------------------------------
            # Update editable fields
            # ----------------------------------
            student.student_name = get_scalar(
                form_data,
                "name",
                student.student_name
            )

            student.phone_number = get_scalar(
                form_data,
                "phone",
                student.phone_number
            )

            student.email_address = get_scalar(
                form_data,
                "email",
                student.email_address
            )

            student.header_faculty = get_scalar(
                form_data,
                "faculty",
                student.header_faculty
            )

            student.course_specialization = get_scalar(
                form_data,
                "department",
                student.course_specialization
            )

            student.academic_level = get_scalar(
                form_data,
                "level",
                student.academic_level
            )

            session.add(student)
            session.commit()
            session.refresh(student)

            return student

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    
# ==========================================================
# FACULTY REGISTRATION ENDPOINT
# ==========================================================
@router.post(
    "/faculty",
    status_code=status.HTTP_201_CREATED
)
async def create_faculty_profile(
        request: Request):
    """
    Creates:

        1. UserAccount
        2. FacultyProfile

    Automatic operations:

        • Faculty ID generation
        • Temporary password generation
        • First login password reset activation
        • Database transaction protection
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            # --------------------------------------------------
            # Generate institutional identifier
            # --------------------------------------------------
            generated_id = generate_faculty_id(session)

            # --------------------------------------------------
            # Resolve uploaded image
            # --------------------------------------------------
            passport_b64 = get_scalar(
                form_data,
                "passport_b64"
            )

            # --------------------------------------------------
            # Create authentication ledger
            # --------------------------------------------------
            create_user_account(
                session=session,
                username=generated_id,
                role="faculty"
            )

            # --------------------------------------------------
            # Build faculty profile object
            # --------------------------------------------------
            faculty = FacultyProfile(

                faculty_id=generated_id,

                faculty_name=get_scalar(
                    form_data,
                    "name",
                    "Unnamed Faculty"
                ),

                age=int(
                    get_scalar(
                        form_data,
                        "age",
                        "30"
                    )
                ),

                sex=get_scalar(
                    form_data,
                    "sex",
                    "Male"
                ),

                profile_pic=passport_b64,

                department=get_scalar(
                    form_data,
                    "department"
                ),

                academic_rank=get_scalar(
                    form_data,
                    "academic_rank"
                ),

                office_cabin=get_scalar(
                    form_data,
                    "office_cabin"
                ),

                phone_number=get_scalar(
                    form_data,
                    "phone"
                ),

                email_address=get_scalar(
                    form_data,
                    "email"
                )
            )

            # --------------------------------------------------
            # Stage object for commit
            # --------------------------------------------------
            session.add(faculty)

            # --------------------------------------------------
            # Commit transaction
            # --------------------------------------------------
            session.commit()

            # --------------------------------------------------
            # Synchronize ORM state
            # --------------------------------------------------
            session.refresh(faculty)

            # --------------------------------------------------
            # Return response payload
            # --------------------------------------------------
            return {
                "generated_id": generated_id,
                "name": faculty.faculty_name,
                "department": faculty.department,
                "passport_b64": faculty.profile_pic,
                "role": faculty.academic_rank
            }

        except Exception as e:

            # --------------------------------------------------
            # Undo partial writes
            # --------------------------------------------------
            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Faculty registration failed: {str(e)}"
            )   
# ==========================================================
# FACULTY DIRECTORY
# ==========================================================
@router.get("/faculty")
async def get_faculty_directory():
    """
    Returns all faculty members.

    Used by:

        • Dashboard tables
        • Search panels
        • Course allocation engine
    """

    with Session(engine) as session:

        faculty = session.exec(
            select(FacultyProfile)
        ).all()

        return faculty
@router.delete("/faculty/{faculty_id}")
async def delete_faculty_profile(
        faculty_id: str):
    """
    Deletes:

        • UserAccount
        • FacultyProfile

    Transaction safe.
    """

    with Session(engine) as session:

        try:

            faculty = session.exec(
                select(FacultyProfile)
                .where(
                    FacultyProfile.faculty_id == faculty_id
                )
            ).first()

            account = session.exec(
                select(UserAccount)
                .where(
                    UserAccount.username == faculty_id
                )
            ).first()

            if not faculty:
                raise HTTPException(
                    status_code=404,
                    detail="Faculty profile not found."
                )

            if account:
                session.delete(account)

            session.delete(faculty)

            session.commit()

            return {
                "message":
                f"{faculty_id} deleted successfully."
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
# ==========================================================
# FACULTY DIRECTORY
# ==========================================================
@router.get("/faculty")
async def get_faculty_directory():
    """
    Returns all faculty members.

    Used by:

        • Dashboard tables
        • Search panels
        • Course allocation engine
    """

    with Session(engine) as session:

        faculty = session.exec(
            select(FacultyProfile)
        ).all()

        return faculty
# ==========================================================
# FACULTY PROFILE UPDATE
# ==========================================================
@router.put("/faculty/{faculty_id}")
async def update_faculty_profile(
        faculty_id: str,
        request: Request):
    """
    Updates editable faculty information.

    Preserves:

        • Faculty ID
        • UserAccount
        • Password state

    Allows changing:

        • Name
        • Department
        • Academic Rank
        • Office Cabin
        • Phone Number
        • Email Address
        • Profile Picture
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            # --------------------------------------------------
            # Locate faculty record
            # --------------------------------------------------
            faculty = session.exec(
                select(FacultyProfile)
                .where(
                    FacultyProfile.faculty_id == faculty_id
                )
            ).first()

            if not faculty:
                raise HTTPException(
                    status_code=404,
                    detail="Faculty profile not found."
                )

            # --------------------------------------------------
            # Update editable fields
            # --------------------------------------------------

            faculty.faculty_name = get_scalar(
                form_data,
                "name",
                faculty.faculty_name
            )

            faculty.age = int(
                get_scalar(
                    form_data,
                    "age",
                    str(faculty.age)
                )
            )

            faculty.sex = get_scalar(
                form_data,
                "sex",
                faculty.sex
            )

            faculty.department = get_scalar(
                form_data,
                "department",
                faculty.department
            )

            faculty.academic_rank = get_scalar(
                form_data,
                "academic_rank",
                faculty.academic_rank
            )

            faculty.office_cabin = get_scalar(
                form_data,
                "office_cabin",
                faculty.office_cabin
            )

            faculty.phone_number = get_scalar(
                form_data,
                "phone",
                faculty.phone_number
            )

            faculty.email_address = get_scalar(
                form_data,
                "email",
                faculty.email_address
            )

            # --------------------------------------------------
            # Update image only if supplied
            # --------------------------------------------------
            passport_b64 = get_scalar(
                form_data,
                "passport_b64"
            )

            if passport_b64:
                faculty.profile_pic = passport_b64

            # --------------------------------------------------
            # Commit changes
            # --------------------------------------------------
            session.add(faculty)

            session.commit()

            session.refresh(faculty)

            # --------------------------------------------------
            # Return updated profile payload
            # --------------------------------------------------
            return {
                "faculty_id": faculty.faculty_id,
                "name": faculty.faculty_name,
                "department": faculty.department,
                "role": faculty.academic_rank,
                "passport_b64": faculty.profile_pic
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Faculty update failed: {str(e)}"
            )
# ==========================================================
# SUPPORT STAFF ID GENERATOR
# ==========================================================
def generate_staff_id(session: Session) -> str:
    """
    Generates sequential support staff identifiers.

    Example:

        STAFF-2026-601
        STAFF-2026-602
    """

    current_year = datetime.datetime.now().year

    records = session.exec(
        select(SupportStaffProfile)
    ).all()

    if not records:
        return f"STAFF-{current_year}-601"

    highest = max(
        int(record.staff_id.split("-")[-1])
        for record in records
        if record.staff_id.startswith("STAFF-")
    )

    return f"STAFF-{current_year}-{highest + 1}"
# ==========================================================
# SUPPORT STAFF REGISTRATION
# ==========================================================
@router.post(
    "/staff",
    status_code=status.HTTP_201_CREATED
)
async def create_staff_profile(request: Request):
    """
    Creates:

        • UserAccount
        • SupportStaffProfile

    Enables:

        • First login password reset
        • Transaction rollback protection
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            generated_id = generate_staff_id(session)

            passport_b64 = get_scalar(
                form_data,
                "passport_b64"
            )

            system_role = get_scalar(
                form_data,
                "system_role",
                "non_academic"
            )

            create_user_account(
                session=session,
                username=generated_id,
                role=system_role
            )

            staff = SupportStaffProfile(

                staff_id=generated_id,

                staff_name=get_scalar(
                    form_data,
                    "name",
                    "Unnamed Staff"
                ),

                age=int(
                    get_scalar(
                        form_data,
                        "age",
                        "30"
                    )
                ),

                sex=get_scalar(
                    form_data,
                    "sex",
                    "Male"
                ),

                profile_pic=passport_b64,

                department=get_scalar(
                    form_data,
                    "department"
                ),

                assigned_role=get_scalar(
                    form_data,
                    "assigned_role"
                ),

                office_cabin=get_scalar(
                    form_data,
                    "office_cabin"
                ),

                phone_number=get_scalar(
                    form_data,
                    "phone"
                ),

                email_address=get_scalar(
                    form_data,
                    "email"
                )
            )

            session.add(staff)

            session.commit()

            session.refresh(staff)

            return {
                "generated_id": generated_id,
                "name": staff.staff_name,
                "department": staff.department,
                "role": staff.assigned_role,
                "passport_b64": staff.profile_pic
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Staff registration failed: {str(e)}"
            )
# ==========================================================
# SUPPORT STAFF REGISTRATION
# ==========================================================
@router.post(
    "/staff",
    status_code=status.HTTP_201_CREATED
)
async def create_staff_profile(request: Request):
    """
    Creates:

        • UserAccount
        • SupportStaffProfile

    Enables:

        • First login password reset
        • Transaction rollback protection
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            generated_id = generate_staff_id(session)

            passport_b64 = get_scalar(
                form_data,
                "passport_b64"
            )

            system_role = get_scalar(
                form_data,
                "system_role",
                "non_academic"
            )

            create_user_account(
                session=session,
                username=generated_id,
                role=system_role
            )

            staff = SupportStaffProfile(

                staff_id=generated_id,

                staff_name=get_scalar(
                    form_data,
                    "name",
                    "Unnamed Staff"
                ),

                age=int(
                    get_scalar(
                        form_data,
                        "age",
                        "30"
                    )
                ),

                sex=get_scalar(
                    form_data,
                    "sex",
                    "Male"
                ),

                profile_pic=passport_b64,

                department=get_scalar(
                    form_data,
                    "department"
                ),

                assigned_role=get_scalar(
                    form_data,
                    "assigned_role"
                ),

                office_cabin=get_scalar(
                    form_data,
                    "office_cabin"
                ),

                phone_number=get_scalar(
                    form_data,
                    "phone"
                ),

                email_address=get_scalar(
                    form_data,
                    "email"
                )
            )

            session.add(staff)

            session.commit()

            session.refresh(staff)

            return {
                "generated_id": generated_id,
                "name": staff.staff_name,
                "department": staff.department,
                "role": staff.assigned_role,
                "passport_b64": staff.profile_pic
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Staff registration failed: {str(e)}"
            )
# ==========================================================
# SUPPORT STAFF DIRECTORY
# ==========================================================
@router.get("/staff")
async def get_staff_directory():
    """
    Retrieves all support staff.
    """

    with Session(engine) as session:

        records = session.exec(
            select(SupportStaffProfile)
        ).all()

        return records

# ==========================================================
# SUPPORT STAFF PROFILE LOOKUP
# ==========================================================
@router.get("/staff/{staff_id}")
async def get_staff_profile(
        staff_id: str):

    with Session(engine) as session:

        staff = session.exec(
            select(SupportStaffProfile)
            .where(
                SupportStaffProfile.staff_id == staff_id
            )
        ).first()

        if not staff:
            raise HTTPException(
                status_code=404,
                detail="Staff profile not found."
            )

        return staff
# ==========================================================
# SUPPORT STAFF PROFILE UPDATE
# ==========================================================
@router.put("/staff/{staff_id}")
async def update_staff_profile(
        staff_id: str,
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            staff = session.exec(
                select(SupportStaffProfile)
                .where(
                    SupportStaffProfile.staff_id == staff_id
                )
            ).first()

            if not staff:
                raise HTTPException(
                    status_code=404,
                    detail="Staff profile not found."
                )

            staff.staff_name = get_scalar(
                form_data,
                "name",
                staff.staff_name
            )

            staff.department = get_scalar(
                form_data,
                "department",
                staff.department
            )

            staff.assigned_role = get_scalar(
                form_data,
                "assigned_role",
                staff.assigned_role
            )

            staff.office_cabin = get_scalar(
                form_data,
                "office_cabin",
                staff.office_cabin
            )

            staff.phone_number = get_scalar(
                form_data,
                "phone",
                staff.phone_number
            )

            staff.email_address = get_scalar(
                form_data,
                "email",
                staff.email_address
            )

            passport_b64 = get_scalar(
                form_data,
                "passport_b64"
            )

            if passport_b64:
                staff.profile_pic = passport_b64

            session.add(staff)

            session.commit()

            session.refresh(staff)

            return staff

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
# ==========================================================
# SUPPORT STAFF DELETION
# ==========================================================
@router.delete("/staff/{staff_id}")
async def delete_staff_profile(
        staff_id: str):

    with Session(engine) as session:

        try:

            staff = session.exec(
                select(SupportStaffProfile)
                .where(
                    SupportStaffProfile.staff_id == staff_id
                )
            ).first()

            account = session.exec(
                select(UserAccount)
                .where(
                    UserAccount.username == staff_id
                )
            ).first()

            if not staff:
                raise HTTPException(
                    status_code=404,
                    detail="Staff profile not found."
                )

            if account:
                session.delete(account)

            session.delete(staff)

            session.commit()

            return {
                "message":
                f"{staff_id} deleted successfully."
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
