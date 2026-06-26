"""
Bright Moon University
Learning Management System API
"""

from fastapi import APIRouter, Request, HTTPException, status
router = APIRouter(
    prefix="/lms",
    tags=["Learning Management System"]
)



from sqlmodel import Session, select

from database.connection import engine

from models.academic import (
    LmsResource,
    Course,
    FacultyProfile
)


# ==========================================================
# CREATE LMS RESOURCE
# ==========================================================
@router.post(
    "/resource",
    status_code=status.HTTP_201_CREATED
)
async def create_resource(
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            course_code = form_data.get("course_code")

            uploaded_by = form_data.get("uploaded_by")

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

            faculty = session.exec(
                select(FacultyProfile)
                .where(
                    FacultyProfile.faculty_id == uploaded_by
                )
            ).first()

            if not faculty:

                raise HTTPException(
                    status_code=404,
                    detail="Faculty not found."
                )

            resource = LmsResource(

                course_code=course_code,

                uploaded_by=uploaded_by,

                title=form_data.get(
                    "title",
                    ""
                ),

                resource_type=form_data.get(
                    "resource_type",
                    "PDF"
                ),

                description=form_data.get(
                    "description",
                    ""
                ),

                file_path=form_data.get(
                    "file_path",
                    ""
                ),

                week_number=int(
                    form_data.get(
                        "week_number",
                        1
                    )
                )
            )

            session.add(resource)

            session.commit()

            session.refresh(resource)

            return resource

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
@router.get("/resources")
async def get_resources():

    with Session(engine) as session:

        return session.exec(
            select(LmsResource)
        ).all()
    
@router.get("/course/{course_code}")
async def get_course_resources(
        course_code: str):

    with Session(engine) as session:

        return session.exec(

            select(LmsResource)
            .where(
                LmsResource.course_code == course_code
            )

        ).all()
# UPDATE RESOUCES VISIBILTY 

@router.put("/resource/{id}/visibility")
async def toggle_visibility(
        id: int):

    with Session(engine) as session:

        resource = session.get(
            LmsResource,
            id
        )

        if not resource:

            raise HTTPException(
                status_code=404,
                detail="Resource not found."
            )

        resource.is_visible = not resource.is_visible

        session.add(resource)

        session.commit()

        session.refresh(resource)

        return resource
# DELETE RESOURCES 

@router.delete("/resource/{id}")
async def delete_resource(
        id: int):

    with Session(engine) as session:

        resource = session.get(
            LmsResource,
            id
        )

        if not resource:

            raise HTTPException(
                status_code=404,
                detail="Resource not found."
            )

        session.delete(resource)

        session.commit()

        return {
            "message":
            "Resource deleted successfully."
        }

