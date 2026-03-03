"""
截图识别 - 免费OCR方案（使用EasyOCR）
"""
import streamlit as st
import streamlit.components.v1 as components
import re
import base64
from io import BytesIO

st.set_page_config(page_title="免费截图识别", page_icon="📷", layout="wide")

st.title("📷 免费截图识别数字")
st.caption("使用 EasyOCR 本地识别，无需API Key")

# 检查EasyOCR是否安装
try:
    import easyocr
    ocr_available = True
except ImportError:
    ocr_available = False
    st.error("⚠️ EasyOCR 未安装，请运行: `pip install easyocr`")

# 上传或粘贴截图
st.markdown("### 📋 上传截图")

uploaded = st.file_uploader("拖拽或点击上传截图", type=['png', 'jpg', 'jpeg'])

if uploaded and ocr_available:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(uploaded, caption="截图预览", use_container_width=True)
    
    with col2:
        if st.button("🔍 识别数字", type="primary", use_container_width=True):
            with st.spinner("正在加载OCR模型并识别（首次较慢）..."):
                try:
                    from PIL import Image
                    import numpy as np
                    
                    # 读取图片
                    img = Image.open(uploaded)
                    img_array = np.array(img)
                    
                    # 创建OCR reader（只识别数字和英文，更快）
                    reader = easyocr.Reader(['en'], gpu=False)
                    
                    # 识别
                    results = reader.readtext(img_array)
                    
                    # 提取数字
                    all_nums = []
                    raw_text = []
                    
                    for (bbox, text, prob) in results:
                        raw_text.append(text)
                        # 提取数字
                        nums = re.findall(r'-?[\d,]+\.?\d*', text)
                        for n in nums:
                            try:
                                val = float(n.replace(',', ''))
                                if val != 0:
                                    all_nums.append(val)
                            except:
                                pass
                    
                    st.session_state.ocr_raw = '\n'.join(raw_text)
                    st.session_state.ocr_nums = all_nums
                    st.success(f"✅ 识别完成！找到 {len(all_nums)} 个数字")
                    
                except Exception as e:
                    st.error(f"识别失败: {e}")

# 显示结果
if "ocr_nums" in st.session_state and st.session_state.ocr_nums:
    st.markdown("---")
    st.markdown("### 📊 识别结果")
    
    # 显示原始文本
    with st.expander("原始识别文本"):
        st.text(st.session_state.ocr_raw)
    
    nums = st.session_state.ocr_nums
    
    # 可编辑的数字列表
    edited_nums = st.text_area("识别到的数字（可编辑）", 
                               '\n'.join([str(n) for n in nums]), 
                               height=150)
    
    # 重新解析编辑后的数字
    final_nums = []
    for line in edited_nums.split('\n'):
        clean = re.sub(r'[^\d.\-]', '', line)
        if clean and re.match(r'^-?\d+\.?\d*$', clean):
            final_nums.append(float(clean))
    
    if final_nums:
        import numpy as np
        
        st.success(f"""**共 {len(final_nums)} 个数字**
- ➕ 求和: **{sum(final_nums):,.2f}**
- 📊 均值: **{sum(final_nums)/len(final_nums):,.2f}**
- ⬆️ 最大: **{max(final_nums):,.2f}**
- ⬇️ 最小: **{min(final_nums):,.2f}**
- 📍 中位数: **{float(np.median(final_nums)):,.2f}**""")

# 清除
if st.button("🗑️ 清除结果"):
    if "ocr_nums" in st.session_state:
        del st.session_state.ocr_nums
    if "ocr_raw" in st.session_state:
        del st.session_state.ocr_raw
    st.rerun()

st.markdown("---")
st.caption("💡 提示：EasyOCR首次运行会下载模型，可能需要几分钟")
