"""
截图识别完整版 - Ctrl+V粘贴 + EasyOCR免费识别
"""
import streamlit as st
import streamlit.components.v1 as components
import re
import base64
from io import BytesIO
import numpy as np

st.set_page_config(page_title="截图识别", page_icon="📷", layout="wide")

# 初始化session state
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "group_a" not in st.session_state:
    st.session_state.group_a = []
if "group_b" not in st.session_state:
    st.session_state.group_b = []

st.title("📷 截图识别数字")
st.caption("支持Ctrl+V粘贴截图，EasyOCR免费识别")

# 创建两列布局
col_left, col_right = st.columns([2, 1])

with col_left:
    # 粘贴/上传区域
    st.markdown("### 📋 粘贴或上传截图")
    
    # Ctrl+V粘贴区域
    paste_html = """
    <style>
    #paste-zone {
        border: 3px dashed #667eea;
        border-radius: 12px;
        padding: 30px 20px;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
        cursor: pointer;
        min-height: 180px;
        transition: all 0.3s;
    }
    #paste-zone:focus {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #e8ffe8 0%, #c8ffc8 100%);
        outline: none;
    }
    #paste-zone.has-image { border-color: #4CAF50; border-style: solid; }
    #paste-zone img { max-width: 100%; max-height: 280px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .hint { color: #666; font-size: 15px; }
    #b64-out { width: 100%; height: 50px; font-size: 9px; margin-top: 10px; display: none; }
    .btn { margin-top: 8px; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; margin-right: 8px; }
    .copy-btn { background: #4CAF50; color: white; }
    .clear-btn { background: #f44336; color: white; }
    </style>
    
    <div id="paste-zone" tabindex="0" autofocus>
        <p class="hint" id="hint1">📋 <b>点击此处</b>，然后按 <b>Ctrl+V</b> 粘贴截图</p>
        <p class="hint" id="hint2" style="font-size:12px;color:#999">或直接拖拽图片到此处</p>
        <img id="preview" style="display:none">
    </div>
    <textarea id="b64-out" readonly></textarea>
    <button class="btn copy-btn" id="copy-btn" style="display:none" onclick="copyB64()">📋 复制图片数据</button>
    <button class="btn clear-btn" id="clear-btn" style="display:none" onclick="clearImage()">🗑️ 清除图片</button>
    
    <script>
    var pasteZone = document.getElementById('paste-zone');
    pasteZone.focus();
    
    function handleImage(dataUrl) {
        document.getElementById('preview').src = dataUrl;
        document.getElementById('preview').style.display = 'block';
        pasteZone.classList.add('has-image');
        document.getElementById('hint1').style.display = 'none';
        document.getElementById('hint2').style.display = 'none';
        document.getElementById('b64-out').value = dataUrl;
        document.getElementById('b64-out').style.display = 'block';
        document.getElementById('copy-btn').style.display = 'inline-block';
        document.getElementById('clear-btn').style.display = 'inline-block';
        localStorage.setItem('ocr_image', dataUrl);
    }
    
    // 粘贴事件
    document.addEventListener('paste', function(e) {
        var items = e.clipboardData.items;
        for (var i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                var blob = items[i].getAsFile();
                var reader = new FileReader();
                reader.onload = function(event) { handleImage(event.target.result); };
                reader.readAsDataURL(blob);
                e.preventDefault();
                break;
            }
        }
    });
    
    // 拖拽事件
    pasteZone.addEventListener('dragover', function(e) { e.preventDefault(); this.style.borderColor = '#4CAF50'; });
    pasteZone.addEventListener('dragleave', function(e) { this.style.borderColor = '#667eea'; });
    pasteZone.addEventListener('drop', function(e) {
        e.preventDefault();
        var file = e.dataTransfer.files[0];
        if (file && file.type.indexOf('image') !== -1) {
            var reader = new FileReader();
            reader.onload = function(event) { handleImage(event.target.result); };
            reader.readAsDataURL(file);
        }
    });
    
    // 复制功能
    function copyB64() {
        var txt = document.getElementById('b64-out');
        txt.select();
        document.execCommand('copy');
        document.getElementById('copy-btn').innerText = '✅ 已复制！';
        setTimeout(function() { document.getElementById('copy-btn').innerText = '📋 复制图片数据'; }, 2000);
    }
    
    // 清除图片
    function clearImage() {
        document.getElementById('preview').src = '';
        document.getElementById('preview').style.display = 'none';
        document.getElementById('hint1').style.display = 'block';
        document.getElementById('hint2').style.display = 'block';
        pasteZone.classList.remove('has-image');
        document.getElementById('b64-out').value = '';
        document.getElementById('b64-out').style.display = 'none';
        document.getElementById('copy-btn').style.display = 'none';
        document.getElementById('clear-btn').style.display = 'none';
        localStorage.removeItem('ocr_image');
    }
    
    // 不再从localStorage恢复图片，每次刷新都是空白
    // 清除旧数据
    localStorage.removeItem('ocr_image');
    </script>
    """
    components.html(paste_html, height=380)
    
    # 手动输入base64
    with st.expander("📝 粘贴图片数据（从上方复制）", expanded=False):
        img_data = st.text_area("Base64图片数据", height=80, key="img_b64", 
                                placeholder="点击上方'复制图片数据'按钮，然后粘贴到这里...")
    
    # 或上传文件
    st.markdown("**或者直接上传文件：**")
    uploaded = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

with col_right:
    st.markdown("### 🧮 计算结果")
    
    # 显示两组数据
    if st.session_state.group_a:
        nums_a = st.session_state.group_a
        st.success(f"""**🟢 组A ({len(nums_a)}个)**
- 求和: {sum(nums_a):,.2f}
- 均值: {sum(nums_a)/len(nums_a):,.2f}""")
    else:
        st.info("🟢 组A: 未设置")
    
    if st.session_state.group_b:
        nums_b = st.session_state.group_b
        st.warning(f"""**🟠 组B ({len(nums_b)}个)**
- 求和: {sum(nums_b):,.2f}
- 均值: {sum(nums_b)/len(nums_b):,.2f}""")
    else:
        st.info("🟠 组B: 未设置")
    
    # 对比分析
    if st.session_state.group_a and st.session_state.group_b:
        sum_a = sum(st.session_state.group_a)
        sum_b = sum(st.session_state.group_b)
        diff = sum_b - sum_a
        pct = (diff / abs(sum_a) * 100) if sum_a != 0 else 0
        direction = "📈 上涨" if pct >= 0 else "📉 下跌"
        
        st.markdown("---")
        st.markdown("**📊 对比 (B vs A)**")
        st.metric("差值", f"{diff:+,.2f}", f"{pct:+.2f}%")
        st.metric("涨跌", direction)
    
    # 清除按钮
    if st.button("🗑️ 清除所有", use_container_width=True):
        st.session_state.group_a = []
        st.session_state.group_b = []
        st.session_state.ocr_result = None
        st.rerun()

# 识别按钮
st.markdown("---")

if st.button("🔍 识别截图中的数字", type="primary", use_container_width=True):
    # 确定图片来源
    image_bytes = None
    
    if uploaded:
        image_bytes = uploaded.getvalue()
    elif img_data and img_data.startswith('data:image'):
        # 解析base64
        try:
            b64_part = img_data.split(',')[1]
            image_bytes = base64.b64decode(b64_part)
        except:
            st.error("图片数据格式错误")
    
    if image_bytes:
        with st.spinner("正在识别（首次加载模型约30秒）..."):
            try:
                import easyocr
                from PIL import Image
                
                # 读取图片
                img = Image.open(BytesIO(image_bytes))
                img_array = np.array(img)
                
                # OCR识别
                reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                results = reader.readtext(img_array)
                
                # 提取数字
                all_nums = []
                raw_lines = []
                
                for (bbox, text, prob) in results:
                    raw_lines.append(text)
                    nums = re.findall(r'-?[\d,]+\.?\d*', text)
                    for n in nums:
                        try:
                            val = float(n.replace(',', ''))
                            if val != 0:
                                all_nums.append(val)
                        except:
                            pass
                
                st.session_state.ocr_result = {
                    'raw': '\n'.join(raw_lines),
                    'nums': all_nums
                }
                st.success(f"✅ 识别完成！找到 {len(all_nums)} 个数字")
                
            except ImportError:
                st.error("EasyOCR未安装，请运行: pip install easyocr")
            except Exception as e:
                st.error(f"识别失败: {e}")
    else:
        st.warning("请先粘贴截图或上传文件")

# 显示识别结果
if st.session_state.ocr_result:
    st.markdown("### 📊 识别结果")
    
    result = st.session_state.ocr_result
    
    # 原始文本
    with st.expander("原始识别文本"):
        st.text(result['raw'])
    
    # 可编辑数字列表
    edited = st.text_area("识别到的数字（可编辑）", 
                          '\n'.join([str(n) for n in result['nums']]), 
                          height=120)
    
    # 解析编辑后的数字
    final_nums = []
    for line in edited.split('\n'):
        clean = re.sub(r'[^\d.\-]', '', line)
        if clean and re.match(r'^-?\d+\.?\d*$', clean):
            final_nums.append(float(clean))
    
    if final_nums:
        # 统计
        st.success(f"""**共 {len(final_nums)} 个数字**
- ➕ 求和: **{sum(final_nums):,.2f}**
- 📊 均值: **{sum(final_nums)/len(final_nums):,.2f}**
- ⬆️ 最大: **{max(final_nums):,.2f}** | ⬇️ 最小: **{min(final_nums):,.2f}**
- 📍 中位数: **{float(np.median(final_nums)):,.2f}**""")
        
        # 存入组
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ 存入组A", use_container_width=True, type="primary"):
                st.session_state.group_a = final_nums
                st.rerun()
        with col2:
            if st.button("➕ 存入组B", use_container_width=True):
                st.session_state.group_b = final_nums
                st.rerun()
