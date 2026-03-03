from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import pytesseract
import re
from PIL import Image
import io

app = FastAPI()

group_a = []
group_b = []

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>截图识别数字</title>
<style>
body{font-family:sans-serif;max-width:900px;margin:40px auto;padding:0 20px;background:#f5f5f5}
h1{color:#333}
.card{background:white;border-radius:8px;padding:20px;margin:16px 0;box-shadow:0 2px 8px rgba(0,0,0,.1)}
.row{display:flex;gap:16px}
.col{flex:1}
input[type=file]{display:block;margin:8px 0;padding:8px;border:2px dashed #ccc;border-radius:4px;width:100%;cursor:pointer}
button{background:#f97316;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-size:15px;margin:4px 2px}
button:hover{background:#ea6c0a}
button.secondary{background:#6b7280}
button.secondary:hover{background:#4b5563}
textarea{width:100%;border:1px solid #ddd;border-radius:4px;padding:8px;font-size:14px;font-family:monospace}
img#preview{max-width:100%;max-height:300px;border:1px solid #ddd;border-radius:4px;display:none;margin-top:8px}
#stats,#comparison{white-space:pre-wrap;font-family:monospace}
label{font-weight:bold;color:#555}
</style>
</head>
<body>
<h1>📷 截图识别数字</h1>
<div class="row">
  <div class="col card">
    <label>上传截图</label>
    <input type="file" id="fileInput" accept="image/*">
    <img id="preview">
    <button onclick="recognize()">🔍 识别数字</button>
  </div>
  <div class="col card">
    <label>识别统计</label>
    <div id="stats" style="min-height:80px;color:#333"></div>
    <hr>
    <label>对比结果</label>
    <div id="comparison" style="min-height:60px;color:#333">🟢 组A: 未设置&#10;🟠 组B: 未设置</div>
  </div>
</div>
<div class="card">
  <label>识别数字（每行一个，可手动编辑）</label>
  <textarea id="nums" rows="6" placeholder="识别后的数字将显示在这里..."></textarea>
  <div>
    <button onclick="saveGroup('a')">存入组A</button>
    <button onclick="saveGroup('b')">存入组B</button>
    <button class="secondary" onclick="clearAll()">清除对比</button>
  </div>
</div>
<script>
document.getElementById('fileInput').onchange = function(e){
  const file = e.target.files[0];
  if(file){
    const reader = new FileReader();
    reader.onload = function(ev){
      const img = document.getElementById('preview');
      img.src = ev.target.result;
      img.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
};
async function recognize(){
  const file = document.getElementById('fileInput').files[0];
  if(!file){alert('请先选择图片');return;}
  const fd = new FormData();
  fd.append('file', file);
  document.getElementById('stats').textContent = '识别中...';
  const res = await fetch('/ocr', {method:'POST', body:fd});
  const data = await res.json();
  document.getElementById('stats').textContent = data.stats;
  document.getElementById('nums').value = data.nums;
}
async function saveGroup(g){
  const nums = document.getElementById('nums').value;
  const res = await fetch('/save_group', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({group:g, nums:nums})
  });
  const data = await res.json();
  document.getElementById('comparison').textContent = data.comparison;
}
async function clearAll(){
  const res = await fetch('/clear', {method:'POST'});
  const data = await res.json();
  document.getElementById('comparison').textContent = data.comparison;
}
</script>
</body>
</html>
"""

def parse_nums(text):
    nums = []
    for line in text.strip().split('\n'):
        clean = re.sub(r'[^\d.\-]', '', line.strip())
        if clean and re.match(r'^-?\d+\.?\d*$', clean):
            nums.append(float(clean))
    return nums

def get_comparison():
    result = ""
    if group_a:
        result += f"🟢 组A ({len(group_a)}个): 和={sum(group_a):,.2f}\n"
    else:
        result += "🟢 组A: 未设置\n"
    if group_b:
        result += f"🟠 组B ({len(group_b)}个): 和={sum(group_b):,.2f}\n"
    else:
        result += "🟠 组B: 未设置\n"
    if group_a and group_b:
        sum_a, sum_b = sum(group_a), sum(group_b)
        pct = ((sum_b - sum_a) / abs(sum_a) * 100) if sum_a != 0 else 0
        direction = "📈" if pct >= 0 else "📉"
        result += f"\n对比: {direction} {pct:+.2f}%"
    return result

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image, config='--psm 6')
    all_nums = []
    for n in re.findall(r'-?[\d,]+\.?\d*', text):
        try:
            val = float(n.replace(',', ''))
            if val != 0:
                all_nums.append(val)
        except:
            pass
    if not all_nums:
        return JSONResponse({"stats": "未识别到数字", "nums": ""})
    nums_str = '\n'.join([str(n) for n in all_nums])
    stats = (f"📊 识别到 {len(all_nums)} 个数字\n"
             f"➕ 求和: {sum(all_nums):,.2f}\n"
             f"📊 均值: {sum(all_nums)/len(all_nums):,.2f}\n"
             f"⬆️ 最大: {max(all_nums):,.2f}\n"
             f"⬇️ 最小: {min(all_nums):,.2f}")
    return JSONResponse({"stats": stats, "nums": nums_str})

@app.post("/save_group")
async def save_group(data: dict):
    global group_a, group_b
    nums = parse_nums(data.get("nums", ""))
    if data.get("group") == "a":
        group_a = nums
    else:
        group_b = nums
    return JSONResponse({"comparison": get_comparison()})

@app.post("/clear")
async def clear():
    global group_a, group_b
    group_a = []
    group_b = []
    return JSONResponse({"comparison": "🟢 组A: 未设置\n🟠 组B: 未设置"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
