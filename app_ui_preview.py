"""
UI 预览文件 - 科技感 + 毛玻璃效果
仅用于设计确认，不影响主应用
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="周均数据对比分析器",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== 全局样式注入 ==============
st.markdown("""
<style>
/* ---- 全局背景 ---- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 40%, #e8f5e9 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] {
    background: rgba(240, 244, 255, 0.6);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(99, 140, 255, 0.2);
}

/* ---- 侧边栏毛玻璃 ---- */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.55) !important;
    backdrop-filter: blur(18px) !important;
    border-right: 1px solid rgba(120, 160, 255, 0.25) !important;
    box-shadow: 4px 0 24px rgba(80, 120, 220, 0.08) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #2a4bbd;
}

/* ---- 主内容区域 ---- */
[data-testid="stMainBlockContainer"] {
    padding-top: 1.5rem;
}

/* ---- 毛玻璃卡片基础类 ---- */
.glass-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.85);
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0;
    box-shadow: 0 8px 32px rgba(60, 100, 200, 0.08), 0 1px 0 rgba(255,255,255,0.9) inset;
}

/* ---- 主标题 ---- */
.main-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #3a7bd5, #00d2ff, #3a7bd5);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shine 4s linear infinite;
    letter-spacing: -0.5px;
}
@keyframes shine {
    to { background-position: 200% center; }
}
.main-header .subtitle {
    color: #6b7db3;
    font-size: 0.95rem;
    margin-top: -8px;
    letter-spacing: 2px;
}
.header-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, #3a7bd5 30%, #00d2ff 70%, transparent);
    margin: 12px auto;
    width: 60%;
    border-radius: 2px;
}

/* ---- 分区标题 ---- */
.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #2a4bbd;
    padding: 8px 16px;
    background: rgba(58, 123, 213, 0.07);
    border-left: 3px solid #3a7bd5;
    border-radius: 0 8px 8px 0;
    margin: 16px 0 10px 0;
    letter-spacing: 0.3px;
}

/* ---- 指标卡片 ---- */
.metric-glass {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 14px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(60,100,200,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.metric-glass::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3a7bd5, #00d2ff);
    border-radius: 14px 14px 0 0;
}
.metric-glass:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(60,100,200,0.14);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #2a4bbd;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.8rem;
    color: #7a8db3;
    margin-top: 4px;
    font-weight: 500;
    letter-spacing: 0.5px;
}
.metric-delta-up { color: #00b87c; font-size: 0.85rem; font-weight: 600; }
.metric-delta-down { color: #f45b69; font-size: 0.85rem; font-weight: 600; }

/* ---- 状态标签 ---- */
.tag-normal {
    display: inline-block;
    background: linear-gradient(135deg, #00c6a2, #00e0b6);
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.tag-abnormal {
    display: inline-block;
    background: linear-gradient(135deg, #f45b69, #ff8b5e);
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ---- Expander 样式 ---- */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.6) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(200, 215, 255, 0.5) !important;
    border-radius: 12px !important;
    margin: 8px 0 !important;
    box-shadow: 0 4px 16px rgba(60, 100, 200, 0.06) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #2a4bbd !important;
}

/* ---- 按钮 ---- */
.stButton > button {
    background: linear-gradient(135deg, #3a7bd5 0%, #00a8cc 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 14px rgba(58, 123, 213, 0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(58, 123, 213, 0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.7) !important;
    color: #3a7bd5 !important;
    border: 1px solid rgba(58,123,213,0.3) !important;
    box-shadow: 0 2px 8px rgba(58, 123, 213, 0.1) !important;
}

/* ---- 数据表格 ---- */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(200, 215, 255, 0.4) !important;
    box-shadow: 0 4px 16px rgba(60, 100, 200, 0.07) !important;
}

/* ---- 输入框 ---- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(120, 160, 255, 0.3) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 3px rgba(58, 123, 213, 0.15) !important;
}

/* ---- Metric 组件 ---- */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.65) !important;
    border: 1px solid rgba(200,215,255,0.5) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 16px rgba(60,100,200,0.06) !important;
}
[data-testid="stMetricValue"] {
    color: #2a4bbd !important;
}

/* ---- Tab ---- */
[data-testid="stTabs"] [data-testid="stTab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
}

/* ---- Divider ---- */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(58,123,213,0.3), transparent) !important;
    margin: 1rem 0 !important;
}

/* ---- Radio & Checkbox ---- */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
    color: #3a4d7a !important;
    font-weight: 500 !important;
}

/* ---- Spinner ---- */
[data-testid="stSpinner"] {
    color: #3a7bd5 !important;
}

/* ---- 科技感装饰点 ---- */
.tech-dots {
    display: flex;
    gap: 5px;
    align-items: center;
    margin-bottom: 4px;
}
.tech-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #3a7bd5;
    opacity: 0.4;
}
.tech-dot:first-child { opacity: 1; background: #00d2ff; }
.tech-dot:nth-child(2) { opacity: 0.7; }
</style>
""", unsafe_allow_html=True)


# ============== 主标题 ==============
st.markdown("""
<div class="main-header">
    <div class="tech-dots" style="justify-content:center">
        <div class="tech-dot"></div><div class="tech-dot"></div><div class="tech-dot"></div>
    </div>
    <div style="display:flex;align-items:center;justify-content:center;gap:14px">
        <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="44" height="44" rx="12" fill="url(#grad1)"/>
            <rect x="8" y="28" width="6" height="10" rx="2" fill="white" fill-opacity="0.95"/>
            <rect x="17" y="20" width="6" height="18" rx="2" fill="white" fill-opacity="0.95"/>
            <rect x="26" y="14" width="6" height="24" rx="2" fill="white" fill-opacity="0.95"/>
            <polyline points="11,27 20,19 29,13 36,9" stroke="white" stroke-width="2" stroke-opacity="0.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <circle cx="36" cy="9" r="2.5" fill="white" fill-opacity="0.9"/>
            <defs>
                <linearGradient id="grad1" x1="0" y1="0" x2="44" y2="44" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stop-color="#3a7bd5"/>
                    <stop offset="100%" stop-color="#00d2ff"/>
                </linearGradient>
            </defs>
        </svg>
        <h1 style="margin:0">周均数据对比分析器</h1>
    </div>
    <div class="header-line"></div>
    <p class="subtitle">WEEKLY DATA ANALYSIS PLATFORM</p>
</div>
""", unsafe_allow_html=True)


# ============== 侧边栏 ==============
with st.sidebar:
    st.markdown("## ⚙️ 配置设置")
    st.markdown("---")

    st.markdown("### 🤖 AI分析设置")
    use_ai = st.checkbox("启用AI智能分析", value=True)
    if use_ai:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

    st.markdown("---")
    st.markdown("### 📏 默认异常阈值")
    use_default = st.checkbox("启用默认阈值", value=True)
    if use_default:
        threshold = st.slider("阈值 (%)", 5, 50, 15, 1)

    st.markdown("---")
    st.markdown("## 🧮 快速计算")
    st.caption("从表格复制数据粘贴到这里")
    input_a = st.text_area("🟢 组A数据", height=80, placeholder="粘贴数据...")
    input_b = st.text_area("🟠 组B数据", height=80, placeholder="粘贴数据...")
    if st.button("计算对比", use_container_width=True):
        st.info("对比结果将显示在这里")


# ============== 数据来源区 ==============
st.markdown('<div class="section-title">📁 数据来源</div>', unsafe_allow_html=True)

with st.expander("🔗 报表系统快捷入口", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🚀 打开 Infoc 报表系统", "http://base.cmcm.com:8080/", use_container_width=True)
    with c2:
        st.text_input("自定义报表地址", placeholder="输入其他报表系统URL")

with st.expander("🧮 快速计算工具（双组对比）", expanded=False):
    st.markdown("**从报表复制数据，粘贴到下方进行快速计算和对比**")
    ca, cb = st.columns(2)
    with ca:
        st.text_area("🟢 组A（粘贴数字，每行一个）", height=120, key="qa")
    with cb:
        st.text_area("🟠 组B（粘贴数字，每行一个）", height=120, key="qb")
    st.button("计算对比", key="calc_btn")

with st.expander("📷 截图识别数字", expanded=False):
    st.link_button("🚀 打开截图识别工具（新窗口）", "https://shiwassu-tomato-ocr.hf.space", use_container_width=True)
    st.components.v1.iframe("https://shiwassu-tomato-ocr.hf.space", height=600, scrolling=True)

# ---- 数据导入 ----
st.markdown('<div class="section-title">📥 导入数据</div>', unsafe_allow_html=True)
data_source = st.radio("选择数据导入方式", ["上传文件", "粘贴数据"], horizontal=True)
uploaded = st.file_uploader("上传 CSV / Excel 文件", type=['csv', 'xlsx', 'xls']) if data_source == "上传文件" else None

st.markdown("---")

# ============== 演示数据（UI效果展示）==============
st.markdown('<div class="section-title">📊 数据处理模式</div>', unsafe_allow_html=True)
st.radio("选择数据处理方式", [
    "模式1: 直接对比（已有周均数据）",
    "模式2: 日期范围计算（按日期筛选计算均值）",
    "模式3: 任意两天对比"
], index=0)

st.markdown("---")

# ============== 示例结果区 ==============
st.markdown('<div class="section-title">📊 分析结果（示例）</div>', unsafe_allow_html=True)

# 指标卡片
st.markdown("""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0">
    <div class="metric-glass">
        <div class="metric-value">12</div>
        <div class="metric-label">总指标数</div>
    </div>
    <div class="metric-glass">
        <div class="metric-value" style="color:#00b87c">8</div>
        <div class="metric-label">正常指标</div>
    </div>
    <div class="metric-glass">
        <div class="metric-value" style="color:#f45b69">4</div>
        <div class="metric-label">异常指标</div>
    </div>
    <div class="metric-glass">
        <div class="metric-value">33%</div>
        <div class="metric-label">异常比例</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Streamlit 原生 metric
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("求和差值", "+1,234", "+5.6%")
with m2:
    st.metric("均值差值", "+102.3", "+3.2%")
with m3:
    st.metric("涨跌比", "📈 上涨", "+5.60%")

st.markdown("---")

# 示例表格
st.markdown('<div class="section-title">📋 对比明细</div>', unsafe_allow_html=True)
demo_df = pd.DataFrame({
    "指标": ["DAU", "MAU", "留存率", "付费率", "ARPU", "LTV"],
    "上周均值": [120000, 850000, "32.1%", "5.2%", 18.5, 220.0],
    "本周均值": [128000, 890000, "34.5%", "4.8%", 19.2, 235.0],
    "涨跌率": ["+6.67%", "+4.71%", "+7.48%", "-7.69%", "+3.78%", "+6.82%"],
    "状态": ["正常", "正常", "正常", "<span class='tag-abnormal'>异常</span>",
             "正常", "正常"],
})
st.dataframe(
    demo_df.drop(columns=["状态"]),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# 示例图表
st.markdown('<div class="section-title">📈 数据可视化</div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["对比柱状图", "涨跌率分布"])

with tab1:
    metrics = ["DAU", "MAU", "ARPU", "LTV"]
    prev_vals = [120000, 850000, 18.5, 220.0]
    curr_vals = [128000, 890000, 19.2, 235.0]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="上周均值", x=metrics, y=prev_vals,
                         marker_color="rgba(58,123,213,0.7)",
                         marker_line_color="rgba(58,123,213,1)", marker_line_width=1))
    fig.add_trace(go.Bar(name="本周均值", x=metrics, y=curr_vals,
                         marker_color="rgba(0,210,255,0.7)",
                         marker_line_color="rgba(0,210,255,1)", marker_line_width=1))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.4)",
        font=dict(color="#3a4d7a", family="sans-serif"),
        legend=dict(bgcolor="rgba(255,255,255,0.6)", bordercolor="rgba(120,160,255,0.3)", borderwidth=1),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(gridcolor="rgba(120,160,255,0.1)"),
        yaxis=dict(gridcolor="rgba(120,160,255,0.1)"),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    rates = [6.67, 4.71, 7.48, -7.69, 3.78, 6.82]
    names = ["DAU", "MAU", "留存率", "付费率", "ARPU", "LTV"]
    colors = ["rgba(0,184,124,0.75)" if r >= 0 else "rgba(244,91,105,0.75)" for r in rates]
    fig2 = go.Figure(go.Bar(x=names, y=rates, marker_color=colors,
                            marker_line_width=0))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.4)",
        font=dict(color="#3a4d7a"),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(gridcolor="rgba(120,160,255,0.1)", ticksuffix="%"),
        xaxis=dict(gridcolor="rgba(120,160,255,0.1)"),
    )
    fig2.add_hline(y=0, line_color="rgba(58,123,213,0.4)", line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown('<div class="section-title">🤖 智能分析报告</div>', unsafe_allow_html=True)
st.button("📝 生成分析报告", use_container_width=True)

st.markdown("---")
st.markdown('<div class="section-title">📥 导出报告</div>', unsafe_allow_html=True)
e1, e2, e3 = st.columns(3)
with e1:
    st.button("📄 导出 Word 报告", use_container_width=True)
with e2:
    st.button("📊 导出 Excel 数据", use_container_width=True)
with e3:
    st.button("📋 复制分析摘要", use_container_width=True)
