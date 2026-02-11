import streamlit as st
import pandas as pd
import altair as alt
import math

# --- 0. アプリケーション設定 ---
st.set_page_config(
    page_title="Market-Based Target Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. ヘッダー & 概念定義 ---
st.title("⚖️ Market-Based Target Feasibility Simulator")
st.markdown("""
**「気合い」ではなく「市場容量」に基づいた目標設定の妥当性監査**
市場のマクロトレンド（人口・購買力）と競争環境から「理論的な適正目標値」を算出し、
会社提示目標との乖離（Gap）から**「組織の疲弊リスク（Burnout Probability）」**および**「損失コスト（Wasted Cost）」**を定量化します。
""")

# --- 2. 入力セクション (Sidebar) ---
with st.sidebar:
    st.header("1. Macro Environment (市場環境)")
    st.caption("外部要因による不可逆な市場変動")
    pop_change = st.slider("域内人口増減率 (Population) [%]", -10.0, 5.0, -1.0, 0.1) / 100
    income_change = st.slider("購買力/単価増減率 (Income) [%]", -10.0, 10.0, 0.0, 0.1) / 100

    st.header("2. Competitive Context (競争)")
    st.caption("市場内での相対的な力関係")
    comp_options = {
        "独走・シェア拡大 (1.10)": 1.10,
        "好転・撤退減 (1.05)": 1.05,
        "安定・不変 (1.00)": 1.00,
        "悪化・参入増 (0.95)": 0.95,
        "激化・価格競争 (0.90)": 0.90
    }
    selected_comp = st.radio("競争環境の変化", list(comp_options.keys()), index=2)
    k_factor = comp_options[selected_comp]

    st.header("3. Company Target (目標)")
    st.caption("単位: 百万円 (M JPY) で統一")
    last_sales = st.number_input("前年売上実績 (Actual t-1)", value=100.0, step=10.0, format="%.1f")
    target_yoy = st.number_input("会社提示目標 (Target t)", value=105.0, step=10.0, format="%.1f")
    
    st.markdown("---")
    st.header("4. Financial Settings (コスト)")
    sales_team_cost = st.number_input(
        "営業チーム総人件費 (M JPY)", 
        value=50.0, 
        step=5.0,
        help="目標達成のために投下されるリソースの総コスト（給与、販管費等）"
    )

# --- 3. 演算ロジック (Core Logic) ---

# A. 市場トレンド係数 (Market Capacity Index)
mc_index = (1 + pop_change) * (1 + income_change)

# B. 理論適正目標 (Theoretical Target)
model_target = last_sales * mc_index * k_factor

# C. 構造的ドロップガード (Safety Valve: SDG)
lower_bound = last_sales * 0.85
is_market_crash = False
if mc_index < 0.85:
    is_market_crash = True
    if model_target < lower_bound:
        model_target = lower_bound

# D. 乖離診断 (Gap Analysis)
gap_value = target_yoy - model_target
gap_percent = gap_value / model_target if model_target != 0 else 0

# E. 損失コスト試算 (Burnout Cost Logic - Normalized Sigmoid)
def calculate_burnout_ratio(gap_pct):
    if gap_pct <= 0: return 0.0
    x0, k = 0.10, 20
    try:
        raw_val = 1 / (1 + math.exp(-k * (gap_pct - x0)))
        base_val = 1 / (1 + math.exp(-k * (0 - x0)))
    except OverflowError:
        return 1.0
    normalized = (raw_val - base_val) / (1 - base_val)
    return min(max(normalized, 0), 1.0)

burnout_ratio = calculate_burnout_ratio(gap_percent)
wasted_cost = sales_team_cost * burnout_ratio

# --- 4. ダッシュボード表示 (Dashboard) ---

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Market Trend (MC)", f"{mc_index:.3f}", delta=f"{(mc_index-1)*100:.1f}%")

with col2:
    st.metric("Theoretical Target", f"¥{model_target:.1f} M")

with col3:
    if gap_value > 0:
        st.metric("Target Gap (Overload)", f"+¥{gap_value:.1f} M", delta=f"+{gap_percent*100:.1f}%", delta_color="inverse")
    else:
        st.metric("Target Gap (Safe)", f"{gap_value:.1f} M", delta="Achievable", delta_color="normal")

with col4:
    st.metric("Est. Wasted Cost", f"¥{wasted_cost:.1f} M", delta=f"Risk: {burnout_ratio*100:.0f}%", delta_color="inverse")

if is_market_crash:
    st.error("⚠️ **CRASH DETECTED:** 市場環境の急変(-15%超)を検知。下限ガード(85%)が作動しています。")

st.markdown("---")

# --- 5. 可視化 (Visualization) ---
col_main, col_sub = st.columns([2, 1])

with col_main:
    st.subheader("📊 Gap Analysis Chart")
    
    df_chart = pd.DataFrame({
        "Category": ["Actual (t-1)", "Market Logic Target", "Company Target"],
        "Value": [last_sales, model_target, target_yoy],
        "Color": ["#808080", "#2ca02c", "#d62728"]
    })
    
    bars = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('Category', sort=["Actual (t-1)", "Market Logic Target", "Company Target"], title=None),
        y=alt.Y('Value', title="Sales (M JPY)"),
        color=alt.Color('Color', scale=None, legend=None),
        tooltip=['Category', 'Value']
    ).properties(height=400)
    
    rule = alt.Chart(pd.DataFrame({'y': [target_yoy]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')
    
    st.altair_chart(bars + rule, use_container_width=True)

with col_sub:
    st.subheader("📝 Audit Report")
    
    if gap_percent > 0.15:
        st.error("判定：【Type C】Structural Failure")
        st.markdown(f"""
        **乖離率: +{gap_percent*100:.1f}% (Critical)**
        
        目標は市場構造から完全に逸脱しています。組織の**疲弊リスクは{burnout_ratio*100:.0f}%**に達しており、投入リソースの多くが回収不能になる可能性が高いです。
        
        **推奨アクション:**
        * 目標の強制下方修正
        * 不採算エリアからの戦略的撤退
        """)
    elif gap_percent > 0.05:
        st.warning("判定：【Type B】Yellow Signal")
        st.markdown(f"""
        **乖離率: +{gap_percent*100:.1f}% (Caution)**
        
        市場ポテンシャルに対して目標が過大です。現場の「努力」でカバーできる限界ラインに近づいています。
        
        **分析結果:**
        * 疲弊リスク（{burnout_ratio*100:.0f}%）が上昇傾向にあります。
        * 離職やモチベーション低下による「組織負債」が蓄積し始めている可能性があります。
        """)
    else:
        st.success("判定：【Type A】Feasible")
        st.markdown(f"""
        **乖離率: {gap_percent*100:.1f}% (Safe)**
        
        目標は市場環境および競争力と整合しています。
        
        **分析結果:**
        * 持続可能な成長が期待できる健全な計画です。
        * 投資対効果（ROI）が最大化される、論理的に「強い」目標設定と診断します。
        """)

st.markdown("---")
st.caption("© 2026 Strategic Target Optimization Engine | Market Capacity Logic")