import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="QC Volume Calculator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Excel data
@st.cache_data
def load_data_from_file(uploaded_file):
    """Load data from uploaded Excel file"""
    xls = pd.ExcelFile(uploaded_file)
    df_mg6200 = pd.read_excel(uploaded_file, sheet_name="MG6200")
    df_mg6200_composite = pd.read_excel(uploaded_file, sheet_name="MG6200复合")
    
    # Clean data
    df_mg6200 = df_mg6200.dropna(how='all').reset_index(drop=True)
    df_mg6200_composite = df_mg6200_composite.dropna(how='all').reset_index(drop=True)
    
    return df_mg6200, df_mg6200_composite

def calculate_maximum(volume):
    """Calculate maximum using floor method"""
    if volume == 0:
        return 0
    result = 800 / volume
    return int(np.floor(result))

def calculate_vials_and_tests(volume, thaw_multiplier=0):
    """
    Calculate vials and test numbers
    thaw_multiplier: 0 for 0 thaw (volume + 200), 1 for 1 thaw (volume*2 + 200)
    """
    if thaw_multiplier == 0:
        total_volume = volume + 200
    else:
        total_volume = volume * 2 + 200
    
    # Determine vials based on total volume
    if total_volume <= 250:
        vials = 4
    elif total_volume <= 330:
        vials = 3
    elif total_volume <= 500:
        vials = 2
    else:
        vials = 1  # More than 500, only 1 vial
    
    # Calculate test numbers
    if volume + 200 == 0:
        tests = 0
    else:
        tests_per_vial = 1000 / (volume + 200)
        tests = int(np.floor(vials * tests_per_vial))
    
    return vials, tests

def get_volume_range_label(volume):
    """Get the volume range label for display"""
    if volume <= 250:
        return "≤ 250 µL"
    elif volume <= 330:
        return "250-330 µL"
    elif volume <= 500:
        return "330-500 µL"
    else:
        return "> 500 µL"

def display_results(total_volume, maximum, vials_0, tests_0, vials_1, tests_1):
    """Display calculation results"""
    st.markdown("---")
    st.markdown("### Calculation Results")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        st.metric("Total Sample Volume", f"{total_volume} µL")
        st.metric("Maximum (Floor)", f"{maximum}")
    
    with col2:
        st.markdown("#### 0 Thaw (Single Thaw)")
        volume_0 = total_volume + 200
        st.metric("Total Volume", f"{volume_0} µL", delta=get_volume_range_label(volume_0))
        st.metric("Max Dispensing Vials", f"{vials_0} vials")
        st.metric("Test Number (Group)", f"{tests_0}")
    
    with col3:
        st.markdown("#### 1 Thaw (Double Thaw)")
        volume_1 = total_volume * 2 + 200
        st.metric("Total Volume", f"{volume_1} µL", delta=get_volume_range_label(volume_1))
        st.metric("Max Dispensing Vials", f"{vials_1} vials")
        st.metric("Test Number (Group)", f"{tests_1}")
    
    # Detailed calculation process
    with st.expander("View Calculation Details"):
        st.markdown(f"**Total Sample Volume:** {total_volume} µL")
        st.markdown(f"**Maximum:** 800 / {total_volume} = {maximum} (floor method)")
        
        st.markdown("---")
        st.markdown("**0 Thaw (Single Thaw):**")
        st.markdown(f"- Total Volume = Sample Volume + 200 = {total_volume} + 200 = {volume_0} µL")
        st.markdown(f"- Volume Range: {get_volume_range_label(volume_0)}")
        st.markdown(f"- Dispensing Vials = {vials_0} vials")
        st.markdown(f"- Test Number = {vials_0} × (1000 / ({total_volume} + 200)) = {tests_0}")
        
        st.markdown("---")
        st.markdown("**1 Thaw (Double Thaw):**")
        st.markdown(f"- Total Volume = Sample Volume × 2 + 200 = {total_volume} × 2 + 200 = {volume_1} µL")
        st.markdown(f"- Volume Range: {get_volume_range_label(volume_1)}")
        st.markdown(f"- Dispensing Vials = {vials_1} vials")
        st.markdown(f"- Test Number = {vials_1} × (1000 / ({total_volume} + 200)) = {tests_1}")

def create_mono_qc_ui(df):
    """Create Mono QC interface"""
    # Get item list
    items = df['ItemName'].dropna().tolist()
    
    # QC name selection - using Items as QC names
    selected_qc = st.selectbox("Select QC Name", items)
    
    if selected_qc:
        # Get sample volume for the selected item
        row = df[df['ItemName'] == selected_qc]
        if not row.empty:
            sample_vol = row['Sample Vol (uL)'].values[0]
            
            st.markdown(f"**Selected Item:** {selected_qc}")
            st.markdown(f"Sample Volume: {sample_vol} µL")
            
            # Calculate all metrics
            total_volume = sample_vol
            maximum = calculate_maximum(total_volume)
            vials_0, tests_0 = calculate_vials_and_tests(total_volume, 0)
            vials_1, tests_1 = calculate_vials_and_tests(total_volume, 1)
            
            # Display results
            display_results(total_volume, maximum, vials_0, tests_0, vials_1, tests_1)
        else:
            st.warning("No data found for the selected item")

def create_multi_qc_ui(df_composite, df_mg6200):
    """Create Multi QC interface"""
    # Get QC names from first row (columns 1-13, since column 0 is empty)
    qc_names = df_composite.iloc[0, 1:14].dropna().tolist()
    
    selected_qc = st.selectbox("Select QC Name", qc_names)
    
    if selected_qc:
        # Find the corresponding column index
        col_index = None
        for i, col in enumerate(df_composite.columns[1:14], 1):
            if df_composite.iloc[0, i] == selected_qc:
                col_index = i
                break
        
        if col_index is not None:
            # Get all items under this QC column
            items = df_composite.iloc[1:, col_index].dropna().tolist()
            
            st.markdown(f"**{selected_qc} contains:**")
            st.write(f"Total {len(items)} items: {', '.join(items[:10])}" + ("..." if len(items) > 10 else ""))
            
            # Get sample volumes for each item
            item_volumes = {}
            for item in items:
                row = df_mg6200[df_mg6200['ItemName'] == item]
                if not row.empty:
                    item_volumes[item] = row['Sample Vol (uL)'].values[0]
            
            # Multi-select items
            selected_items = st.multiselect(
                "Select Items (µL)",
                options=items,
                default=items[:min(3, len(items))]
            )
            
            if selected_items:
                # Calculate total volume
                total_volume = sum(item_volumes.get(item, 0) for item in selected_items)
                
                # Display selected items with their volumes
                st.markdown("**Selected Items and Volumes:**")
                vol_df = pd.DataFrame({
                    'Item': selected_items,
                    'Volume (µL)': [item_volumes.get(item, 0) for item in selected_items]
                })
                st.dataframe(vol_df, hide_index=True, use_container_width=True)
                
                # Show total
                st.info(f"**Total Sample Volume: {total_volume} µL**")
                
                # Calculate all metrics
                maximum = calculate_maximum(total_volume)
                vials_0, tests_0 = calculate_vials_and_tests(total_volume, 0)
                vials_1, tests_1 = calculate_vials_and_tests(total_volume, 1)
                
                # Display results
                display_results(total_volume, maximum, vials_0, tests_0, vials_1, tests_1)
            else:
                st.info("Please select at least one item")

def main():
    # Header
    st.title("🧪 QC Volume Calculator")
    st.markdown("### Quality Control Sample Volume Calculator")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Mode selection
        mode = st.radio(
            "Select QC Type:",
            ["mono QC", "multi QC"],
            index=0,
            help="mono QC: Uses data from MG6200 sheet; multi QC: Uses data from MG6200复合 sheet"
        )
        
        st.divider()
        
        # File upload
        st.subheader("Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Excel File (各项目加样量.xlsx)",
            type=["xlsx", "xls"],
            help="Upload Excel file containing both 'MG6200' and 'MG6200复合' sheets"
        )
        
        # File format info
        with st.expander("📋 File Format Info"):
            st.markdown("**Required Sheets:**")
            st.markdown("- **MG6200**: Contains ItemName and Sample Vol")
            st.markdown("- **MG6200复合**: Contains QC groups with items")
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Load data
            df_mg6200, df_mg6200_composite = load_data_from_file(uploaded_file)
            
            # Display mode-specific interface
            if mode == "mono QC":
                st.subheader("🔬 Mono QC Mode")
                create_mono_qc_ui(df_mg6200)
            else:
                st.subheader("📊 Multi QC Mode")
                create_multi_qc_ui(df_mg6200_composite, df_mg6200)
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please make sure the file contains both 'MG6200' and 'MG6200复合' sheets with correct format.")
    else:
        # Display placeholder when no file uploaded
        st.info("👈 Please upload an Excel file from the sidebar to begin")
        
        st.markdown("### 📖 How to Use")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Step 1**")
            st.markdown("Upload your Excel file containing the QC data sheets")
        
        with col2:
            st.markdown("**Step 2**")
            st.markdown("Select either **mono QC** or **multi QC** mode")
        
        with col3:
            st.markdown("**Step 3**")
            st.markdown("Choose QC/items and view calculated results")
        
        st.divider()
        
        # Data format preview
        st.markdown("### 📊 Expected Data Format")
        
        tab1, tab2 = st.tabs(["MG6200 Sheet", "MG6200复合 Sheet"])
        
        with tab1:
            st.markdown("**Column Structure:**")
            st.markdown("""
            - **ItemName**: Test item names
            - **Sample Vol (uL)**: Sample volume in microliters
            - **Min Disp Vol**: Minimum dispensing volume (200 + Sample Vol)
            - **Maximum**: Maximum value (ROUNDDOWN(800/Sample Vol, 0))
            """)
        
        with tab2:
            st.markdown("**Column Structure:**")
            st.markdown("""
            - **QC Name**: Quality control names (first row)
            - **Items**: Test items listed under each QC column
            - **Total sample volume**: Sum of sample volumes (SUMIF formula)
            - **+Dead volume (200 uL)**: Total volume with dead volume added
            """)

if __name__ == "__main__":
    main()