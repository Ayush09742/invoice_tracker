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