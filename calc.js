(function(){
    if(window._calcToolActive) return alert('计算工具已启用！');
    window._calcToolActive = true;
    
    var nums = [];
    var cells = [];
    
    // 添加样式
    var style = document.createElement('style');
    style.id = 'calc-tool-style';
    style.textContent = `
        body { outline: 4px solid #667eea !important; outline-offset: -4px; }
        .calc-selected { background: #4CAF50 !important; color: white !important; }
        #calc-panel { position: fixed; top: 20px; right: 20px; z-index: 2147483647; 
            background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
            padding: 20px; border-radius: 12px; font-family: Arial, sans-serif; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.3); min-width: 250px; }
        #calc-panel button { border: none; padding: 10px 16px; border-radius: 6px; 
            cursor: pointer; font-size: 14px; margin-right: 8px; }
    `;
    document.head.appendChild(style);
    
    // 创建面板
    var panel = document.createElement('div');
    panel.id = 'calc-panel';
    panel.innerHTML = `
        <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">🧮 计算工具已启用</div>
        <div style="background:rgba(255,255,255,0.2);padding:8px;border-radius:6px;margin-bottom:12px;font-size:13px;">
            ✅ 紫色边框 = 已激活<br>👆 直接点击单元格选择
        </div>
        <div id="calc-count" style="margin-bottom:8px;">已选择: 0 个</div>
        <div id="calc-results" style="background:rgba(0,0,0,0.2);padding:12px;border-radius:8px;margin-bottom:15px;line-height:1.8;">
            点击单元格开始...
        </div>
        <button id="calc-clear" style="background:rgba(255,255,255,0.25);color:white;">清除</button>
        <button id="calc-close" style="background:#e74c3c;color:white;">关闭</button>
    `;
    document.body.appendChild(panel);
    
    function parseNum(text) {
        var n = text.replace(/[,%￥$\s]/g, '');
        var f = parseFloat(n);
        return isNaN(f) ? null : f;
    }
    
    function update() {
        document.getElementById('calc-count').textContent = '已选择: ' + nums.length + ' 个';
        var el = document.getElementById('calc-results');
        if (nums.length === 0) {
            el.innerHTML = '点击单元格开始...';
            return;
        }
        var sum = nums.reduce((a,b) => a+b, 0);
        var avg = sum / nums.length;
        var max = Math.max(...nums);
        var min = Math.min(...nums);
        var html = '<div>➕ 求和: <b>' + sum.toLocaleString() + '</b></div>';
        html += '<div>📊 平均: <b>' + avg.toLocaleString(undefined,{maximumFractionDigits:2}) + '</b></div>';
        html += '<div>⬆️ 最大: <b>' + max.toLocaleString() + '</b></div>';
        html += '<div>⬇️ 最小: <b>' + min.toLocaleString() + '</b></div>';
        html += '<div>🔢 计数: <b>' + nums.length + '</b></div>';
        if (nums.length >= 2) {
            var change = ((nums[nums.length-1] - nums[0]) / Math.abs(nums[0]) * 100);
            html += '<div>📈 变化: <b style="color:' + (change>=0?'#98FB98':'#FFB6C1') + '">' + 
                (change>=0?'+':'') + change.toFixed(2) + '%</b></div>';
        }
        el.innerHTML = html;
    }
    
    function onClick(e) {
        var cell = e.target.closest('td, th');
        if (!cell || panel.contains(e.target)) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        var idx = cells.indexOf(cell);
        if (idx > -1) {
            cell.classList.remove('calc-selected');
            cells.splice(idx, 1);
            nums.splice(idx, 1);
        } else {
            var val = parseNum(cell.innerText);
            if (val !== null) {
                cell.classList.add('calc-selected');
                cells.push(cell);
                nums.push(val);
            }
        }
        update();
    }
    
    document.addEventListener('click', onClick, true);
    
    document.getElementById('calc-clear').onclick = function(e) {
        e.stopPropagation();
        cells.forEach(c => c.classList.remove('calc-selected'));
        cells = [];
        nums = [];
        update();
    };
    
    document.getElementById('calc-close').onclick = function(e) {
        e.stopPropagation();
        cells.forEach(c => c.classList.remove('calc-selected'));
        document.removeEventListener('click', onClick, true);
        panel.remove();
        style.remove();
        window._calcToolActive = false;
    };
    
    alert('🧮 计算工具已启用！\n\n直接点击表格单元格选择数据');
})();
