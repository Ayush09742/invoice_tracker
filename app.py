import streamlit as st
from datetime import date

from database import engine
from models import Base
from utils import generate_invoice_pdf
from utils import (
    add_invoice,
    get_invoices,
    delete_invoice,
    mark_paid,
    export_all_invoices_pdf,
    send_whatsapp_reminder,
    load_company_profile,
    save_company_profile,
    generate_invoice_pdf,
    reset_database,
    get_overdue_days,
    get_monthly_total,
    export_all_invoices_pdf,
    get_overdue_days,
)

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Pennywise",
    page_icon="💰",
    layout="wide",
)

USERNAME = "admin"
PASSWORD = "94517"


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login_screen():

    st.header("Login")

    username = st.text_input(
        "Username",
        key="login_user"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_pass"
    )

    # credentials (single line as requested)
    USERNAME, PASSWORD = "admin", "94517"

    if st.button("Login", key="login_btn"):

        if username == USERNAME and password == PASSWORD:

            st.session_state.logged_in = True

            st.rerun()

        else:

            st.error("Invalid login")


def dashboard():

    st.header("Dashboard")

    invoices = get_invoices()

    overdue = [
    inv for inv in get_invoices()
    if get_overdue_days(inv) > 0
]

    total = get_monthly_total()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Invoices", len(invoices))

    c2.metric("This Month Revenue", total)

    c3.metric("Overdue", len(overdue))

    st.divider()

    # EXPORT ALL INVOICES BUTTON
    pdf_all = export_all_invoices_pdf()

    st.download_button(
        label="Download All Invoices (PDF)",
        data=pdf_all,
        file_name="all_invoices.pdf",
        mime="application/pdf",
        key="download_all_pdf"
    )


def add_invoice_section():

    st.header("Add Invoice")

    client_name = st.text_input(
        "Client Name",
        key="add_name",
    )

    client_phone = st.text_input(
        "Client Phone",
        key="add_phone",
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        key="add_amount",
    )

    invoice_date = st.date_input(
        "Invoice Date",
        value=date.today(),
        key="add_date",
    )

    due_date = st.date_input(
        "Due Date",
        value=date.today(),
        key="add_due",
    )

    status = st.selectbox(
        "Status",
        ["Pending", "Paid"],
        key="add_status",
    )

    if st.button("Add Invoice", key="add_btn"):

        add_invoice(
            client_name,
            client_phone,
            amount,
            invoice_date,
            due_date,
            status,
        )

        st.success("Invoice added")

        st.rerun()


def invoice_list():

    st.header("All Invoices")

    invoices = get_invoices()

    if not invoices:

        st.info("No invoices yet")

        return

    for inv in invoices:

        overdue_days = get_overdue_days(inv)

        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

        # Invoice Number
        c1.write(inv.invoice_number)

        # Client
        c2.write(inv.client_name)

        # Amount
        c3.write(inv.amount)

        # Status Color
        if inv.status == "Paid":

            c4.success("Paid")

        elif overdue_days > 0:

            c4.error(f"Overdue {overdue_days} days")

        else:

            c4.warning("Pending")

        # Mark Paid
        if c5.button(
            "Mark Paid",
            key=f"paid_{inv.id}"
        ):

            mark_paid(inv.id)

            st.rerun()

        # Delete
        if c6.button(
            "Delete",
            key=f"delete_{inv.id}"
        ):

            delete_invoice(inv.id)

            st.rerun()

        # Send WhatsApp Reminder
        if c7.button(
            "Send Reminder",
            key=f"rem_{inv.id}"
        ):

            send_whatsapp_reminder(inv)

        # Download Single Invoice PDF
        pdf_data = generate_invoice_pdf(inv)

        c8.download_button(

            label="Download PDF",

            data=pdf_data,

            file_name=f"{inv.invoice_number}.pdf",

            mime="application/pdf",

            key=f"pdf_{inv.id}"

        )

def company_settings():

    st.header("Company Settings")

    profile = load_company_profile()
    payment_link = st.text_input(
    "Payment Link",
    value=profile.get("payment_link"),
    key="company_payment"
)

    name = st.text_input(
        "Company Name",
        value=profile.get("name"),
        key="company_name",
    )

    email = st.text_input(
        "Email",
        value=profile.get("email"),
        key="company_email",
    )

    contact = st.text_input(
        "Contact",
        value=profile.get("contact"),
        key="company_contact",
    )

    gst = st.text_input(
        "GST",
        value=profile.get("gst"),
        key="company_gst",
    )

    if st.button("Save Profile", key="save_profile"):

        save_company_profile(

            {
                "name": name,
                "email": email,
                "contact": contact,
                "gst": gst,
            }

        )

        st.success("Saved")


def factory_reset():

    st.sidebar.header("System")

    if st.sidebar.button(
        "Factory Reset",
        key="reset_btn",
    ):

        reset_database()

        st.success("All data cleared")

        st.rerun()


def main_app():

    factory_reset()

    dashboard()

    tab1, tab2, tab3 = st.tabs(
        [
            "Add Invoice",
            "Invoices",
            "Settings",
        ]
    )

    with tab1:
        add_invoice_section()

    with tab2:
        invoice_list()

    with tab3:
        company_settings()


if st.session_state.logged_in:

    main_app()

else:

    login_screen()