"""
截图识别 - Gradio版本（支持Ctrl+V粘贴）
"""
import gradio as gr
import numpy as np
import re

# 初始化两组数据
group_a = []
group_b = []

def recognize_numbers(image):
    """识别图片中的数字"""
    if image is None:
        return "请先粘贴或上传截图", ""
    
    try:
        import easyocr
        
        # OCR识别
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        results = reader.readtext(np.array(image))
        
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
        
        if not all_nums:
            return "未识别到数字", ""
        
        # 计算统计
        nums_str = '\n'.join([str(n) for n in all_nums])
        
        stats = f"""📊 识别到 {len(all_nums)} 个数字

➕ 求和: {sum(all_nums):,.2f}
📊 均值: {sum(all_nums)/len(all_nums):,.2f}
⬆️ 最大: {max(all_nums):,.2f}
⬇️ 最小: {min(all_nums):,.2f}
📍 中位数: {float(np.median(all_nums)):,.2f}"""
        
        return stats, nums_str
        
    except Exception as e:
        return f"识别失败: {e}", ""

def save_to_group_a(nums_text):
    """存入组A"""
    global group_a
    nums = parse_nums(nums_text)
    if nums:
        group_a = nums
        return get_comparison()
    return "组A: 未设置数据"

def save_to_group_b(nums_text):
    """存入组B"""
    global group_b
    nums = parse_nums(nums_text)
    if nums:
        group_b = nums
        return get_comparison()
    return "组B: 未设置数据"

def parse_nums(text):
    """解析数字"""
    nums = []
    for line in text.split('\n'):
        clean = re.sub(r'[^\d.\-]', '', line)
        if clean and re.match(r'^-?\d+\.?\d*$', clean):
            nums.append(float(clean))
    return nums

def get_comparison():
    """获取对比结果"""
    result = ""
    
    if group_a:
        result += f"🟢 组A ({len(group_a)}个): 和={sum(group_a):,.2f} 均={sum(group_a)/len(group_a):,.2f}\n"
    else:
        result += "🟢 组A: 未设置\n"
    
    if group_b:
        result += f"🟠 组B ({len(group_b)}个): 和={sum(group_b):,.2f} 均={sum(group_b)/len(group_b):,.2f}\n"
    else:
        result += "🟠 组B: 未设置\n"
    
    if group_a and group_b:
        sum_a, sum_b = sum(group_a), sum(group_b)
        diff = sum_b - sum_a
        pct = (diff / abs(sum_a) * 100) if sum_a != 0 else 0
        direction = "📈 上涨" if pct >= 0 else "📉 下跌"
        result += f"\n📊 对比 (B vs A):\n差值: {diff:+,.2f}\n涨跌: {direction} {pct:+.2f}%"
    
    return result

def clear_all():
    """清除所有"""
    global group_a, group_b
    group_a = []
    group_b = []
    return "已清除所有数据"

# 创建Gradio界面
with gr.Blocks(title="截图识别数字", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 📷 截图识别数字")
    gr.Markdown("**支持 Ctrl+V 直接粘贴截图！** 使用 EasyOCR 免费识别")
    
    with gr.Row():
        with gr.Column(scale=2):
            # 图片输入 - 支持粘贴
            image_input = gr.Image(
                label="📋 粘贴或上传截图（点击此处后按Ctrl+V）",
                type="pil",
                sources=["upload", "clipboard"],
                height=350
            )
            
            recognize_btn = gr.Button("🔍 识别数字", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            # 统计结果
            stats_output = gr.Textbox(label="📊 统计结果", lines=8)
            
            # 对比结果
            comparison_output = gr.Textbox(label="🆚 两组对比", lines=6, value="🟢 组A: 未设置\n🟠 组B: 未设置")
    
    with gr.Row():
        with gr.Column():
            nums_output = gr.Textbox(label="识别到的数字（可编辑）", lines=6)
        
        with gr.Column():
            with gr.Row():
                save_a_btn = gr.Button("➕ 存入组A", variant="primary")
                save_b_btn = gr.Button("➕ 存入组B", variant="secondary")
            clear_btn = gr.Button("🗑️ 清除所有")
    
    # 绑定事件
    recognize_btn.click(
        fn=recognize_numbers,
        inputs=[image_input],
        outputs=[stats_output, nums_output]
    )
    
    save_a_btn.click(
        fn=save_to_group_a,
        inputs=[nums_output],
        outputs=[comparison_output]
    )
    
    save_b_btn.click(
        fn=save_to_group_b,
        inputs=[nums_output],
        outputs=[comparison_output]
    )
    
    clear_btn.click(
        fn=clear_all,
        outputs=[comparison_output]
    )

# 启动
if __name__ == "__main__":
    app.launch(server_port=8510, share=False)
