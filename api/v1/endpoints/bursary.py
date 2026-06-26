"""
Bright Moon University
Bursary & Financial Services Engine
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

from models.academic import (
    StudentProfile,
    Invoice,
    Payment,
    FinancialClearance
)

router = APIRouter(
    prefix="/bursary",
    tags=["Bursary Engine"]
)

# ==========================================================
# FINANCIAL CLEARANCE ENGINE
# ==========================================================
def update_financial_clearance(
        session: Session,
        student_id: str):
    """
    Automatically evaluates student financial status.
    """

    invoices = session.exec(

        select(Invoice)
        .where(
            Invoice.student_id == student_id
        )

    ).all()

    if not invoices:
        return

    all_paid = all(
        invoice.status == "Paid"
        for invoice in invoices
    )

    clearance = session.exec(

        select(FinancialClearance)
        .where(
            FinancialClearance.student_id
            == student_id
        )

    ).first()

    if not clearance:

        clearance = FinancialClearance(
            student_id=student_id
        )

    clearance.is_cleared = all_paid

    clearance.clearance_note = (
        "Financial obligations satisfied."
        if all_paid
        else "Outstanding invoice balance exists."
    )

    session.add(clearance)

# ==========================================================
# INVOICE GENERATOR
# ==========================================================
def generate_invoice_reference():

    year = datetime.datetime.now().year

    timestamp = int(
        datetime.datetime.now().timestamp()
    )

    return f"INV-{year}-{timestamp}"


# ==========================================================
# TRANSACTION GENERATOR
# ==========================================================
def generate_transaction_reference():

    year = datetime.datetime.now().year

    timestamp = int(
        datetime.datetime.now().timestamp()
    )

    return f"TXN-{year}-{timestamp}"


# ==========================================================
# CREATE STUDENT INVOICE
# ==========================================================
@router.post(
    "/invoice",
    status_code=status.HTTP_201_CREATED
)
async def create_invoice(
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            student_id = form_data.get(
                "student_id"
            )

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

            invoice = Invoice(

                invoice_reference=
                generate_invoice_reference(),

                student_id=student_id,

                description=form_data.get(
                    "description",
                    "Tuition Fee"
                ),

                amount_due=float(
                    form_data.get(
                        "amount_due",
                        0
                    )
                ),

                semester=int(
                    form_data.get(
                        "semester",
                        1
                    )
                ),

                session_year=form_data.get(
                    "session_year",
                    "2026/2027"
                )
            )

            session.add(invoice)

            session.commit()

            session.refresh(invoice)

            return invoice

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

@router.get("/invoices")
async def get_invoices():

    with Session(engine) as session:

        return session.exec(
            select(Invoice)
        ).all()



@router.get("/student/{student_id}")
async def student_financial_profile(
        student_id: str):

    with Session(engine) as session:

        invoices = session.exec(

            select(Invoice)
            .where(
                Invoice.student_id == student_id
            )

        ).all()

        payments = session.exec(

            select(Payment)
            .where(
                Payment.student_id == student_id
            )

        ).all()

        clearance = session.exec(

            select(FinancialClearance)
            .where(
                FinancialClearance.student_id
                == student_id
            )

        ).first()

        return {

            "student_id": student_id,

            "invoices": invoices,

            "payments": payments,

            "clearance": clearance

        }

# ==========================================================
# RECORD PAYMENT
# ==========================================================
@router.post(
    "/payment",
    status_code=status.HTTP_201_CREATED
)
async def record_payment(
        request: Request):

    form_data = await request.form()

    with Session(engine) as session:

        try:

            invoice_reference = form_data.get(
                "invoice_reference"
            )

            invoice = session.exec(

                select(Invoice)
                .where(
                    Invoice.invoice_reference
                    == invoice_reference
                )

            ).first()

            if not invoice:

                raise HTTPException(
                    status_code=404,
                    detail="Invoice not found."
                )

            payment_amount = float(
                form_data.get(
                    "amount_paid",
                    0
                )
            )

            payment = Payment(

                transaction_reference=
                generate_transaction_reference(),

                invoice_reference=
                invoice_reference,

                student_id=
                invoice.student_id,

                amount_paid=
                payment_amount,

                payment_channel=
                form_data.get(
                    "payment_channel",
                    "Bank Transfer"
                ),

                payment_date=
                str(
                    datetime.date.today()
                )
            )

            session.add(payment)

            # -----------------------------------------
            # Update invoice balance
            # -----------------------------------------

            invoice.amount_paid += payment_amount

            if invoice.amount_paid >= invoice.amount_due:

                invoice.status = "Paid"

            elif invoice.amount_paid > 0:

                invoice.status = "Partial"

            session.add(invoice)

            # -----------------------------------------
            # Recalculate clearance
            # -----------------------------------------

            update_financial_clearance(
                session,
                invoice.student_id
            )

            session.commit()

            session.refresh(payment)

            return payment

        except Exception as e:

            session.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

# ==========================================================
# PAYMENT DIRECTORY
# ==========================================================
@router.get("/payments")
async def get_payments():

    with Session(engine) as session:

        return session.exec(
            select(Payment)
        ).all()
    

# ==========================================================
# STUDENT CLEARANCE STATUS
# ==========================================================
@router.get(
    "/clearance/{student_id}"
)
async def get_clearance_status(
        student_id: str):

    with Session(engine) as session:

        clearance = session.exec(

            select(FinancialClearance)
            .where(
                FinancialClearance.student_id
                == student_id
            )

        ).first()

        if not clearance:

            return {

                "student_id": student_id,

                "is_cleared": False,

                "message":
                "No clearance record found."
            }

        return clearance


# ==========================================================
# OUTSTANDING DEBTORS
# ==========================================================
@router.get("/debtors")
async def get_debtors():

    with Session(engine) as session:

        invoices = session.exec(

            select(Invoice)
            .where(
                Invoice.status != "Paid"
            )

        ).all()

        return invoices
    
