"""
The Bright Moon University - Student Action Endpoints
File: api/v1/endpoints/students.py
Description: Handles document delivery pipelines and auxiliary campus service requests.
"""

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from sqlmodel import Session
from database.connection import get_session
from models.academic import ServiceRequest
import os

router = APIRouter(prefix="/student", tags=["Student Workspace Services"])

@router.post("/apply-service")
async def process_service_application(
    student_id: str = Form(...),
    service_type: str = Form(...), # "hostel", "bus", "library"
    description: str = Form(...),
    session: Session = Depends(get_session)
):
    new_request = ServiceRequest(
        student_id=student_id, service_type=service_type, description=description, status="Pending Review"
    )
    session.add(new_request)
    session.commit()
    return {"status": "Application submitted successfully.", "service": service_type}


@router.post("/upload-assignment/{course_code}")
async def submit_pdf_assignment(
    course_code: str,
    student_id: str = Form(...),
    assignment_file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # Enforce strict PDF formatting constraints
    if not assignment_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Validation Error: Only PDF documents are authorized for upload submissions.")
        
    # Standardize a secure storage path destination directory
    storage_dir = f"storage/submissions/{course_code}"
    os.makedirs(storage_dir, exist_ok=True)
    
    file_destination = os.path.join(storage_dir, f"{student_id}_final_task.pdf")
    
    with open(file_destination, "wb") as buffer:
        buffer.write(await assignment_file.read())
        
    return {"status": "Coursework successfully delivered to faculty repository.", "saved_path": file_destination}