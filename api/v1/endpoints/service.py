"""
Bright Moon University
Service Desk Management Engine
"""

import datetime

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    status
)

from sqlmodel import (
    Session,
    select
)

from database.connection import engine

from models.academic import ServiceRequest

router = APIRouter(
    prefix="/service",
    tags=["Service Desk"]
)

# ==========================================================
# CREATE SERVICE REQUEST
# ==========================================================
@router.post(
    "/request",
    status_code=status.HTTP_201_CREATED
)
async def create_service_request(
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            ticket = ServiceRequest(

                requester_id=form_data.get(
                    "requester_id",
                    ""
                ),

                requester_type=form_data.get(
                    "requester_type",
                    "Student"
                ),

                request_type=form_data.get(
                    "request_type",
                    "General"
                ),

                title=form_data.get(
                    "title",
                    ""
                ),

                description=form_data.get(
                    "description",
                    ""
                ),

                assigned_department=form_data.get(
                    "assigned_department",
                    "Registry"
                ),

                created_at=str(
                    datetime.datetime.now()
                )
            )

            session.add(ticket)

            session.commit()

            session.refresh(ticket)

            return ticket

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        
# ==========================================================
# ALL SERVICE REQUESTS
# ==========================================================
@router.get("/requests")
async def get_requests():

    with Session(engine) as session:

        return session.exec(
            select(ServiceRequest)
        ).all()
    

# ==========================================================
# GET REQUEST
# ==========================================================
@router.get("/request/{request_id}")
async def get_request(
        request_id: int):

    with Session(engine) as session:

        ticket = session.get(
            ServiceRequest,
            request_id
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Request not found."
            )

        return ticket

# ==========================================================
# UPDATE REQUEST STATUS
# ==========================================================
@router.put(
    "/request/{request_id}/status"
)
async def update_request_status(
        request_id: int,
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        ticket = session.get(
            ServiceRequest,
            request_id
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Request not found."
            )

        ticket.status = form_data.get(
            "status",
            ticket.status
        )

        ticket.response_note = form_data.get(
            "response_note",
            ticket.response_note
        )

        session.add(ticket)

        session.commit()

        session.refresh(ticket)

        return ticket
    

# ==========================================================
# USER REQUEST HISTORY
# ==========================================================
@router.get(
    "/requester/{requester_id}"
)
async def get_user_requests(
        requester_id: str):

    with Session(engine) as session:

        return session.exec(

            select(ServiceRequest)
            .where(
                ServiceRequest.requester_id
                == requester_id
            )

        ).all()

# ==========================================================
# DEPARTMENT WORK QUEUE
# ==========================================================
@router.get(
    "/department/{department}"
)
async def department_queue(
        department: str):

    with Session(engine) as session:

        return session.exec(

            select(ServiceRequest)
            .where(
                ServiceRequest.assigned_department
                == department
            )

        ).all()

# ==========================================================
# DELETE REQUEST
# ==========================================================
@router.delete(
    "/request/{request_id}"
)
async def delete_request(
        request_id: int):

    with Session(engine) as session:

        ticket = session.get(
            ServiceRequest,
            request_id
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Request not found."
            )

        session.delete(ticket)

        session.commit()

        return {
            "message":
            "Request deleted successfully."
        }
