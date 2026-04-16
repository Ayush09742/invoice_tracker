import os
import json
import urllib.parse
import webbrowser
from datetime import datetime, date
from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

from database import SessionLocal, engine
from models import Invoice, Base

DB_FILE = "invoice.db"
PROFILE_FILE = "company_profile.json"


# ---------------- COMPANY PROFILE ----------------

def load_company_profile():

    if not os.path.exists(PROFILE_FILE):

        return {
            "name": "",
            "contact": "",
            "email": "",
            "gst": "",
            "payment_link": ""
        }

    with open(PROFILE_FILE, "r") as f:

        return json.load(f)


def save_company_profile(profile):

    with open(PROFILE_FILE, "w") as f:

        json.dump(profile, f)


get_company_profile = load_company_profile


# ---------------- INVOICE NUMBER ----------------

def generate_invoice_number():

    db = SessionLocal()

    last = (
        db.query(Invoice)
        .order_by(Invoice.id.desc())
        .first()
    )

    if not last:

        return "INV-0001"

    last_num = int(last.invoice_number.split("-")[1])

    new = last_num + 1

    return f"INV-{new:04d}"


# ---------------- ADD INVOICE ----------------

def add_invoice(
    client_name,
    client_phone,
    amount,
    invoice_date,
    due_date,
    status,
):

    db = SessionLocal()

    invoice_number = generate_invoice_number()

    new_invoice = Invoice(

        invoice_number=invoice_number,
        client_name=client_name,
        client_phone=client_phone,
        amount=amount,
        date=invoice_date,
        due_date=due_date,
        status=status,
        created_at=datetime.now(),

    )

    db.add(new_invoice)
    db.commit()

    return new_invoice


def get_invoices():

    db = SessionLocal()

    return (
        db.query(Invoice)
        .order_by(Invoice.id.desc())
        .all()
    )


def delete_invoice(invoice_id):

    db = SessionLocal()

    inv = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if inv:

        db.delete(inv)
        db.commit()


def mark_paid(invoice_id):

    db = SessionLocal()

    inv = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if inv:

        inv.status = "Paid"
        db.commit()


# ---------------- OVERDUE ----------------

def get_overdue_days(invoice):

    if invoice.status == "Paid":
        return 0

    today = date.today()

    if today > invoice.due_date:

        return (today - invoice.due_date).days

    return 0


def get_monthly_total():

    today = date.today()

    db = SessionLocal()

    invoices = db.query(Invoice).all()

    total = 0

    for inv in invoices:

        if inv.date.month == today.month:

            total += inv.amount

    return total


def get_client_ledger(name):

    db = SessionLocal()

    return (
        db.query(Invoice)
        .filter(Invoice.client_name == name)
        .all()
    )


# ---------------- EXPORT ALL PDF ----------------

def export_all_invoices_pdf():

    invoices = get_invoices()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(8.27 * inch, 11.69 * inch),
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>All Invoices Report</b>",
            styles["Title"],
        )
    )

    elements.append(Spacer(1, 20))

    data = [["Invoice", "Client", "Amount", "Status"]]

    for inv in invoices:

        data.append([
            inv.invoice_number,
            inv.client_name,
            inv.amount,
            inv.status
        ])

    table = Table(data)

    table.setStyle(

        TableStyle(

            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black)
            ]

        )

    )

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer
def generate_invoice_pdf(invoice):

    company = load_company_profile()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(8.27 * inch, 11.69 * inch),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=60,
    )

    styles = getSampleStyleSheet()

    elements = []

    header = Paragraph(
        f"""
        <b>{company.get("name")}</b><br/>
        {company.get("email")}<br/>
        {company.get("contact")}<br/>
        GST: {company.get("gst")}
        """,
        styles["Normal"],
    )

    elements.append(header)
    elements.append(Spacer(1, 20))

    title = Paragraph(
        "<para align=center><font size=18><b>INVOICE</b></font></para>",
        styles["Normal"],
    )

    elements.append(title)
    elements.append(Spacer(1, 25))

    data = [
        ["Invoice Number", invoice.invoice_number],
        ["Client Name", invoice.client_name],
        ["Amount", f"₹ {invoice.amount}"],
        ["Invoice Date", str(invoice.date)],
        ["Due Date", str(invoice.due_date)],
        ["Status", invoice.status],
    ]

    table = Table(data, colWidths=[180, 300])

    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 50))

    footer = Paragraph(
        "<para alignment='right'>"
        "<font size=9 color=grey>"
        "Powered by Pennywise"
        "</font>"
        "</para>",
        styles["Normal"],
    )

    elements.append(footer)

    doc.build(elements)

    buffer.seek(0)

    return buffer


# ---------------- WHATSAPP ----------------

import urllib.parse

def generate_whatsapp_link(invoice, company_profile):

    phone = invoice.client_phone

    message = f"""
Hello {invoice.client_name},

This is a reminder for your invoice.

Invoice Number: {invoice.invoice_number}
Amount: ₹{invoice.amount}
Due Date: {invoice.due_date}

Please make the payment at your earliest convenience.

Regards,
{company_profile.get("company_name", "Your Company")}
"""

    encoded_message = urllib.parse.quote(message)

    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"

    return whatsapp_url
def clear_company_settings():

    import os

    PROFILE_FILE = "company_profile.json"

    try:

        if os.path.exists(PROFILE_FILE):

            os.remove(PROFILE_FILE)

            print("Company profile deleted")

        else:

            print("Company profile file not found")

        return True

    except Exception as e:

        print("CLEAR COMPANY SETTINGS ERROR:", e)

        return False

    
# ---------------- FACTORY RESET ----------------

def reset_database():

    import sqlite3

    DB_FILE = "invoice.db"

    try:

        conn = sqlite3.connect(DB_FILE)

        cursor = conn.cursor()

        # Delete all invoices
        cursor.execute("DELETE FROM invoices")

        # Try resetting auto-increment safely
        try:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name='invoices'"
            )
        except sqlite3.OperationalError:
            # sqlite_sequence may not exist — that's OK
            pass

        conn.commit()

        conn.close()

        print("All invoices cleared")

        return True

    except Exception as e:

        print("RESET DATABASE ERROR:", e)

        return False