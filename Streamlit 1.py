import streamlit as st  # 👈 FIXED: Added missing framework import
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Credit Risk Dashboard",
    page_icon="🏦",
    layout="wide"
)

# ── Your results (paste your actual el_table here) ───────────
@st.cache_data
def load_data():
    return pd.DataFrame({
        'grade':             ['A','B','C','D','E','F','G'],
        'Avg_PD_Baseline':   [0.03, 0.08, 0.13, 0.18, 0.26, 0.34, 0.36],
        'Avg_PD_Stressed':   [0.06, 0.15, 0.26, 0.37, 0.52, 0.67, 0.72],
        'Avg_LGD':           [0.61, 0.63, 0.64, 0.64, 0.64, 0.64, 0.64],
        'Total_EAD':         [16326725468, 19319821552, 17713544248,
                               8238215499,  3357872687,   990385205,  300301293],
        'Total_EL_Baseline': [291882645,  876209954, 1369856995,
                               933639860,  534865102,  206090777,   67449198],
        'Total_EL_Stressed': [583765290, 1752419908, 2739713991,
                              1867279720, 1069730204,  412181554,  134898396],
    })

df = load_data()
df['EL_Increase_Amt'] = df['Total_EL_Stressed'] - df['Total_EL_Baseline']

# ── Sidebar — Stress Test Controls ───────────────────────────
st.sidebar.header("🎛️ Stress Test Controls")

pd_multiplier = st.sidebar.slider(
    "PD Stress Multiplier",
    min_value=1.0, max_value=5.0, value=2.0, step=0.1,
    help="1.0 = baseline, 2.0 = recession, 3.0 = severe crisis"
)

lgd_shock = st.sidebar.slider(
    "LGD Shock (+%)",
    min_value=0.0, max_value=0.30, value=0.0, step=0.01,
    help="Additional LGD under stress (e.g. 0.10 = +10%)"
)

selected_grades = st.sidebar.multiselect(
    "Filter Grades",
    options=['A','B','C','D','E','F','G'],
    default=['A','B','C','D','E','F','G']
)

# ── Apply interactive stress test ────────────────────────────
df_filtered = df[df['grade'].isin(selected_grades)].copy()
df_filtered['PD_Custom']  = np.clip(df_filtered['Avg_PD_Baseline'] * pd_multiplier, 0, 1)
df_filtered['LGD_Custom'] = np.clip(df_filtered['Avg_LGD'] + lgd_shock, 0, 1)
df_filtered['EL_Custom']  = (df_filtered['PD_Custom'] *
                              df_filtered['LGD_Custom'] *
                              df_filtered['Total_EAD'])

# ── Header ────────────────────────────────────────────────────
st.title("🏦 Credit Risk — Expected Loss Dashboard")
st.caption("Interactive PD × LGD × EAD model with stress testing")

# ── KPI Cards ─────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_ead      = df_filtered['Total_EAD'].sum()
total_baseline = df_filtered['Total_EL_Baseline'].sum()
total_custom   = df_filtered['EL_Custom'].sum()

# Safe percentage calculation to avoid dividing by zero if user clears all grades
el_change_pct = ((total_custom - total_baseline) / total_baseline * 100) if total_baseline > 0 else 0.0

col1.metric("Total EAD",          f"${total_ead/1e9:.2f}B")
col2.metric("Baseline EL",        f"${total_baseline/1e9:.2f}B")
col3.metric("Stressed EL",        f"${total_custom/1e9:.2f}B",
            delta=f" +{el_change_pct:.1f}%", delta_color="inverse")
col4.metric("EL / EAD Ratio",     f"{total_custom/total_ead*100:.2f}%" if total_ead > 0 else "0.00%")

st.divider()

# ── Charts ────────────────────────────────────────────────────
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Expected Loss by Grade")
    fig1 = go.Figure()
    fig1.add_bar(name="Baseline EL", x=df_filtered['grade'],
                 y=df_filtered['Total_EL_Baseline']/1e6,
                 marker_color='steelblue')
    fig1.add_bar(name="Custom Stress EL", x=df_filtered['grade'],
                 y=df_filtered['EL_Custom']/1e6,
                 marker_color='crimson', opacity=0.7)
    fig1.update_layout(barmode='group', yaxis_title="EL ($ Millions)",
                       xaxis_title="Grade", legend_title="Scenario")
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("PD — Baseline vs Stressed")
    fig2 = px.line(
        df_filtered, x='grade',
        y=['Avg_PD_Baseline', 'PD_Custom'],
        labels={'value': 'Probability of Default', 'variable': 'Scenario'},
        markers=True, color_discrete_map={
            'Avg_PD_Baseline': 'steelblue',
            'PD_Custom': 'crimson'
        }
    )
    fig2.update_yaxes(tickformat='.0%')
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("EAD Distribution by Grade")
    fig3 = px.pie(df_filtered, values='Total_EAD', names='grade',
                  color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("EL Increase Under Stress")
    df_filtered['EL_Increase_Custom'] = df_filtered['EL_Custom'] - df_filtered['Total_EL_Baseline']
    fig4 = px.bar(df_filtered, x='grade', y='EL_Increase_Custom',
                  color='EL_Increase_Custom',
                  color_continuous_scale='Reds',
                  labels={'EL_Increase_Custom': 'Additional Loss ($)'})
    st.plotly_chart(fig4, use_container_width=True)

# ── Data Table ────────────────────────────────────────────────
st.subheader("📋 Full Results Table")
display_df = df_filtered[[
    'grade','Avg_PD_Baseline','PD_Custom',
    'LGD_Custom','Total_EAD','Total_EL_Baseline','EL_Custom'
]].copy()

display_df.columns = [
    'Grade','PD Baseline','PD Stressed',
    'LGD','Total EAD ($)','EL Baseline ($)','EL Stressed ($)'
]
st.dataframe(
    display_df.style.format({
        'PD Baseline':    '{:.1%}',
        'PD Stressed':    '{:.1%}',
        'LGD':            '{:.1%}',
        'Total EAD ($)':  '${:,.0f}',
        'EL Baseline ($)':'${:,.0f}',
        'EL Stressed ($)':'${:,.0f}',
    }).background_gradient(subset=['PD Stressed'], cmap='Reds'),
    use_container_width=True
)
