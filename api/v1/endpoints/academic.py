"""
Bright Moon University
Academic Engine API

Handles:

    • Course Management
    • Faculty Course Allocation
    • Enrollment
    • Grade Management
    • Exam Office Release Pipeline
"""

from fastapi import APIRouter, HTTPException, status, Request
from sqlmodel import Session, select


from database.connection import engine
from models.academic import (
    Course,
    CourseAllocation,
    Enrollment,
    Grade
)

router = APIRouter(
    prefix="/academic",
    tags=["Academic Engine"]
)

# ==========================================================
# LETTER GRADE CALCULATOR
# ==========================================================
def calculate_grade(ca: float, exam: float):

    total = ca + exam

    if total >= 90:
        letter = "A"

    elif total >= 80:
        letter = "B"

    elif total >= 70:
        letter = "C"

    elif total >= 60:
        letter = "D"

    elif total >= 50:
        letter = "E"

    else:
        letter = "F"

    return total, letter
# ==========================================================
# GRADE POINT CALCULATOR
# ==========================================================
def letter_to_grade_point(letter: str) -> int:
    """
    Converts letter grades to grade points.
    """

    mapping = {

        "A": 5,
        "B": 4,
        "C": 3,
        "D": 2,
        "E": 1,
        "F": 0

    }

    return mapping.get(letter, 0)
# ==========================================================
# GPA CALCULATOR
# ==========================================================
def calculate_gpa(
        session: Session,
        student_id: str,
        semester: int):

    enrollments = session.exec(

        select(Enrollment)
        .where(
            Enrollment.student_id == student_id,
            Enrollment.semester == semester
        )

    ).all()

    total_units = 0
    total_points = 0

    for enrollment in enrollments:

        grade = session.exec(

            select(Grade)
            .where(
                Grade.enrollment_id == enrollment.id,
                Grade.is_released == True
            )

        ).first()

        if not grade:
            continue

        course = session.exec(

            select(Course)
            .where(
                Course.course_code == enrollment.course_code
            )

        ).first()

        if not course:
            continue

        units = course.credit_hours

        grade_point = letter_to_grade_point(
            grade.letter_grade
        )

        total_units += units

        total_points += units * grade_point

    if total_units == 0:
        return 0.0

    return round(
        total_points / total_units,
        2
    )

# ==========================================================
# CGPA CALCULATOR
# ==========================================================
def calculate_cgpa(
        session: Session,
        student_id: str):

    semesters = session.exec(

        select(Enrollment.semester)
        .where(
            Enrollment.student_id == student_id
        )

    ).all()

    semesters = list(set(semesters))

    if len(semesters) == 0:
        return 0.0

    values = []

    for semester in semesters:

        values.append(

            calculate_gpa(
                session,
                student_id,
                semester
            )

        )

    return round(

        sum(values) / len(values),

        2

    )

# ==========================================================
# DEGREE CLASSIFICATION
# ==========================================================
def degree_classification(cgpa: float):

    if cgpa >= 4.50:
        return "First Class"

    elif cgpa >= 3.50:
        return "Second Class Upper"

    elif cgpa >= 2.40:
        return "Second Class Lower"

    elif cgpa >= 1.50:
        return "Third Class"

    return "Pass"

# ==========================================================
# COMPLETE TRANSCRIPT
# ==========================================================
@router.get("/transcript/{student_id}")
async def generate_transcript(
        student_id: str):

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
                detail="Student not found."
            )

        cgpa = calculate_cgpa(
            session,
            student_id
        )

        return {

            "student_name": student.student_name,

            "student_id": student.student_id,

            "programme": student.course_specialization,

            "faculty": student.header_faculty,

            "academic_level": student.academic_level,

            "cgpa": cgpa,

            "classification":
            degree_classification(cgpa)

        }

# ==========================================================
# CREATE COURSE
# ==========================================================
@router.post(
    "/course",
    status_code=status.HTTP_201_CREATED
)
async def create_course(request: Request):
    """
    Registers a new course into the university catalog.
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            course_code = form_data.get(
                "course_code",
                ""
            ).upper()

            # Prevent duplicate course codes
            existing = session.exec(
                select(Course)
                .where(
                    Course.course_code == course_code
                )
            ).first()

            if existing:

                raise HTTPException(
                    status_code=409,
                    detail="Course already exists."
                )

            course = Course(

                course_code=course_code,

                title=form_data.get(
                    "title",
                    ""
                ),

                credit_hours=int(
                    form_data.get(
                        "credit_hours",
                        3
                    )
                ),

                academic_level=form_data.get(
                    "academic_level",
                    "100 Level"
                )

            )

            session.add(course)

            session.commit()

            session.refresh(course)

            return course

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Course creation failed: {str(e)}"
            )
# ==========================================================
# CREATE COURSE
# ==========================================================
@router.post(
    "/course",
    status_code=status.HTTP_201_CREATED
)
async def create_course(request: Request):
    """
    Registers a new course into the university catalog.
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            course_code = form_data.get(
                "course_code",
                ""
            ).upper()

            # Prevent duplicate course codes
            existing = session.exec(
                select(Course)
                .where(
                    Course.course_code == course_code
                )
            ).first()

            if existing:

                raise HTTPException(
                    status_code=409,
                    detail="Course already exists."
                )

            course = Course(

                course_code=course_code,

                title=form_data.get(
                    "title",
                    ""
                ),

                credit_hours=int(
                    form_data.get(
                        "credit_hours",
                        3
                    )
                ),

                academic_level=form_data.get(
                    "academic_level",
                    "100 Level"
                )

            )

            session.add(course)

            session.commit()

            session.refresh(course)

            return course

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Course creation failed: {str(e)}"
            )
# ==========================================================
# COURSE DIRECTORY
# ==========================================================
@router.get("/courses")
async def get_course_directory():
    """
    Returns the complete course catalog.
    """

    with Session(engine) as session:

        return session.exec(
            select(Course)
        ).all()
# ==========================================================
# COURSE LOOKUP
# ==========================================================
@router.get("/course/{course_code}")
async def get_course(
        course_code: str):

    with Session(engine) as session:

        course = session.exec(
            select(Course)
            .where(
                Course.course_code == course_code
            )
        ).first()

        if not course:

            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        return course

# ==========================================================
# UPDATE COURSE
# ==========================================================
@router.put("/course/{course_code}")
async def update_course(
        course_code: str,
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            course = session.exec(
                select(Course)
                .where(
                    Course.course_code == course_code
                )
            ).first()

            if not course:

                raise HTTPException(
                    status_code=404,
                    detail="Course not found."
                )

            course.title = form_data.get(
                "title",
                course.title
            )

            course.credit_hours = int(
                form_data.get(
                    "credit_hours",
                    course.credit_hours
                )
            )

            course.academic_level = form_data.get(
                "academic_level",
                course.academic_level
            )

            session.add(course)

            session.commit()

            session.refresh(course)

            return course

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
# ==========================================================
# DELETE COURSE
# ==========================================================
@router.delete("/course/{course_code}")
async def delete_course(
        course_code: str):

    with Session(engine) as session:

        try:

            course = session.exec(
                select(Course)
                .where(
                    Course.course_code == course_code
                )
            ).first()

            if not course:

                raise HTTPException(
                    status_code=404,
                    detail="Course not found."
                )

            session.delete(course)

            session.commit()

            return {
                "message":
                f"{course_code} deleted successfully."
            }

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

# ==========================================================
# STUDENT COURSE ENROLLMENT
# ==========================================================
@router.post(
    "/enrollment",
    status_code=status.HTTP_201_CREATED
)
async def create_enrollment(request: Request):
    """
    Registers a student into a course.
    """

    form_data = await request.form()

    with Session(engine) as session:

        try:

            student_id = form_data.get("student_id")
            course_code = form_data.get("course_code")
            semester = int(form_data.get("semester", 1))

            # Verify student
            student = session.exec(
                select(StudentProfile)
                .where(
                    StudentProfile.student_id == student_id
                )
            ).first()

            if not student:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found."
                )

            # Verify course
            course = session.exec(
                select(Course)
                .where(
                    Course.course_code == course_code
                )
            ).first()

            if not course:
                raise HTTPException(
                    status_code=404,
                    detail="Course not found."
                )

            # Prevent duplicate registration
            existing = session.exec(
                select(Enrollment)
                .where(
                    Enrollment.student_id == student_id,
                    Enrollment.course_code == course_code
                )
            ).first()

            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="Student already enrolled."
                )

            enrollment = Enrollment(
                student_id=student_id,
                course_code=course_code,
                semester=semester
            )

            session.add(enrollment)

            session.commit()

            session.refresh(enrollment)

            return enrollment

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

# ==========================================================
# ENROLLMENT DIRECTORY
# ==========================================================
@router.get("/enrollments")
async def get_enrollments():

    with Session(engine) as session:

        return session.exec(
            select(Enrollment)
        ).all()

# ==========================================================
# STUDENT REGISTERED COURSES
# ==========================================================
@router.get("/student/{student_id}")
async def get_student_enrollments(
        student_id: str):

    with Session(engine) as session:

        enrollments = session.exec(
            select(Enrollment)
            .where(
                Enrollment.student_id == student_id
            )
        ).all()

        return enrollments

# ==========================================================
# REMOVE COURSE REGISTRATION
# ==========================================================
@router.delete("/enrollment/{id}")
async def delete_enrollment(
        id: int):

    with Session(engine) as session:

        enrollment = session.get(
            Enrollment,
            id
        )

        if not enrollment:

            raise HTTPException(
                status_code=404,
                detail="Enrollment not found."
            )

        session.delete(enrollment)

        session.commit()

        return {
            "message":
            "Enrollment deleted successfully."
        }

# ==========================================================
# CREATE GRADE SHEET
# ==========================================================
@router.post(
    "/grade",
    status_code=status.HTTP_201_CREATED
)
async def create_grade(request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            enrollment_id = int(
                form_data.get("enrollment_id")
            )

            ca = float(
                form_data.get(
                    "continuous_assessment",
                    0
                )
            )

            exam = float(
                form_data.get(
                    "final_exam",
                    0
                )
            )

            enrollment = session.get(
                Enrollment,
                enrollment_id
            )

            if not enrollment:

                raise HTTPException(
                    status_code=404,
                    detail="Enrollment not found."
                )

            existing = session.exec(
                select(Grade)
                .where(
                    Grade.enrollment_id == enrollment_id
                )
            ).first()

            if existing:

                raise HTTPException(
                    status_code=409,
                    detail="Grade already exists."
                )

            total, letter = calculate_grade(
                ca,
                exam
            )

            grade = Grade(

                enrollment_id=enrollment_id,

                continuous_assessment=ca,

                final_exam=exam,

                total_score=total,

                letter_grade=letter
            )

            session.add(grade)

            session.commit()

            session.refresh(grade)

            return grade

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

# ==========================================================
# GRADE DIRECTORY
# ==========================================================
@router.get("/grades")
async def get_grades():

    with Session(engine) as session:

        return session.exec(
            select(Grade)
        ).all()

# ==========================================================
# SINGLE GRADE LOOKUP
# ==========================================================
@router.get("/grade/{id}")
async def get_grade(
        id: int):

    with Session(engine) as session:

        grade = session.get(
            Grade,
            id
        )

        if not grade:

            raise HTTPException(
                status_code=404,
                detail="Grade not found."
            )

        return grade

# ==========================================================
# SINGLE GRADE LOOKUP
# ==========================================================
@router.get("/grade/{id}")
async def get_grade(
        id: int):

    with Session(engine) as session:

        grade = session.get(
            Grade,
            id
        )

        if not grade:

            raise HTTPException(
                status_code=404,
                detail="Grade not found."
            )

        return grade
        
# ==========================================================
# UPDATE GRADE
# ==========================================================
@router.put("/grade/{id}")
async def update_grade(
        id: int,
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            grade = session.get(
                Grade,
                id
            )

            if not grade:

                raise HTTPException(
                    status_code=404,
                    detail="Grade not found."
                )

            grade.continuous_assessment = float(
                form_data.get(
                    "continuous_assessment",
                    grade.continuous_assessment
                )
            )

            grade.final_exam = float(
                form_data.get(
                    "final_exam",
                    grade.final_exam
                )
            )

            total, letter = calculate_grade(
                grade.continuous_assessment,
                grade.final_exam
            )

            grade.total_score = total

            grade.letter_grade = letter

            session.add(grade)

            session.commit()

            session.refresh(grade)

            return grade

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )


# ==========================================================
# DELETE GRADE
# ==========================================================
@router.delete("/grade/{id}")
async def delete_grade(
        id: int):

    with Session(engine) as session:

        grade = session.get(
            Grade,
            id
        )

        if not grade:

            raise HTTPException(
                status_code=404,
                detail="Grade not found."
            )

        session.delete(grade)

        session.commit()

        return {
            "message":
            "Grade deleted successfully."
        }

# ==========================================================
# EXAM OFFICE RESULT RELEASE
# ==========================================================
@router.put("/grade/{grade_id}/release")
async def release_grade(
        grade_id: int):
    """
    Approves and releases a grade sheet for student visibility.
    """

    with Session(engine) as session:

        grade = session.get(
            Grade,
            grade_id
        )

        if not grade:

            raise HTTPException(
                status_code=404,
                detail="Grade not found."
            )

        if grade.is_released:

            return {
                "message": "Grade already released.",
                "grade_id": grade.id
            }

        grade.is_released = True

        session.add(grade)

        session.commit()

        session.refresh(grade)

        return {
            "message": "Result released successfully.",
            "grade_id": grade.id,
            "released": grade.is_released
        }
# ==========================================================
# REVERSE RESULT RELEASE
# ==========================================================
@router.put("/grade/{grade_id}/unrelease")
async def unrelease_grade(
        grade_id: int):

    with Session(engine) as session:

        grade = session.get(
            Grade,
            grade_id
        )

        if not grade:

            raise HTTPException(
                status_code=404,
                detail="Grade not found."
            )

        grade.is_released = False

        session.add(grade)

        session.commit()

        session.refresh(grade)

        return {
            "message": "Result withdrawn.",
            "released": grade.is_released
        }

# ==========================================================
# REVERSE RESULT RELEASE
# ==========================================================
@router.put("/grade/{grade_id}/unrelease")
async def unrelease_grade(
        grade_id: int):

    with Session(engine) as session:

        grade = session.get(
            Grade,
            grade_id
        )

        if not grade:

            raise HTTPException(
                status_code=404,
                detail="Grade not found."
            )

        grade.is_released = False

        session.add(grade)

        session.commit()

        session.refresh(grade)

        return {
            "message": "Result withdrawn.",
            "released": grade.is_released
        }
# ==========================================================
# PENDING RESULTS
# ==========================================================
@router.get("/grades/unreleased")
async def get_unreleased_grades():
    """
    Returns all grades awaiting Exam Office approval.
    """

    with Session(engine) as session:

        grades = session.exec(
            select(Grade)
            .where(
                Grade.is_released == False
            )
        ).all()

        return grades
# ==========================================================
# RELEASED RESULTS
# ==========================================================
@router.get("/grades/released")
async def get_released_grades():
    """
    Returns released grades.
    """

    with Session(engine) as session:

        grades = session.exec(
            select(Grade)
            .where(
                Grade.is_released == True
            )
        ).all()

        return grades

# ==========================================================
# EXAM OFFICE ANALYTICS
# ==========================================================
@router.get("/exam-office/statistics")
async def exam_office_statistics():

    with Session(engine) as session:

        total = len(
            session.exec(
                select(Grade)
            ).all()
        )

        released = len(
            session.exec(
                select(Grade)
                .where(
                    Grade.is_released == True
                )
            ).all()
        )

        unreleased = len(
            session.exec(
                select(Grade)
                .where(
                    Grade.is_released == False
                )
            ).all()
        )

        return {

            "total_grade_records": total,

            "released_records": released,

            "pending_records": unreleased

        }
    
# ==========================================================
# SEMESTER RESULT SHEET
# ==========================================================
@router.get("/results/{student_id}/{semester}")
async def get_semester_result(
        student_id: str,
        semester: int):

    with Session(engine) as session:

        enrollments = session.exec(

            select(Enrollment)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.semester == semester
            )

        ).all()

        records = []

        for enrollment in enrollments:

            grade = session.exec(

                select(Grade)
                .where(
                    Grade.enrollment_id == enrollment.id,
                    Grade.is_released == True
                )

            ).first()

            if not grade:
                continue

            course = session.exec(

                select(Course)
                .where(
                    Course.course_code == enrollment.course_code
                )

            ).first()

            records.append({

                "course_code": course.course_code,

                "course_title": course.title,

                "credit_hours": course.credit_hours,

                "score": grade.total_score,

                "grade": grade.letter_grade

            })

        gpa = calculate_gpa(
            session,
            student_id,
            semester
        )

        return {

            "student_id": student_id,

            "semester": semester,

            "gpa": gpa,

            "results": records

        }