"""
周均数据对比分析器
功能：
1. 数据格式修正 - 处理报表系统常见格式问题
2. 周均计算与对比 - 计算差值和涨跌率
3. 异常标记 - 标出涨跌异常数据
4. 漏斗分析 - 给出结论和归因
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')


class TrendStatus(Enum):
    """涨跌状态"""
    NORMAL_UP = "正常上涨"
    NORMAL_DOWN = "正常下降"
    ABNORMAL_UP = "[!] 异常上涨"
    ABNORMAL_DOWN = "[!] 异常下降"
    STABLE = "稳定"


@dataclass
class AnalysisConfig:
    """分析配置"""
    abnormal_threshold: float = 0.15  # 涨跌幅超过15%视为异常
    critical_threshold: float = 0.30  # 涨跌幅超过30%视为严重异常
    funnel_drop_threshold: float = 0.20  # 漏斗转化率下降超过20%视为异常
    decimal_places: int = 2  # 小数位数


class WeeklyDataAnalyzer:
    """周均数据对比分析器"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.raw_data: Optional[pd.DataFrame] = None
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.comparison_result: Optional[pd.DataFrame] = None
        self.funnel_analysis: Optional[Dict] = None
        
    def load_data(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        加载数据文件
        支持: CSV, Excel (.xlsx, .xls)
        """
        file_ext = file_path.lower().split('.')[-1]
        
        try:
            if file_ext == 'csv':
                # 尝试多种编码
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        self.raw_data = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif file_ext in ['xlsx', 'xls']:
                self.raw_data = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            print(f"[OK] 成功加载数据: {len(self.raw_data)} 行, {len(self.raw_data.columns)} 列")
            return self.raw_data
            
        except Exception as e:
            raise Exception(f"加载数据失败: {str(e)}")
    
    def load_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """从DataFrame加载数据"""
        self.raw_data = df.copy()
        print(f"[OK] 成功加载数据: {len(self.raw_data)} 行, {len(self.raw_data.columns)} 列")
        return self.raw_data
    
    def clean_data(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        数据格式修正
        - 去除空白字符
        - 转换数值格式（移除千分位、百分号等）
        - 处理缺失值
        - 统一列名格式
        """
        data = df if df is not None else self.raw_data
        if data is None:
            raise ValueError("没有可处理的数据")
        
        cleaned = data.copy()
        
        # 1. 清理列名
        cleaned.columns = cleaned.columns.str.strip()
        
        # 2. 处理每一列
        for col in cleaned.columns:
            if cleaned[col].dtype == 'object':
                # 去除空白字符
                cleaned[col] = cleaned[col].astype(str).str.strip()
                
                # 尝试转换为数值
                cleaned[col] = self._try_convert_numeric(cleaned[col])
        
        # 3. 处理缺失值
        numeric_cols = cleaned.select_dtypes(include=[np.number]).columns
        cleaned[numeric_cols] = cleaned[numeric_cols].fillna(0)
        
        self.cleaned_data = cleaned
        print(f"[OK] 数据清洗完成")
        return cleaned
    
    def _try_convert_numeric(self, series: pd.Series) -> pd.Series:
        """尝试将字符串列转换为数值"""
        def convert_value(val):
            if pd.isna(val) or val == 'nan' or val == '':
                return np.nan
            
            val_str = str(val).strip()
            
            # 移除千分位分隔符
            val_str = val_str.replace(',', '')
            
            # 处理百分号
            if '%' in val_str:
                try:
                    return float(val_str.replace('%', '')) / 100
                except:
                    return val
            
            # 尝试直接转换
            try:
                return float(val_str)
            except:
                return val
        
        converted = series.apply(convert_value)
        
        # 如果大部分值都能转换为数值，则返回转换后的结果
        numeric_count = pd.to_numeric(converted, errors='coerce').notna().sum()
        if numeric_count > len(converted) * 0.5:
            return pd.to_numeric(converted, errors='coerce')
        return series
    
    def compare_weeks(self, 
                      current_week_col: str, 
                      previous_week_col: str,
                      metric_col: str) -> pd.DataFrame:
        """
        对比两周数据
        
        Args:
            current_week_col: 本周数据列名
            previous_week_col: 上周数据列名  
            metric_col: 指标名称列名
        
        Returns:
            包含对比结果的DataFrame
        """
        data = self.cleaned_data if self.cleaned_data is not None else self.raw_data
        if data is None:
            raise ValueError("请先加载数据")
        
        result = pd.DataFrame()
        result['指标'] = data[metric_col]
        result['上周均值'] = pd.to_numeric(data[previous_week_col], errors='coerce')
        result['本周均值'] = pd.to_numeric(data[current_week_col], errors='coerce')
        
        # 计算差值
        result['差值'] = result['本周均值'] - result['上周均值']
        
        # 计算涨跌率
        result['涨跌率'] = result.apply(
            lambda row: (row['差值'] / row['上周均值'] * 100) 
            if row['上周均值'] != 0 else 0, 
            axis=1
        )
        result['涨跌率'] = result['涨跌率'].round(self.config.decimal_places)
        
        # 标记异常
        result['状态'] = result['涨跌率'].apply(self._evaluate_trend)
        result['是否异常'] = result['状态'].apply(lambda x: '[!] 是' if '异常' in x else '否')
        
        self.comparison_result = result
        return result
    
    def compare_weeks_auto(self, week1_data: Dict[str, float], week2_data: Dict[str, float],
                           week1_name: str = "上周", week2_name: str = "本周") -> pd.DataFrame:
        """
        自动对比两周数据（字典格式输入）
        
        Args:
            week1_data: 上周数据 {指标名: 值}
            week2_data: 本周数据 {指标名: 值}
        """
        metrics = list(set(week1_data.keys()) | set(week2_data.keys()))
        
        result = pd.DataFrame()
        result['指标'] = metrics
        result[f'{week1_name}均值'] = [week1_data.get(m, 0) for m in metrics]
        result[f'{week2_name}均值'] = [week2_data.get(m, 0) for m in metrics]
        
        # 计算差值
        result['差值'] = result[f'{week2_name}均值'] - result[f'{week1_name}均值']
        
        # 计算涨跌率
        result['涨跌率(%)'] = result.apply(
            lambda row: round((row['差值'] / row[f'{week1_name}均值'] * 100), 2) 
            if row[f'{week1_name}均值'] != 0 else 0, 
            axis=1
        )
        
        # 标记异常
        result['状态'] = result['涨跌率(%)'].apply(self._evaluate_trend)
        result['是否异常'] = result['状态'].apply(lambda x: '[!] 是' if '异常' in x else '否')
        
        self.comparison_result = result
        return result
    
    def _evaluate_trend(self, change_rate: float) -> str:
        """评估涨跌趋势"""
        abs_rate = abs(change_rate) / 100  # 转换为小数
        
        if abs_rate < 0.03:  # 小于3%视为稳定
            return TrendStatus.STABLE.value
        elif abs_rate >= self.config.critical_threshold:
            return TrendStatus.ABNORMAL_UP.value if change_rate > 0 else TrendStatus.ABNORMAL_DOWN.value
        elif abs_rate >= self.config.abnormal_threshold:
            return TrendStatus.ABNORMAL_UP.value if change_rate > 0 else TrendStatus.ABNORMAL_DOWN.value
        else:
            return TrendStatus.NORMAL_UP.value if change_rate > 0 else TrendStatus.NORMAL_DOWN.value
    
    def analyze_funnel(self, funnel_stages: List[str], 
                       stage_col: str = '指标',
                       current_col: str = '本周均值',
                       previous_col: str = '上周均值') -> Dict:
        """
        漏斗分析
        
        Args:
            funnel_stages: 漏斗阶段列表（按顺序）
            stage_col: 阶段列名
            current_col: 本周数据列名
            previous_col: 上周数据列名
        """
        data = self.comparison_result if self.comparison_result is not None else self.cleaned_data
        if data is None:
            raise ValueError("请先进行数据对比")
        
        funnel_result = {
            'stages': [],
            'conversion_rates': [],
            'rate_changes': [],
            'issues': [],
            'conclusions': []
        }
        
        for i, stage in enumerate(funnel_stages):
            stage_data = data[data[stage_col] == stage]
            if stage_data.empty:
                continue
                
            current_val = float(stage_data[current_col].values[0])
            previous_val = float(stage_data[previous_col].values[0])
            
            stage_info = {
                'name': stage,
                'current': current_val,
                'previous': previous_val,
                'change': current_val - previous_val,
                'change_rate': ((current_val - previous_val) / previous_val * 100) if previous_val != 0 else 0
            }
            
            # 计算转化率（相对于上一阶段）
            if i > 0 and len(funnel_result['stages']) > 0:
                prev_stage = funnel_result['stages'][-1]
                if prev_stage['current'] != 0:
                    stage_info['conversion_rate_current'] = current_val / prev_stage['current'] * 100
                else:
                    stage_info['conversion_rate_current'] = 0
                    
                if prev_stage['previous'] != 0:
                    stage_info['conversion_rate_previous'] = previous_val / prev_stage['previous'] * 100
                else:
                    stage_info['conversion_rate_previous'] = 0
                
                # 转化率变化
                conv_change = stage_info['conversion_rate_current'] - stage_info['conversion_rate_previous']
                stage_info['conversion_change'] = conv_change
                
                # 判断是否异常
                if abs(conv_change) > self.config.funnel_drop_threshold * 100:
                    issue = f"[!] 【{stage}】转化率{'上升' if conv_change > 0 else '下降'}{abs(conv_change):.1f}%，需重点关注"
                    funnel_result['issues'].append(issue)
            
            funnel_result['stages'].append(stage_info)
        
        # 生成结论
        funnel_result['conclusions'] = self._generate_conclusions(funnel_result)
        self.funnel_analysis = funnel_result
        
        return funnel_result
    
    def _generate_conclusions(self, funnel_result: Dict) -> List[str]:
        """生成分析结论"""
        conclusions = []
        
        if not funnel_result['stages']:
            return ["数据不足，无法生成结论"]
        
        # 1. 整体趋势
        first_stage = funnel_result['stages'][0]
        last_stage = funnel_result['stages'][-1]
        
        overall_change = last_stage['change_rate']
        if overall_change > 10:
            conclusions.append(f"[UP] 整体表现良好，最终指标【{last_stage['name']}】环比上涨{overall_change:.1f}%")
        elif overall_change < -10:
            conclusions.append(f"[DOWN] 整体表现下滑，最终指标【{last_stage['name']}】环比下降{abs(overall_change):.1f}%")
        else:
            conclusions.append(f"[--] 整体表现稳定，最终指标【{last_stage['name']}】环比变化{overall_change:.1f}%")
        
        # 2. 问题环节识别
        problem_stages = []
        for i, stage in enumerate(funnel_result['stages']):
            if stage['change_rate'] < -self.config.abnormal_threshold * 100:
                problem_stages.append(stage['name'])
        
        if problem_stages:
            conclusions.append(f"[!] 需重点关注环节：{', '.join(problem_stages)}")
        
        # 3. 归因分析
        if len(funnel_result['stages']) >= 2:
            # 找出下降最严重的环节
            max_drop_stage = min(funnel_result['stages'], key=lambda x: x['change_rate'])
            if max_drop_stage['change_rate'] < -5:
                conclusions.append(f"[*] 主要瓶颈：【{max_drop_stage['name']}】下降{abs(max_drop_stage['change_rate']):.1f}%")
                conclusions.append(self._attribute_cause(max_drop_stage))
        
        # 4. 问题列表
        if funnel_result['issues']:
            conclusions.append("\n[LIST] 具体问题：")
            conclusions.extend([f"  - {issue}" for issue in funnel_result['issues']])
        
        return conclusions
    
    def _attribute_cause(self, stage: Dict) -> str:
        """归因分析"""
        change_rate = stage['change_rate']
        stage_name = stage['name']
        
        # 根据指标名称推测可能的原因
        causes = []
        
        if any(kw in stage_name for kw in ['曝光', '展示', 'PV', 'UV', '访问']):
            if change_rate < 0:
                causes = ["流量渠道变化", "推广投放减少", "自然流量波动", "竞品分流"]
            else:
                causes = ["推广投放增加", "活动引流", "自然增长"]
                
        elif any(kw in stage_name for kw in ['点击', 'CTR', '进入']):
            if change_rate < 0:
                causes = ["物料吸引力下降", "用户兴趣变化", "展示位置变化", "竞品影响"]
            else:
                causes = ["物料优化效果", "精准度提升"]
                
        elif any(kw in stage_name for kw in ['转化', '成交', '订单', '支付', '购买']):
            if change_rate < 0:
                causes = ["价格竞争力下降", "用户决策周期延长", "支付流程问题", "库存问题"]
            else:
                causes = ["促销活动效果", "价格优势", "服务体验提升"]
                
        elif any(kw in stage_name for kw in ['留存', '复购', '回访']):
            if change_rate < 0:
                causes = ["用户体验下降", "产品问题", "竞品吸引", "触达效率下降"]
            else:
                causes = ["用户粘性提升", "会员策略奏效"]
        else:
            if change_rate < 0:
                causes = ["外部环境变化", "内部运营调整", "数据统计口径变化"]
            else:
                causes = ["运营策略优化", "产品改进", "市场增长"]
        
        return f"[CAUSE] 可能原因：{', '.join(causes[:3])}"
    
    def get_abnormal_metrics(self) -> pd.DataFrame:
        """获取所有异常指标"""
        if self.comparison_result is None:
            raise ValueError("请先进行数据对比")
        
        abnormal = self.comparison_result[self.comparison_result['是否异常'].str.contains('是')]
        return abnormal
    
    def generate_report(self) -> str:
        """生成完整分析报告"""
        report = []
        report.append("=" * 60)
        report.append("           周均数据对比分析报告")
        report.append("=" * 60)
        
        if self.comparison_result is not None:
            report.append("\n[DATA] 【数据对比明细】\n")
            report.append(self.comparison_result.to_string(index=False))
            
            # 异常数据汇总
            abnormal = self.get_abnormal_metrics()
            if not abnormal.empty:
                report.append("\n\n[!] 【异常数据标记】\n")
                report.append(abnormal.to_string(index=False))
        
        if self.funnel_analysis is not None:
            report.append("\n\n[FUNNEL] 【漏斗分析】\n")
            for stage in self.funnel_analysis['stages']:
                conv_info = ""
                if 'conversion_rate_current' in stage:
                    conv_info = f" (转化率: {stage['conversion_rate_current']:.1f}%)"
                report.append(f"  {stage['name']}: {stage['current']:,.0f} (环比: {stage['change_rate']:+.1f}%){conv_info}")
            
            report.append("\n\n[REPORT] 【分析结论】\n")
            for conclusion in self.funnel_analysis['conclusions']:
                report.append(f"  {conclusion}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def export_result(self, output_path: str):
        """导出分析结果"""
        if self.comparison_result is None:
            raise ValueError("没有可导出的结果")
        
        if output_path.endswith('.xlsx'):
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                self.comparison_result.to_excel(writer, sheet_name='数据对比', index=False)
                
                abnormal = self.get_abnormal_metrics()
                if not abnormal.empty:
                    abnormal.to_excel(writer, sheet_name='异常数据', index=False)
        else:
            self.comparison_result.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"[OK] 结果已导出至: {output_path}")


def demo():
    """演示示例"""
    print("=" * 60)
    print("        周均数据对比分析器 - 使用示例")
    print("=" * 60)
    
    # 创建示例数据
    sample_data = {
        '指标': ['UV(访客数)', 'PV(页面浏览)', '加购数', '提交订单数', '支付成功数', '支付金额(元)'],
        '上周均值': [100000, 350000, 15000, 8000, 5000, 250000],
        '本周均值': [95000, 320000, 12000, 7200, 4800, 235000]
    }
    
    df = pd.DataFrame(sample_data)
    
    # 初始化分析器
    analyzer = WeeklyDataAnalyzer()
    
    # 加载数据
    analyzer.load_from_dataframe(df)
    
    # 清洗数据
    analyzer.clean_data()
    
    # 对比分析
    result = analyzer.compare_weeks(
        current_week_col='本周均值',
        previous_week_col='上周均值', 
        metric_col='指标'
    )
    
    # 漏斗分析
    funnel_stages = ['UV(访客数)', 'PV(页面浏览)', '加购数', '提交订单数', '支付成功数']
    analyzer.analyze_funnel(funnel_stages)
    
    # 生成报告
    report = analyzer.generate_report()
    print(report)
    
    return analyzer


if __name__ == "__main__":
    demo()
