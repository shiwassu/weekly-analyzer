"""
截图识别 - 支持Ctrl+V直接粘贴
"""
import streamlit as st
import streamlit.components.v1 as components
import re
import base64

st.set_page_config(page_title="截图识别", page_icon="📷", layout="wide")

st.title("📷 截图识别数字")

# 侧边栏设置
with st.sidebar:
    st.markdown("## ⚙️ 设置")
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        st.success("✅ 已设置")

# 粘贴区域 - 全屏监听Ctrl+V
st.markdown("### 📋 Ctrl+V 粘贴截图")

# 自定义HTML组件 - 粘贴后自动提交base64到隐藏input
paste_component = """
<style>
#paste-zone {
    border: 3px dashed #667eea;
    border-radius: 12px;
    padding: 40px 20px;
    text-align: center;
    background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
    cursor: pointer;
    min-height: 200px;
    transition: all 0.3s;
}
#paste-zone:focus {
    border-color: #4CAF50;
    background: linear-gradient(135deg, #e8ffe8 0%, #c8ffc8 100%);
    outline: none;
}
#paste-zone.has-image {
    border-color: #4CAF50;
    border-style: solid;
}
#paste-zone img {
    max-width: 100%;
    max-height: 350px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.hint { color: #666; font-size: 16px; margin-bottom: 15px; }
.success-msg { color: #4CAF50; font-weight: bold; margin-top: 15px; }
</style>

<div id="paste-zone" tabindex="0" autofocus>
    <p class="hint">📋 <b>点击此处</b>，然后按 <b>Ctrl+V</b> 粘贴截图</p>
    <p class="hint" style="font-size:13px;color:#999">（截图后会自动复制到剪贴板）</p>
    <img id="preview" style="display:none">
    <p id="success-msg" class="success-msg" style="display:none">✅ 已粘贴！点击下方按钮识别</p>
</div>

<input type="hidden" id="image-data">

<script>
// 自动聚焦
document.getElementById('paste-zone').focus();

// 监听整个文档的粘贴事件
document.addEventListener('paste', function(e) {
    var items = e.clipboardData.items;
    for (var i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            var blob = items[i].getAsFile();
            var reader = new FileReader();
            reader.onload = function(event) {
                var base64 = event.target.result;
                
                // 显示预览
                var img = document.getElementById('preview');
                img.src = base64;
                img.style.display = 'block';
                document.getElementById('success-msg').style.display = 'block';
                document.getElementById('paste-zone').classList.add('has-image');
                document.querySelector('.hint').style.display = 'none';
                
                // 存储数据
                document.getElementById('image-data').value = base64;
                
                // 发送到Streamlit (通过URL参数)
                var params = new URLSearchParams(window.parent.location.search);
                
                // 使用localStorage临时存储
                localStorage.setItem('pasted_image', base64);
                
                // 通知父窗口
                window.parent.postMessage({type: 'paste_image', data: base64}, '*');
            };
            reader.readAsDataURL(blob);
            e.preventDefault();
            break;
        }
    }
});

// 检查localStorage中是否有已粘贴的图片
var saved = localStorage.getItem('pasted_image');
if (saved && saved.startsWith('data:image')) {
    document.getElementById('preview').src = saved;
    document.getElementById('preview').style.display = 'block';
    document.getElementById('success-msg').style.display = 'block';
    document.getElementById('paste-zone').classList.add('has-image');
    document.querySelector('.hint').style.display = 'none';
    document.getElementById('image-data').value = saved;
}
</script>
"""

components.html(paste_component, height=450)

# 手动输入base64（作为备选方案）
with st.expander("📝 或手动粘贴图片数据", expanded=False):
    st.markdown("如果上方粘贴不生效，请：")
    st.markdown("1. 在上方粘贴截图后，按F12打开控制台")
    st.markdown("2. 输入: `localStorage.getItem('pasted_image')`")
    st.markdown("3. 复制结果粘贴到下方")
    manual_base64 = st.text_area("Base64图片数据", height=100, key="manual_b64")

# 识别按钮
st.markdown("---")

if st.button("🔍 识别截图中的数字", type="primary", use_container_width=True):
    # 尝试获取图片数据
    img_data = None
    
    # 优先使用手动输入的
    if manual_base64 and manual_base64.startswith('data:image'):
        img_data = manual_base64
    
    if img_data and api_key:
        with st.spinner("正在识别..."):
            try:
                import openai
                
                # 提取base64部分
                if ',' in img_data:
                    b64_part = img_data.split(',')[1]
                else:
                    b64_part = img_data
                
                client = openai.OpenAI(api_key=api_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "识别图片中的所有数字。只返回数字，每行一个数字，不要任何其他文字。如果有百分比，去掉%符号只保留数字。"},
                            {"type": "image_url", "image_url": {"url": img_data}}
                        ]
                    }],
                    max_tokens=2000
                )
                
                result = resp.choices[0].message.content
                st.session_state.ocr_result = result
                st.success("✅ 识别成功！")
                
            except Exception as e:
                st.error(f"识别失败: {e}")
    elif not api_key:
        st.warning("请先在左侧边栏输入 OpenAI API Key")
    else:
        st.warning("请先粘贴截图，或手动输入图片数据")

# 显示识别结果
if "ocr_result" in st.session_state and st.session_state.ocr_result:
    st.markdown("### 📊 识别结果")
    
    edited = st.text_area("识别到的数字（可编辑）", st.session_state.ocr_result, height=150)
    
    # 提取数字
    nums = []
    for line in edited.split('\n'):
        clean = re.sub(r'[^\d.\-]', '', line)
        if clean and re.match(r'^-?\d+\.?\d*$', clean):
            nums.append(float(clean))
    
    if nums:
        import numpy as np
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"""**共 {len(nums)} 个数字**
- ➕ 求和: **{sum(nums):,.2f}**
- 📊 均值: **{sum(nums)/len(nums):,.2f}**""")
        with col2:
            st.info(f"""
- ⬆️ 最大: **{max(nums):,.2f}**
- ⬇️ 最小: **{min(nums):,.2f}**
- 📍 中位: **{float(np.median(nums)):,.2f}**""")

# 清除按钮
if st.button("🗑️ 清除"):
    if "ocr_result" in st.session_state:
        del st.session_state.ocr_result
    st.rerun()
