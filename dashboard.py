import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Rajesh Kirana Store - AI Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛒 Kirana Automation")
st.sidebar.image("https://img.icons8.com/color/96/000000/shop.png", width=100)
menu = st.sidebar.radio("Navigation", ["Overview", "Inventory", "WhatsApp Orders", "OCR Digitization", "Invoices"])

# Header
st.title("Namaste, Rajesh! 🙏")
st.subheader(f"Store Status - {datetime.now().strftime('%d %B %Y')}")

# Backend URL (FastAPI)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if menu == "Overview":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Today's Orders", "12", "+2")
    with col2:
        st.metric("Total Revenue", "₹4,520", "+₹850")
    with col3:
        st.metric("Low Stock Items", "5", "-1")
    with col4:
        st.metric("Active Webhook", "Healthy", delta_color="normal")

    st.markdown("---")
    
    st.subheader("Recent WhatsApp Orders")
    # Mock data for demonstration
    recent_orders = pd.DataFrame({
        'Customer': ['Amit', 'Suresh', 'Priya', 'Rahul'],
        'Message': ['2kg sugar, 1kg atta', '1 lux soap, 5kg rice', '2 litre milk, 1 bread', '10kg wheat'],
        'Status': ['Processed', 'Pending', 'Delivered', 'Processed'],
        'Amount': ['₹145', '₹320', '₹90', '₹450']
    })
    st.table(recent_orders)

elif menu == "Inventory":
    st.subheader("Inventory Management")
    # In a real app, this would fetch from SQLite via FastAPI
    inventory_data = pd.DataFrame({
        'Item Name': ['Sugar (Madhur)', 'Atta (Aashirvaad)', 'Lux Soap', 'Milk (Amul)', 'Rice (Basmati)'],
        'Stock': [45, 12, 85, 20, 150],
        'Unit': ['kg', 'kg', 'pcs', 'litres', 'kg'],
        'Price': [45, 55, 35, 65, 95],
        'GST': ['5%', '0%', '18%', '0%', '5%']
    })
    
    st.dataframe(inventory_data, use_container_width=True)
    
    with st.expander("Add New Item"):
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Item Name")
        with c2: st.number_input("Quantity", min_value=0)
        with c3: st.selectbox("Unit", ["kg", "g", "pcs", "litres", "packets"])
        st.button("Update Stock")

elif menu == "OCR Digitization":
    st.subheader("Magic Photo Uploader (OCR)")
    st.info("Upload a photo of your handwritten ledger or invoice to digitize it instantly.")
    
    uploaded_file = st.file_uploader("Choose a ledger image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Ledger', use_column_width=True)
        if st.button("Start AI Digitization"):
            with st.spinner('Processing with Tesseract OCR...'):
                # Mock result
                st.success("Digitization Complete!")
                st.write("### Extracted Items:")
                extracted = pd.DataFrame({
                    'Item': ['Sugar', 'Atta', 'Soap'],
                    'Qty': ['2kg', '5kg', '2pcs'],
                    'Confidence': ['98%', '95%', '92%']
                })
                st.table(extracted)
                st.button("Sync to Inventory")

elif menu == "WhatsApp Orders":
    st.subheader("Live WhatsApp Feed")
    st.write("Real-time order parsing using Hinglish NLP.")
    
    # Simulation of incoming messages
    with st.container():
        st.markdown("""
        **Amit (987xxx3210):** *'2kg chini aur 1 packet surf excel bhej do'*
        > **AI Bot:** Available! Total ₹245. Generating invoice...
        """)
        st.markdown("---")
        st.markdown("""
        **Priya (912xxx4567):** *'Need 1 bread and 2 eggs'*
        > **AI Bot:** Out of stock: Eggs. Available: Bread.
        """)

elif menu == "Invoices":
    st.subheader("GST Invoice History")
    st.write("Download and send professional invoices with UPI QR codes.")
    
    invoices = pd.DataFrame({
        'Invoice ID': ['INV-2026-001', 'INV-2026-002', 'INV-2026-003'],
        'Customer': ['Amit', 'Rahul', 'Suresh'],
        'Date': ['2026-02-15', '2026-02-15', '2026-02-14'],
        'Total': ['₹245', '₹450', '₹320']
    })
    st.dataframe(invoices, use_container_width=True)
    st.button("Generate New Manual Invoice")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Developed with ❤️ by [Databloom AI](https://databloom.ai)")
