# 周均数据对比分析器

一个用于分析报表系统导出数据的工具，支持格式修正、差值对比、异常标记和漏斗归因分析。

## 功能特性

- ✅ **数据格式修正** - 自动处理千分位、百分号、空白字符等常见格式问题
- ✅ **周均数据对比** - 计算差值和涨跌率
- ✅ **异常标记** - 自动标出涨跌异常数据（默认阈值15%）
- ✅ **漏斗分析** - 计算各环节转化率，识别瓶颈
- ✅ **智能归因** - 根据指标类型给出可能原因

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基本使用

```python
from weekly_analyzer import WeeklyDataAnalyzer

# 初始化分析器
analyzer = WeeklyDataAnalyzer()

# 方式一：从文件加载（支持 CSV/Excel）
analyzer.load_data('your_data.csv')

# 方式二：从 DataFrame 加载
import pandas as pd
df = pd.read_csv('your_data.csv')
analyzer.load_from_dataframe(df)

# 清洗数据
analyzer.clean_data()

# 对比分析
result = analyzer.compare_weeks(
    current_week_col='本周均值',    # 本周数据列名
    previous_week_col='上周均值',   # 上周数据列名
    metric_col='指标'               # 指标名称列名
)

# 查看异常数据
abnormal = analyzer.get_abnormal_metrics()
print(abnormal)

# 漏斗分析（按顺序指定漏斗各阶段）
funnel_stages = ['UV(访客数)', '加购数', '提交订单数', '支付成功数']
analyzer.analyze_funnel(funnel_stages)

# 生成完整报告
report = analyzer.generate_report()
print(report)

# 导出结果
analyzer.export_result('分析结果.xlsx')
```

### 3. 运行示例
```bash
python weekly_analyzer.py
```

## 数据格式要求

CSV 或 Excel 文件，至少包含以下列：
| 指标 | 上周均值 | 本周均值 |
|------|----------|----------|
| UV   | 100000   | 95000    |
| PV   | 350000   | 320000   |

## 配置参数

```python
from weekly_analyzer import WeeklyDataAnalyzer, AnalysisConfig

# 自定义配置
config = AnalysisConfig(
    abnormal_threshold=0.15,      # 异常阈值（15%）
    critical_threshold=0.30,      # 严重异常阈值（30%）
    funnel_drop_threshold=0.20,   # 漏斗转化率异常阈值（20%）
    decimal_places=2              # 小数位数
)

analyzer = WeeklyDataAnalyzer(config)
```

## 输出示例

```
============================================================
           周均数据对比分析报告
============================================================

📊 【数据对比明细】

        指标  上周均值  本周均值    差值  涨跌率       状态 是否异常
  UV(访客数)  100000    95000  -5000   -5.0  正常下降      否
  PV(页面浏览) 350000   320000 -30000   -8.6  正常下降      否
      加购数   15000    12000  -3000  -20.0 ⚠️ 异常下降  ⚠️ 是

⚠️ 【异常数据标记】
      指标  上周均值  本周均值   差值  涨跌率       状态 是否异常
    加购数   15000    12000  -3000  -20.0 ⚠️ 异常下降  ⚠️ 是

📝 【分析结论】
  📉 整体表现下滑，最终指标【支付成功数】环比下降4.0%
  ⚠️ 需重点关注环节：加购数
  🔍 主要瓶颈：【加购数】下降20.0%
  💡 可能原因：物料吸引力下降, 用户兴趣变化, 展示位置变化
```

## 文件说明

- `weekly_analyzer.py` - 主分析器代码
- `sample_data.csv` - 示例数据
- `requirements.txt` - 依赖包
