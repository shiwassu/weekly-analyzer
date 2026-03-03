"""
截图识别数字测试 - 本地测试版本
"""
import streamlit as st
import streamlit.components.v1 as components
import re
import base64
from io import BytesIO

st.set_page_config(page_title="截图识别测试", page_icon="📷", layout="wide")

st.title("📷 截图识别数字")

# 侧边栏 - API Key设置
with st.sidebar:
    st.markdown("## ⚙️ 设置")
    api_key = st.text_input("OpenAI API Key", type="password", key="ocr_api_key",
                           help="用于图片识别")
    if api_key:
        st.success("✅ API Key 已设置")

# 粘贴截图区域
st.markdown("### 📋 粘贴截图识别")

# 使用自定义组件实现粘贴功能，将结果存入session_state
if "pasted_image_data" not in st.session_state:
    st.session_state.pasted_image_data = None

paste_html = """
<style>
#paste-area {
    border: 3px dashed #667eea;
    border-radius: 12px;
    padding: 30px;
    text-align: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    cursor: pointer;
    min-height: 120px;
}
#paste-area:focus { border-color: #764ba2; outline: none; }
#paste-area img { max-width: 100%; max-height: 300px; border-radius: 8px; margin-top: 10px; }
#result-box { margin-top: 15px; padding: 10px; background: #e8f5e9; border-radius: 8px; display: none; }
</style>

<div id="paste-area" tabindex="0" onclick="this.focus()">
    <p>📋 <b>点击此处</b>，然后按 <b>Ctrl+V</b> 粘贴截图</p>
    <img id="preview" style="display:none">
</div>
<div id="result-box">
    <p>✅ 已粘贴！请复制下方数据到输入框：</p>
    <textarea id="base64-output" style="width:100%;height:60px;font-size:10px;"></textarea>
</div>

<script>
document.getElementById('paste-area').addEventListener('paste', function(e) {
    var items = e.clipboardData.items;
    for (var i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            var blob = items[i].getAsFile();
            var reader = new FileReader();
            reader.onload = function(event) {
                document.getElementById('preview').src = event.target.result;
                document.getElementById('preview').style.display = 'block';
                document.getElementById('result-box').style.display = 'block';
                document.getElementById('base64-output').value = event.target.result;
                document.getElementById('base64-output').select();
            };
            reader.readAsDataURL(blob);
            e.preventDefault();
            break;
        }
    }
});
</script>
"""
components.html(paste_html, height=350)

st.markdown("**粘贴后复制上方的数据到这里：**")
base64_input = st.text_area("图片数据", height=80, key="base64_input", 
                            placeholder="粘贴截图后，复制上方生成的数据到这里...")

# 或者上传文件
st.markdown("---")
uploaded_file = st.file_uploader("或者直接上传截图文件", type=['png', 'jpg', 'jpeg'], key="ocr_upload")

if uploaded_file:
    st.image(uploaded_file, caption="上传的截图", width=400)
    
    # 检查是否有OpenAI API Key
    api_key = st.text_input("OpenAI API Key", type="password", key="ocr_api_key")
    
    if api_key and st.button("识别数字"):
        try:
            import openai
            import base64
            
            # 读取图片并编码
            image_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 调用OpenAI Vision API
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的所有数字，只返回数字，每个数字一行，不要任何其他文字说明。如果是表格，按行从左到右、从上到下的顺序列出所有数字。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            st.success("识别结果：")
            st.code(result)
            
            # 提取数字
            numbers = re.findall(r'-?[\d,]+\.?\d*', result)
            nums = [float(n.replace(',', '')) for n in numbers if n]
            
            if nums:
                st.markdown("### 📊 计算结果")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("数量", len(nums))
                    st.metric("求和", f"{sum(nums):,.2f}")
                with col2:
                    st.metric("均值", f"{sum(nums)/len(nums):,.2f}")
                    st.metric("最大", f"{max(nums):,.2f}")
                
        except Exception as e:
            st.error(f"识别失败: {str(e)}")

st.markdown("---")

# 方案2: 手动输入识别结果
st.subheader("方案2: 手动输入（备选）")

col1, col2 = st.columns(2)

with col1:
    input_a = st.text_area("🟢 组A数据", height=150, placeholder="粘贴或输入数字...")
    
with col2:
    input_b = st.text_area("🟠 组B数据", height=150, placeholder="粘贴或输入数字...")

def parse_nums(text):
    if not text:
        return []
    matches = re.findall(r'-?[\d,]+\.?\d*', text)
    return [float(m.replace(',', '')) for m in matches if m]

nums_a = parse_nums(input_a)
nums_b = parse_nums(input_b)

if nums_a:
    import numpy as np
    st.success(f"""**🟢 组A ({len(nums_a)}个)**
- 求和: {sum(nums_a):,.2f}
- 均值: {sum(nums_a)/len(nums_a):,.2f}
- 最大: {max(nums_a):,.2f}
- 最小: {min(nums_a):,.2f}
- 中位数: {float(np.median(nums_a)):,.2f}""")

if nums_b:
    import numpy as np
    st.warning(f"""**🟠 组B ({len(nums_b)}个)**
- 求和: {sum(nums_b):,.2f}
- 均值: {sum(nums_b)/len(nums_b):,.2f}
- 最大: {max(nums_b):,.2f}
- 最小: {min(nums_b):,.2f}
- 中位数: {float(np.median(nums_b)):,.2f}""")

if nums_a and nums_b:
    sum_a, sum_b = sum(nums_a), sum(nums_b)
    diff = sum_b - sum_a
    pct = (diff / abs(sum_a) * 100) if sum_a != 0 else 0
    direction = "📈 上涨" if pct >= 0 else "📉 下跌"
    
    st.info(f"""**📊 对比分析 (B vs A)**
- 求和差值: {diff:+,.2f}
- 涨跌比: {direction} {pct:+.2f}%""")
