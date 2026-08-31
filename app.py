import streamlit as st
import pandas as pd
import numpy as np
import io

# ============================================================
# 内置数据 - 使用 CSV 字符串确保长度一致
# ============================================================

MG6200_CSV = """ItemName,Sample Vol (uL)
HIV,100
IL-10,100
TNF-a,100
TSH,100
ALD,99
PTH,99
Renin,99
S100,99
CT,90
ACTH,75
hs-cTnI,75
IL-1β,75
AF3,50
AMH,50
AngI,50
AngII,50
Anti-TSHR,50
BNP,50
CG,50
CIV,50
Cortisol,50
E2,50
E3,50
FT3,50
HA,50
HBeAb,50
HBeAb quant,50
HBsAb,50
HBsAg,50
HBcAb,50
HBcAb quant,50
hs-cTnT,50
IAA,50
IL-8,50
LN,50
NT-proBNP,50
PIVKA II,50
PⅢP N-P,50
proGRP,50
T,50
T3,50
Tg,50
TMAb,50
TP,50
CK-MB,50
Anti-HCV,50
PIIIPN-P,50
G17,49
LH,49
rT3,40
CA72-4,29
DHEA-S,25
P,25
TG-Ab,25
C-P,20
FPSA,20
HBP,20
IL-6,20
INS,20
NSE,20
PCT,20
PLGF,20
PRL,20
ST2,20
TAT,20
tPSA,20
CA 125,19
CYFRA 21-1,19
FSH,19
GH,19
PGI,19
PGII,19
25-OH-VD,15
FT4,15
HBeAg,15
HBeAg quant,15
HE4,15
Osteocalcin,15
TPO-Ab,15
VB12,15
CA242,14
SCC,14
CA 15-3,11
CA 19-9,11
lgE,11
AFP,10
CA50,10
CEA,10
CMV IgG,10
CMV IgM,10
CRP,10
D-Dimer,10
FABP,10
FDP,10
FER,10
Free-β-HCG,10
HbA1c,10
HCG+β,10
HSV-II IgG,10
HSV-II IgM,10
HSV-I IgG,10
HSV-I IgM,10
IGF-1,10
IGFBP-3,10
IL-2R,10
Lp-PLA2,10
Myo,10
NGAL,10
PAPP-A,10
PIC,10
Rubella IgG,10
Rubella IgM,10
SAA,10
SHBG,10
T4,10
TM,10
Toxo IgG,10
Toxo IgM,10
tPAI-C,10
β-MG,10"""

df_mg6200_builtin = pd.read_csv(io.StringIO(MG6200_CSV))

# ---- MG6200复合 数据（QC 分组） ----
qc_items = {
    "Thyroid function series Multi Control 1": ["FT3", "FT4", "T3", "T4", "TSH"],
    "Thyroid function series Multi Control 2": ["FT3", "FT4", "T3", "T4", "TSH", "TG-Ab", "TPO-Ab", "Tg", "Anti-TSHR", "rT3", "TMAb"],
    "Hormone series Multi Control 1": ["FSH", "PRL", "LH", "HCG+β", "T", "P", "E2", "E3"],
    "Hormone series Multi Control 2": ["AMH", "SHBG", "GH", "DHEA-S"],
    "Infectious disease Multi Control 1": ["HBsAg", "HBeAg quant", "Anti-HCV", "TP", "HIV"],
    "Infectious disease Multi Control 2": ["HBsAb", "HBeAb quant", "HBeAb quant", "HBcAb quant", "HIV"],
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
# 核心计算函数（修正后）
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

    # Test Number 直接等于瓶数（0 thaw）或 2倍瓶数（1 thaw）
    if thaw_multiplier == 0:
        tests = vials
    else:
        tests = 2 * vials

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
        st.metric("Maximum Test Number", f"{maximum}")

    with col2:
        st.markdown("#### 0 Thaw (Single Thaw)")
        vol_0 = total_volume + 200
        st.metric("Minimum Volume/Vial", f"{vol_0} µL", delta=get_volume_range_label(vol_0))
        st.metric("Max Dispensing Vials", f"{vials_0} vials")
        st.metric("Test Number (Group)", f"{tests_0}")

    with col3:
        st.markdown("#### 1 Thaw (Double Thaw)")
        vol_1 = total_volume * 2 + 200
        st.metric("Minimum Volume/Vial", f"{vol_1} µL", delta=get_volume_range_label(vol_1))
        st.metric("Max Dispensing Vials", f"{vials_1} vials")
        st.metric("Test Number (Group)", f"{tests_1}")

    with st.expander("View Calculation Details"):
        st.markdown(f"**Total Sample Volume:** {total_volume} µL")
        st.markdown(f"**Maximum Test Number:** 800 / {total_volume} = {maximum} (floor method)")
        st.markdown("---")
        st.markdown("**0 Thaw (Single Thaw):**")
        st.markdown(f"- Minimum Volume/Vial = Sample Volume + 200 = {total_volume} + 200 = {vol_0} µL")
        st.markdown(f"- Volume Range: {get_volume_range_label(vol_0)} → Max Dispensing Vials = {vials_0}")
        st.markdown(f"- Test Number = Max Dispensing Vials = {tests_0}")
        st.markdown("---")
        st.markdown("**1 Thaw (Double Thaw):**")
        st.markdown(f"- Minimum Volume/Vial = Sample Volume × 2 + 200 = {total_volume} × 2 + 200 = {vol_1} µL")
        st.markdown(f"- Volume Range: {get_volume_range_label(vol_1)} → Max Dispensing Vials = {vials_1}")
        st.markdown(f"- Test Number = 2 × Max Dispensing Vials = {tests_1}")

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
    qc_names = list(df_composite.keys())
    selected_qc = st.selectbox("Select QC Name", qc_names)

    if selected_qc:
        items = df_composite[selected_qc]
        st.markdown(f"**{selected_qc} contains:**")
        st.write(f"Total {len(items)} items: {', '.join(items[:10])}" + ("..." if len(items) > 10 else ""))

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

    with st.sidebar:
        st.header("Settings")
        mode = st.radio(
            "Select QC Type:",
            ["mono QC", "multi QC"],
            index=0
        )
        st.divider()

        st.subheader("Data Source")
        st.info("📦 Using built-in data (embedded in the app).")
        uploaded_file = st.file_uploader(
            "Upload Excel File (optional, to override built-in data)",
            type=["xlsx", "xls"]
        )

        with st.expander("📋 Built-in Data Summary"):
            st.markdown(f"**MG6200:** {len(df_mg6200_builtin)} items")
            st.markdown(f"**MG6200复合:** {len(qc_items)} QC groups")

    # 数据加载（优先使用上传的文件）
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            if "MG6200" not in xls.sheet_names or "MG6200复合" not in xls.sheet_names:
                st.error("Uploaded file must contain both 'MG6200' and 'MG6200复合' sheets.")
                df_mg6200 = df_mg6200_builtin
                df_mg6200_composite = qc_items
                st.warning("Falling back to built-in data.")
            else:
                df_mg6200 = pd.read_excel(uploaded_file, sheet_name="MG6200").dropna(how='all').reset_index(drop=True)
                df_comp_raw = pd.read_excel(uploaded_file, sheet_name="MG6200复合").dropna(how='all').reset_index(drop=True)
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

    if mode == "mono QC":
        st.subheader("🔬 Mono QC Mode")
        create_mono_qc_ui(df_mg6200)
    else:
        st.subheader("📊 Multi QC Mode")
        create_multi_qc_ui(df_mg6200_composite, df_mg6200)

if __name__ == "__main__":
    main()
