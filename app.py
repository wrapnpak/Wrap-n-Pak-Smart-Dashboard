import streamlit as st
import pandas as pd

st.set_page_config(page_title="Order Analysis Dashboard", layout="wide")

st.title("📦 SKU & City Order Analysis")

# Define the target SKUs
TARGET_SKUS = {
    10264594: "Chequered Sheet",
    10258817: "Twin Tone Roll",
    10273819: "Brown Roll",
    10258800: "Baking Sheet"
}

uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx', 'csv'])

if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    
    # Ensure date column is datetime
    df['Order Date Date'] = pd.to_datetime(df['Order Date Date'])
    
    # Sidebar for Date Selection
    all_dates = sorted(df['Order Date Date'].unique())
    selected_date = st.date_input("Select Date for Analysis", value=all_dates[-1])
    selected_date = pd.to_datetime(selected_date)

    if st.button("Run Analysis"):
        # 1. Filter data for the specific date
        day_data = df[df['Order Date Date'] == selected_date]
        
        # 2. Filter data up to the specific date (for averages)
        cumulative_data = df[df['Order Date Date'] <= selected_date]
        
        # Get all unique cities from the ENTIRE dataset to ensure they are all shown
        all_cities = df['Customer City'].unique()

        st.header(f"Analysis for {selected_date.date()}")

        # --- SECTION 1: TOTAL ORDERS PER SKU ---
        st.subheader("Total Orders for Specific SKUs")
        sku_summary = []
        for sku_id, name in TARGET_SKUS.items():
            total = day_data[day_data['Item ID'] == sku_id]['Orders'].sum()
            sku_summary.append({"Item ID": sku_id, "Product Name": name, "Total Orders": total})
        st.table(pd.DataFrame(sku_summary))

        # --- SECTION 2: CITY BREAKDOWN ---
        st.subheader("City-wise Breakdown & Daily Averages")
        
        city_results = []
        for city in all_cities:
            city_day_data = day_data[day_data['Customer City'] == city]
            city_cum_data = cumulative_data[cumulative_data['Customer City'] == city]
            
            # Unique dates for this city in history
            unique_days = city_cum_data['Order Date Date'].nunique()
            
            # Calculations
            total_orders_today = city_day_data['Orders'].sum()
            avg_orders_per_day = city_cum_data['Orders'].sum() / unique_days if unique_days > 0 else 0
            
            row = {
                "Customer City": city,
                "Total Orders (Today)": total_orders_today,
                "Avg Orders/Day (Historical)": round(avg_orders_per_day, 2)
            }
            
            # SKU specific averages per city
            for sku_id, name in TARGET_SKUS.items():
                sku_city_cum = city_cum_data[city_cum_data['Item ID'] == sku_id]
                sku_avg = sku_city_cum['Orders'].sum() / unique_days if unique_days > 0 else 0
                row[f"{name} (Avg/Day)"] = round(sku_avg, 2)
                
            city_results.append(row)

        st.dataframe(pd.DataFrame(city_results), use_container_width=True)

        # --- SECTION 3: OVERALL TOTAL ---
        net_total = day_data['Orders'].sum()
        st.metric("Net Total Orders Overall", net_total)
