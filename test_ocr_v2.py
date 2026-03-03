"""
截图识别数字 - 简化版本
"""
import streamlit as st
import re
import base64

st.set_page_config(page_title="截图识别", page_icon="📷", layout="wide")

st.title("📷 截图识别数字")

# 侧边栏设置
with st.sidebar:
    st.markdown("## ⚙️ 设置")
    api_key = st.text_input("OpenAI API Key", type="password", 
                           help="用于GPT-4o识别图片中的数字")
    if api_key:
        st.success("✅ 已设置")

# 主区域
st.markdown("### 上传或拖拽截图")
uploaded = st.file_uploader("", type=['png', 'jpg', 'jpeg'], 
                            help="支持PNG、JPG格式",
                            label_visibility="collapsed")

if uploaded:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(uploaded, caption="截图预览", use_container_width=True)
    
    with col2:
        if not api_key:
            st.warning("请在左侧边栏输入 OpenAI API Key")
        else:
            if st.button("🔍 识别数字", type="primary", use_container_width=True):
                with st.spinner("正在识别..."):
                    try:
                        import openai
                        
                        # 编码图片
                        img_bytes = uploaded.getvalue()
                        b64_img = base64.b64encode(img_bytes).decode('utf-8')
                        
                        # 调用API
                        client = openai.OpenAI(api_key=api_key)
                        resp = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "识别图片中的所有数字。只返回数字，每行一个，不要其他文字。"},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                                ]
                            }],
                            max_tokens=2000
                        )
                        
                        result = resp.choices[0].message.content
                        st.session_state.ocr_result = result
                        
                    except Exception as e:
                        st.error(f"识别失败: {e}")

# 显示识别结果
if "ocr_result" in st.session_state and st.session_state.ocr_result:
    st.markdown("---")
    st.markdown("### 📊 识别结果")
    
    result = st.session_state.ocr_result
    
    # 可编辑的结果
    edited = st.text_area("识别到的数字（可编辑）", result, height=150)
    
    # 提取数字
    nums = []
    for line in edited.split('\n'):
        clean = re.sub(r'[^\d.\-,]', '', line.replace(',', ''))
        if clean and re.match(r'^-?\d+\.?\d*$', clean):
            nums.append(float(clean))
    
    if nums:
        import numpy as np
        
        st.success(f"""**共 {len(nums)} 个数字**
- ➕ 求和: **{sum(nums):,.2f}**
- 📊 均值: **{sum(nums)/len(nums):,.2f}**
- ⬆️ 最大: **{max(nums):,.2f}**
- ⬇️ 最小: **{min(nums):,.2f}**
- 📍 中位数: **{float(np.median(nums)):,.2f}**""")
        
        # 存储到组A或组B
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ 存入组A", use_container_width=True):
                st.session_state.group_a = nums
                st.rerun()
        with c2:
            if st.button("➕ 存入组B", use_container_width=True):
                st.session_state.group_b = nums
                st.rerun()

# 两组对比
st.markdown("---")
st.markdown("### 📊 两组对比")

col1, col2 = st.columns(2)

with col1:
    if "group_a" in st.session_state and st.session_state.group_a:
        nums_a = st.session_state.group_a
        st.success(f"""**🟢 组A ({len(nums_a)}个)**
求和: {sum(nums_a):,.2f}
均值: {sum(nums_a)/len(nums_a):,.2f}""")
        if st.button("清除组A"):
            del st.session_state.group_a
            st.rerun()
    else:
        st.info("🟢 组A: 未设置")

with col2:
    if "group_b" in st.session_state and st.session_state.group_b:
        nums_b = st.session_state.group_b
        st.warning(f"""**🟠 组B ({len(nums_b)}个)**
求和: {sum(nums_b):,.2f}
均值: {sum(nums_b)/len(nums_b):,.2f}""")
        if st.button("清除组B"):
            del st.session_state.group_b
            st.rerun()
    else:
        st.info("🟠 组B: 未设置")

# 对比分析
if "group_a" in st.session_state and "group_b" in st.session_state:
    if st.session_state.group_a and st.session_state.group_b:
        sum_a = sum(st.session_state.group_a)
        sum_b = sum(st.session_state.group_b)
        diff = sum_b - sum_a
        pct = (diff / abs(sum_a) * 100) if sum_a != 0 else 0
        
        st.markdown("### 📈 对比结果 (B vs A)")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("求和差值", f"{diff:+,.2f}")
        with m2:
            st.metric("变化率", f"{pct:+.2f}%")
        with m3:
            direction = "📈 上涨" if pct >= 0 else "📉 下跌"
            st.metric("涨跌", direction)
