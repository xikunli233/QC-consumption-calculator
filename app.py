import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# 内置数据（从你的 Excel 提取）
# ============================================================

# ---- MG6200 数据 ----
mg6200_data = {
    "ItemName": [
        "HIV", "IL-10", "TNF-a", "TSH", "ALD", "PTH", "Renin", "S100",
        "CT", "ACTH", "hs-cTnI", "IL-1β", "AF3", "AMH", "AngI", "AngII",
        "Anti-TSHR", "BNP", "CG", "CIV", "Cortisol", "E2", "E3", "FT3",
        "HA", "HBeAb", "HBeAb quant", "HBsAb", "HBsAg", "HBcAb",
        "HBcAb quant", "hs-cTnT", "IAA", "IL-8", "LN", "NT-proBNP",
        "PIVKA II", "PⅢP N-P", "proGRP", "T", "T3", "Tg", "TMAb", "TP",
        "CK-MB", "Anti-HCV", "PIIIPN-P", "G17", "LH", "rT3", "CA72-4",
        "DHEA-S", "P", "TG-Ab", "C-P", "FPSA", "HBP", "IL-6", "INS",
        "NSE", "PCT", "PLGF", "PRL", "ST2", "TAT", "tPSA", "CA 125",
        "CYFRA 21-1", "FSH", "GH", "PGI", "PGII", "25-OH-VD", "FT4",
        "HBeAg", "HBeAg quant", "HE4", "Osteocalcin", "TPO-Ab", "VB12",
        "CA242", "SCC", "CA 15-3", "CA 19-9", "lgE", "AFP", "CA50",
        "CEA", "CMV IgG", "CMV IgM", "CRP", "D-Dimer", "FABP", "FDP",
        "FER", "Free-β-HCG", "HbA1c", "HCG+β", "HSV-II IgG", "HSV-II IgM",
        "HSV-I IgG", "HSV-I IgM", "IGF-1", "IGFBP-3", "IL-2R", "Lp-PLA2",
        "Myo", "NGAL", "PAPP-A", "PIC", "Rubella IgG", "Rubella IgM",
        "SAA", "SHBG", "T4", "TM", "Toxo IgG", "Toxo IgM", "tPAI-C", "β-MG"
    ],
    "Sample Vol (uL)": [
        100, 100, 100, 100, 99, 99, 99, 99,
        90, 75, 75, 75, 50, 50, 50, 50,
        50, 50, 50, 50, 50, 50, 50, 50,
        50, 50, 50, 50, 50, 50, 50, 50,
        50, 50, 50, 50, 50, 50, 50, 50,
        50, 50, 50, 50, 50, 50, 50, 49,
        49, 40, 29, 25, 25, 25, 20, 20,
        20, 20, 20, 20, 20, 20, 20, 20,
        20, 20, 19, 19, 19, 19, 19, 15,
        15, 15, 15, 15, 15, 15, 14, 14,
        11, 11, 11, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10
    ]
}
df_mg6200_builtin = pd.DataFrame(mg6200_data)

# ---- MG6200复合 数据 ----
# QC名称（14列，从B到O）
qc_names = [
    "Thyroid function series Multi Control 1",
    "Thyroid function series Multi Control 2",
    "Hormone series Multi Control 1",
    "Hormone series Multi Control 2",
    "Infectious disease Multi Control 1",
    "Infectious disease Multi Control 2",
    "Cardiovascular series Multi Control 2",
    "Tumor series Multi Control 1",
    "Tumor series Multi Control 2",
    "Tumor series Multi Control 3",
    "Inflammation series Multi Control",
    "Liver Fibrosis series Multi Control",
    "TORCH IgG Multi Control",
    "TORCH IgM Multi Control"
]

# 每个QC下的项目列表（从表中提取）
qc_items = {
    "Thyroid function series Multi Control 1": ["FT3", "FT4", "T3", "T4", "TSH"],
    "Thyroid function series Multi Control 2": ["FT3", "FT4", "T3", "T4", "TSH", "TG-Ab", "TPO-Ab", "Tg", "Anti-TSHR", "rT3", "TMAb"],
    "Hormone series Multi Control 1": ["FSH", "PRL", "LH", "HCG+β", "T", "P", "E2", "E3"],
    "Hormone series Multi Control 2": ["AMH", "SHBG", "GH", "DHEA-S"],
    "Infectious disease Multi Control 1": ["HBsAg", "HBeAg quant", "Anti-HCV", "TP", "HIV"],
    "Infectious disease Multi Control 2": ["HBsAb", "HBeAb quant", "HBeAb quant", "HBcAb quant", "HIV"],  # 注意有两个 HBeAb quant，按原表保留
    "Cardiovascular series Multi Control 2": ["hs-cTnI", "hs-cTnT", "CK-MB", "Myo", "BNP", "NT-proBNP", "D-Dimer"],
    "Tumor series Multi Control 1": ["AFP", "CEA", "CA 125", "CA 19-9", "CA 15-3", "CA72-4", "CYFRA 21-1", "tPSA", "fPSA", "SCC", "NSE", "ProGRP"],
    "Tumor series Multi Control 2": ["CA242", "CA50", "HE4", "S100"],
    "Tumor series Multi Control 3": ["PGI", "PGII", "G17"],
    "Inflammation series Multi Control": ["CRP", "PCT", "IL-6", "SAA"],
    "Liver Fibrosis series Multi Control": ["HA", "CG", "PIIIPN-P", "CIV", "LN"],
    "TORCH IgG Multi Control": ["HSV-I IgG", "HSV-II IgG", "TOXO IgG", "Rubella IgG", "CMV IgG"],
    "TORCH IgM Multi Control": ["HSV-I IgM", "HSV-II IgM", "TOXO IgM", "Rubella IgM", "CMV IgM"]
}

# ============================================================
# 核心计算函数
# ============================================================

def calculate_maximum(volume):
    if volume == 0:
        return 0
    return int(np.floor(800 / volume))

def calculate_vials_and_tests(volume, thaw_multiplier=0):
    """
    thaw_multiplier: 0 -> 0 thaw (volume + 200)
                    1 -> 1 thaw (volume*2 + 200)
    """
    if thaw_multiplier == 0:
        total_volume = volume + 200
    else:
        total_volume = volume * 2 + 200

    if total_volume <= 250:
        vials = 4
    elif total_volume <= 330:
        vials = 3
    elif total_volume <= 500:
        vials = 2
    else:
        vials = 1

    if volume + 200 == 0:
        tests = 0
    else:
        tests_per_vial = 1000 / (volume + 200)
        tests = int(np.floor(vials * tests_per_vial))

    return vials, tests

def get_volume_range_label(volume):
    if volume <= 250:
        return "≤ 250 µL"
    elif volume <= 330:
        return "250-330 µL"
    elif volume <= 500:
        return "330-500 µL"
    else:
        return "> 500 µL"

def display_results(total_volume, maximum, vials_0, tests_0, vials_1, tests_1):
    st.markdown("---")
    st.markdown("### Calculation Results")

    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.metric("Total Sample Volume", f"{total_volume} µL")
        st.metric("Maximum (Floor)", f"{maximum}")

    with col2:
        st.markdown("#### 0 Thaw (Single Thaw)")
        vol_0 = total_volume + 200
        st.metric("Total Volume", f"{vol_0} µL", delta=get_volume_range_label(vol_0))
        st.metric("Max Dispensing Vials", f"{vials_0} vials")
        st.metric("Test Number (Group)", f"{tests_0}")

    with col3:
        st.markdown("#### 1 Thaw (Double Thaw)")
        vol_1 = total_volume * 2 + 200
        st.metric("Total Volume", f"{vol_1} µL", delta=get_volume_range_label(vol_1))
        st.metric("Max Dispensing Vials", f"{vials_1} vials")
        st.metric("Test Number (Group)", f"{tests_1}")

    with st.expander("View Calculation Details"):
        st.markdown(f"**Total Sample Volume:** {total_volume} µL")
        st.markdown(f"**Maximum:** 800 / {total_volume} = {maximum} (floor method)")
        st.markdown("---")
        st.markdown("**0 Thaw (Single Thaw):**")
        st.markdown(f"- Total Volume = Sample Volume + 200 = {total_volume} + 200 = {vol_0} µL")
        st.markdown(f"- Volume Range: {get_volume_range_label(vol_0)}")
        st.markdown(f"- Dispensing Vials = {vials_0} vials")
        st.markdown(f"- Test Number = {vials_0} × (1000 / ({total_volume} + 200)) = {tests_0}")
        st.markdown("---")
        st.markdown("**1 Thaw (Double Thaw):**")
        st.markdown(f"- Total Volume = Sample Volume × 2 + 200 = {total_volume} × 2 + 200 = {vol_1} µL")
        st.markdown(f"- Volume Range: {get_volume_range_label(vol_1)}")
        st.markdown(f"- Dispensing Vials = {vials_1} vials")
        st.markdown(f"- Test Number = {vials_1} × (1000 / ({total_volume} + 200)) = {tests_1}")

# ============================================================
# UI 渲染函数
# ============================================================

def create_mono_qc_ui(df):
    items = df['ItemName'].dropna().tolist()
    selected_qc = st.selectbox("Select QC Name", items)

    if selected_qc:
        row = df[df['ItemName'] == selected_qc]
        if not row.empty:
            sample_vol = row['Sample Vol (uL)'].values[0]
            st.markdown(f"**Selected Item:** {selected_qc}")
            st.markdown(f"Sample Volume: {sample_vol} µL")

            total_volume = sample_vol
            maximum = calculate_maximum(total_volume)
            vials_0, tests_0 = calculate_vials_and_tests(total_volume, 0)
            vials_1, tests_1 = calculate_vials_and_tests(total_volume, 1)
            display_results(total_volume, maximum, vials_0, tests_0, vials_1, tests_1)
        else:
            st.warning("No data found for the selected item")

def create_multi_qc_ui(df_composite, df_mg6200):
    # 从内置字典构建QC名称列表
    qc_names = list(df_composite.keys())
    selected_qc = st.selectbox("Select QC Name", qc_names)

    if selected_qc:
        items = df_composite[selected_qc]
        st.markdown(f"**{selected_qc} contains:**")
        st.write(f"Total {len(items)} items: {', '.join(items[:10])}" + ("..." if len(items) > 10 else ""))

        # 获取每个项目的加样量
        item_volumes = {}
        for item in items:
            row = df_mg6200[df_mg6200['ItemName'] == item]
            if not row.empty:
                item_volumes[item] = row['Sample Vol (uL)'].values[0]

        selected_items = st.multiselect(
            "Select Items (µL)",
            options=items,
            default=items[:min(3, len(items))]
        )

        if selected_items:
            total_volume = sum(item_volumes.get(item, 0) for item in selected_items)

            st.markdown("**Selected Items and Volumes:**")
            vol_df = pd.DataFrame({
                'Item': selected_items,
                'Volume (µL)': [item_volumes.get(item, 0) for item in selected_items]
            })
            st.dataframe(vol_df, hide_index=True, use_container_width=True)
            st.info(f"**Total Sample Volume: {total_volume} µL**")

            maximum = calculate_maximum(total_volume)
            vials_0, tests_0 = calculate_vials_and_tests(total_volume, 0)
            vials_1, tests_1 = calculate_vials_and_tests(total_volume, 1)
            display_results(total_volume, maximum, vials_0, tests_0, vials_1, tests_1)
        else:
            st.info("Please select at least one item")

# ============================================================
# 主程序
# ============================================================

def main():
    st.set_page_config(
        page_title="QC Volume Calculator",
        page_icon="🧪",
        layout="wide"
    )

    st.title("🧪 QC Volume Calculator")
    st.markdown("### Quality Control Sample Volume Calculator")

    # ---- 侧边栏 ----
    with st.sidebar:
        st.header("Settings")
        mode = st.radio(
            "Select QC Type:",
            ["mono QC", "multi QC"],
            index=0,
            help="mono QC: Uses data from MG6200 sheet; multi QC: Uses data from MG6200复合 sheet"
        )
        st.divider()

        st.subheader("Data Source")
        # 内置数据提示
        st.info("📦 Using built-in data (embedded in the app).")
        # 可选的上传功能（覆盖内置数据）
        uploaded_file = st.file_uploader(
            "Upload Excel File (optional, to override built-in data)",
            type=["xlsx", "xls"],
            help="Upload your own Excel file if you want to use custom data."
        )

        with st.expander("📋 Built-in Data Summary"):
            st.markdown(f"**MG6200:** {len(df_mg6200_builtin)} items")
            st.markdown(f"**MG6200复合:** {len(qc_items)} QC groups")

    # ---- 数据加载 ----
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            if "MG6200" not in xls.sheet_names or "MG6200复合" not in xls.sheet_names:
                st.error("Uploaded file must contain both 'MG6200' and 'MG6200复合' sheets.")
                # 回退到内置数据
                df_mg6200 = df_mg6200_builtin
                df_mg6200_composite = qc_items
                st.warning("Falling back to built-in data.")
            else:
                df_mg6200 = pd.read_excel(uploaded_file, sheet_name="MG6200").dropna(how='all').reset_index(drop=True)
                # 读取复合表，但为了统一接口，我们转换为字典形式
                df_comp_raw = pd.read_excel(uploaded_file, sheet_name="MG6200复合").dropna(how='all').reset_index(drop=True)
                # 提取QC名称和项目列表
                qc_names_from_file = df_comp_raw.iloc[0, 1:14].dropna().tolist()
                qc_items_from_file = {}
                for i, qc_name in enumerate(qc_names_from_file, start=1):
                    items = df_comp_raw.iloc[1:, i].dropna().tolist()
                    qc_items_from_file[qc_name] = items
                df_mg6200_composite = qc_items_from_file
                st.success("✅ Custom file loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}. Using built-in data.")
            df_mg6200 = df_mg6200_builtin
            df_mg6200_composite = qc_items
    else:
        df_mg6200 = df_mg6200_builtin
        df_mg6200_composite = qc_items

    # ---- 主界面 ----
    if mode == "mono QC":
        st.subheader("🔬 Mono QC Mode")
        create_mono_qc_ui(df_mg6200)
    else:
        st.subheader("📊 Multi QC Mode")
        create_multi_qc_ui(df_mg6200_composite, df_mg6200)

if __name__ == "__main__":
    main()