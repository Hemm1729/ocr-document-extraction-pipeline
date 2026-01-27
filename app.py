
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="ContractIQ",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .red-flag {
        color: #ff4b4b;
        font-weight: bold;
    }
    .green-flag {
        color: #09ab3b;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 ContractIQ: Intelligent Contract Analysis")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["New Analysis", "History"])

if page == "New Analysis":
    st.header("Upload Contract")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Analyze Contract", type="primary"):
            with st.spinner("Processing... Extracting Data, Checking VIN, and Analyzing Fairness..."):
                try:
                    files = {"file": uploaded_file}
                    response = requests.post(f"{API_URL}/process", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        data = result.get("extraction", {})
                        
                        st.success("Analysis Complete!")
                        
                        # --- Section 1: Financial Overview ---
                        st.subheader("💰 Financial Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Sale Price", data.get("Total_Sale_Price", "N/A"))
                        with col2:
                            st.metric("APR", data.get("APR", "N/A"))
                        with col3:
                            st.metric("Monthly Payment", data.get("Monthly_Payment", "N/A"))
                        with col4:
                            st.metric("Amount Financed", data.get("Amount_Financed", "N/A"))

                        # --- Section 2: Fairness Analysis ---
                        st.divider()
                        st.subheader("⚖️ Fairness Analysis")
                        
                        score = data.get("fairness_score", 0)
                        
                        # Gauge-like display
                        try:
                            score = float(score)
                        except (ValueError, TypeError):
                            score = 0
                            
                        st.progress(min(score / 100, 1.0))
                        st.caption(f"Fairness Score: {int(score)}/100")
                        
                        f_col1, f_col2 = st.columns(2)
                        
                        with f_col1:
                            st.error("🚩 Red Flags (Risks)")
                            red_flags = data.get("red_flags", [])
                            if red_flags:
                                for flag in red_flags:
                                    st.markdown(f"- {flag}")
                            else:
                                st.write("No major red flags detected.")
                                
                        with f_col2:
                            st.success("✅ Green Flags (Benefits)")
                            green_flags = data.get("green_flags", [])
                            if green_flags:
                                for flag in green_flags:
                                    st.markdown(f"- {flag}")
                            else:
                                st.write("No specific green flags noted.")

                        if "summary" in data:
                            st.info(f"**Summary:** {data['summary']}")

                        # --- Section 3: Vehicle Details ---
                        st.divider()
                        st.subheader("🚗 Vehicle Information")
                        
                        if "vin_details" in data:
                            v = data["vin_details"]
                            # Convert to DataFrame for Table
                            # Filter out 'error' if present or just show all
                            df_vin = pd.DataFrame(list(v.items()), columns=["Attribute", "Value"])
                            st.table(df_vin)
                            
                            st.caption(f"VIN: {data.get('VIN', 'N/A')}")
                        else:
                            st.warning(f"VIN not verified. Extracted: {data.get('VIN', 'N/A')}")

                        # --- Other Details ---
                        st.subheader("📋 Other Details")
                        details_list = []
                        excluded_keys = ["Total_Sale_Price", "APR", "Monthly_Payment", "Amount_Financed", 
                                         "fairness_score", "red_flags", "green_flags", "summary", 
                                         "vin_details", "VIN"]
                                         
                        for key, value in data.items():
                            if key not in excluded_keys and isinstance(value, (str, int, float)):
                                details_list.append({"Field": key, "Value": value})
                                
                        if details_list:
                            st.table(pd.DataFrame(details_list))
                        else:
                            st.info("No other details found.")


                            
                    else:
                        st.error(f"Error processing file: {response.text}")
                        
                except Exception as e:
                    st.error(f"Failed to connect to API: {e}")

elif page == "History":
    st.header("Analysis History")
    
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            docs = response.json()
            
            if docs:
                df = pd.DataFrame(docs)
                df['upload_timestamp'] = pd.to_datetime(df['upload_timestamp'])
                
                # Table with Delete Option
                for index, row in df.iterrows():
                    col1, col2, col3, col4 = st.columns([1, 4, 3, 2])
                    with col1:
                        st.write(f"#{row['id']}")
                    with col2:
                        st.write(row['filename'])
                    with col3:
                         st.write(row['upload_timestamp']) 
                    with col4:
                        if st.button("Delete", key=f"del_{row['id']}"):
                            try:
                                res = requests.delete(f"{API_URL}/documents/{row['id']}")
                                if res.status_code == 200:
                                    st.success("Deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete.")
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                st.divider()
                
                # Detail View
                st.subheader("Load Details")
                doc_id = st.number_input("Enter ID to View", min_value=1, step=1)
                if st.button("Load"):
                     res = requests.get(f"{API_URL}/results/{doc_id}")
                     if res.status_code == 200:
                         data = res.json()
                         # Normalized check for extraction data (API vs DB schema)
                         ext = data.get("extraction") or data.get("extracted_data")

                         # Improved Detail View
                         if ext:
                             
                             st.markdown(f"### 📄 {data.get('filename', 'Document')}")
                             
                             # Financials
                             c1, c2, c3 = st.columns(3)
                             c1.metric("APR", ext.get("APR", "N/A"))
                             c2.metric("Monthly Payment", ext.get("Monthly_Payment", "N/A"))
                             c3.metric("Total Price", ext.get("Total_Sale_Price", "N/A"))
                             
                             st.divider()
                             
                             # Fairness
                             score = ext.get("fairness_score", 0)
                             try:
                                 score = float(score)
                             except: 
                                 score = 0
                             st.progress(min(score/100, 1.0))
                             st.caption(f"Fairness Score: {int(score)}/100")
                             
                             fc1, fc2 = st.columns(2)
                             with fc1:
                                 st.error("Red Flags")
                                 for f in ext.get("red_flags", []):
                                     st.markdown(f"- {f}")
                             with fc2:
                                 st.success("Green Flags")
                                 for f in ext.get("green_flags", []):
                                     st.markdown(f"- {f}")
                                     
                             if "summary" in ext:
                                 st.info(f"**Summary**: {ext['summary']}")

                             # Vehicle Details
                             st.divider()
                             st.markdown("### 🚗 Vehicle Information")
                             if "vin_details" in ext:
                                 v = ext["vin_details"]
                                 df_vin = pd.DataFrame(list(v.items()), columns=["Attribute", "Value"])
                                 st.table(df_vin)
                                 
                                 st.caption(f"VIN: {ext.get('VIN', 'N/A')}")
                             else:
                                 st.warning(f"VIN not verified. Extracted: {ext.get('VIN', 'N/A')}")

                             # Other Details
                             st.markdown("### 📋 Other Details")
                             details_list = []
                             excluded_keys = ["Total_Sale_Price", "APR", "Monthly_Payment", "Amount_Financed", 
                                              "fairness_score", "red_flags", "green_flags", "summary", 
                                              "vin_details", "VIN"]

                             for key, value in ext.items():
                                 if key not in excluded_keys and isinstance(value, (str, int, float)):
                                     details_list.append({"Field": key, "Value": value})
                                     
                             if details_list:
                                 st.table(pd.DataFrame(details_list))


                     else:
                         st.error("Document not found.")
            else:
                st.info("No documents found.")
        else:
            st.error("Failed to fetch history.")
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")

