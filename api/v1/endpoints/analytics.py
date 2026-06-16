"""
The Bright Moon University - Administrative Big-Data Analytics
File: api/v1/endpoints/analytics.py
Description: Leverages Pandas pipelines to compute real-time student academic risk profiles.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database.connection import get_session
from models.academic import StudentProfile
import pandas as pd

router = APIRouter(prefix="/analytics", tags=["Admin Predictive Analytics Suite"])

@router.get("/attendance-risk")
async def calculate_attendance_risk_matrix(session: Session = Depends(get_session)):
    # 1. Pull raw data records straight from the SQLite engine database
    students = session.exec(select(StudentProfile)).all()
    
    if not students:
        return {"risk_alerts_count": 0, "flagged_candidates": []}
        
    # 2. Convert the SQLModel rows into a high-speed pandas DataFrame structure
    data_matrix = [
        {"id": s.student_id, "name": s.student_name, "dept": s.course_specialization, "attendance": s.attendance_pct}
        for s in students
    ]
    df = pd.DataFrame(data_matrix)
    
    # 3. Apply operational risk filter rules (Attendance < 75%)
    risk_df = df[df["attendance"] < 75.0]
    
    # 4. Export the resulting dataframe payload cleanly back to JSON formats
    flagged_records = risk_df.to_dict(orient="records")
    
    return {
        "total_evaluated_students": len(df),
        "risk_alerts_count": len(flagged_records),
        "flagged_candidates": flagged_records
    }