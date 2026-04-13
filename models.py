from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from database import Base


class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(String, unique=True)

    client_name = Column(String)

    client_phone = Column(String)

    amount = Column(Float)

    date = Column(Date)

    due_date = Column(Date)

    status = Column(String)

    created_at = Column(DateTime)
    from database import SessionLocal
from datetime import datetime
from database import SessionLocal
from datetime import datetime


def add_invoice(
    invoice_number,
    client_name,
    client_phone,
    amount,
    date,
    due_date
):

    session = SessionLocal()

    new_invoice = Invoice(
        invoice_number=invoice_number,
        client_name=client_name,
        client_phone=client_phone,
        amount=amount,
        date=date,
        due_date=due_date,
        status="Pending",
        created_at=datetime.now()
    )

    session.add(new_invoice)
    session.commit()
    session.close()

    return new_invoice


def get_all_invoices():

    session = SessionLocal()

    invoices = (
        session.query(Invoice)
        .order_by(Invoice.id.desc())
        .all()
    )

    session.close()

    return invoices


def mark_invoice_paid(invoice_id):

    session = SessionLocal()

    invoice = (
        session.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if invoice:
        invoice.status = "Paid"
        session.commit()

    session.close()


def delete_invoice(invoice_id):

    session = SessionLocal()

    invoice = (
        session.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if invoice:
        session.delete(invoice)
        session.commit()

    session.close()


def add_invoice(
    invoice_number,
    client_name,
    client_phone,
    amount,
    date,
    due_date
):

    session = SessionLocal()

    new_invoice = Invoice(
        invoice_number=invoice_number,
        client_name=client_name,
        client_phone=client_phone,
        amount=amount,
        date=date,
        due_date=due_date,
        status="Pending",
        created_at=datetime.now()
    )

    session.add(new_invoice)
    session.commit()
    session.close()

    return new_invoice


def get_all_invoices():

    session = SessionLocal()

    invoices = (
        session.query(Invoice)
        .order_by(Invoice.id.desc())
        .all()
    )

    session.close()

    return invoices


def mark_invoice_paid(invoice_id):

    session = SessionLocal()

    invoice = (
        session.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if invoice:
        invoice.status = "Paid"
        session.commit()

    session.close()


def delete_invoice(invoice_id):

    session = SessionLocal()

    invoice = (
        session.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if invoice:
        session.delete(invoice)
        session.commit()

    session.close()