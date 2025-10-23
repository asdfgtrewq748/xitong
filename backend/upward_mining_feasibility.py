# -*- coding: utf-8 -*-
"""
扰动度计算模块
基于钻孔CSV数据计算上行开采可行度
"""

import pandas as pd
import numpy as np
import re
import traceback
from typing import Tuple, Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class InterpolationLayer:
    """中间岩层数据结构"""
    name: str
    thickness: float
    tensile_strength: float
    elastic_modulus: float
    bulking_factor: float
    sequence: int


class UpwardMiningFeasibility:
    """
    上行开采可行度计算器
    基于修改后的公式实现上行开采可行度的计算
    """

    def __init__(self, lamda: float, C: float):
        """
        使用特定区域的系数初始化分析器
        Args:
            lamda (float): 上行开采可行度影响因子 (λ)
            C (float): 特定矿区的地质常数
        """
        self.lamda = lamda
        self.C = C

    @classmethod
    def calculate_coefficients(cls, khd_min: float, khd_max: float) -> Tuple[float, float]:
        """
        使用极限分区方法计算可行度系数 (λ) 和地质常数 (C)
        该方法假设可行度 'omega' 的范围为 0 到 10
        """
        if khd_max <= khd_min:
            raise ValueError("khd_max 必须大于 khd_min")

        # 根据极限分区法计算 λ
        lamda = 10.0 / (khd_max - khd_min)
        # 计算地质常数 C
        C = -lamda * khd_min

        return lamda, C

    def calculate_feasibility_from_data(self, mining_coal_thickness: float,
                                       intermediate_layers: List[Dict[str, Any]]) -> Tuple[float, float]:
        """
        根据数据计算上行开采可行度

        Args:
            mining_coal_thickness: 开采煤层厚度M
            intermediate_layers: 中间岩层数据列表

        Returns:
            Tuple[float, float]: (上行开采可行度 ω, KHD综合地质参数)
        """
        if mining_coal_thickness <= 0:
            raise ValueError("开采煤层厚度M必须是正数")

        if not intermediate_layers:
            raise ValueError("中间岩层数据不能为空")

        # 计算D和H - 两个煤层中间所有层的厚度和
        D = sum(layer['thickness'] for layer in intermediate_layers)
        H = D  # H也是中间所有层的厚度和

        if D <= 0 or H <= 0:
            raise ValueError("中间岩层总厚度必须为正数")

        # 按照公式进行求和计算
        sum_term = 0
        for i, layer in enumerate(intermediate_layers):
            Hi = layer['thickness']  # 第i层厚度
            Ri = layer.get('tensile_strength', 3.0)  # 第i层抗拉强度

            # 获取碎胀系数，如果没有则使用默认值
            Kpi = layer.get('bulking_factor', 1.15)

            # 计算Ki系数（基于抗拉强度和碎胀系数）
            Ki = self.calculate_ki_from_properties(Ri, Kpi)

            # 公式计算项: Ki × (Hi/H) × (Hi²/(D×M))
            term = Ki * (Hi/H) * (Hi**2 / (D * mining_coal_thickness))
            sum_term += term

        # 最终公式: ω = λ × ∑(...) + C
        omega = self.lamda * sum_term + self.C
        return omega, sum_term

    def calculate_ki_from_properties(self, tensile_strength: float, bulking_factor: float = 1.15,
                                   base_tensile: float = 3.0, base_bulking: float = 1.15) -> float:
        """
        根据岩石物理性质计算Ki系数
        Ki系数反映第i层岩石的综合强度特征
        """
        # 抗拉强度影响 (抗拉强度越高，Ki越大)
        tensile_factor = tensile_strength / base_tensile

        # 碎胀系数影响 (碎胀系数越大，表示岩石越破碎，Ki越小)
        bulking_factor = max(bulking_factor, 1.0)  # 确保碎胀系数≥1
        bulking_factor_normalized = base_bulking / bulking_factor

        # 综合Ki系数计算
        Ki = (tensile_factor + bulking_factor_normalized) / 2

        # 限制Ki系数在合理范围内
        return max(0.1, min(3.0, Ki))

    def evaluate_feasibility(self, omega: float) -> Dict[str, str]:
        """
        根据可行度ω值评估上行开采的可行性等级
        评估标准基于工程实践经验
        """
        if omega < 0:
            grade = "无效"
            description = "计算结果异常，请检查输入数据。"
        elif 0 <= omega < 2:
            grade = "I级 (不可行/极困难)"
            description = "煤层基本处于垮落带内，完整度破坏非常严重，上行开采不合理或过于危险。"
        elif 2 <= omega < 4:
            grade = "II级 (困难)"
            description = "上行开采难度大，易出现顶板问题和巷道支护困难，需要重型支护或充填。"
        elif 4 <= omega < 6:
            grade = "III级 (可行，需支护)"
            description = "中等破坏程度，顶板和煤层少量破碎，但裂隙发育程度大。技术上可行，局部需加强支护。"
        elif 6 <= omega < 8:
            grade = "IV级 (良好)"
            description = "轻微破坏，煤层完整性良好，顶板有少量裂隙，下沉量微小，上行开采效果较好。"
        else:  # omega >= 8
            grade = "V级 (优良)"
            description = "煤层基本不受下煤层开采的影响，煤层间的相互作用基本不存在，上行开采不存在困难。"

        return {
            "feasibility_degree": round(omega, 3),
            "level": grade,
            "description": description
        }


def get_base_coal_name(name: str) -> str:
    """
    从详细的煤层名称中提取基础名称。
    例如: '6-1煤' -> '6煤', '5煤' -> '5煤'
    """
    name = str(name).strip()
    # 匹配开头的数字
    match = re.match(r'^(\d+)', name)
    if match:
        # 如果匹配到数字，则返回 "数字+煤"
        return f"{match.group(1)}煤"
    # 如果没有匹配到数字（例如 "主焦煤"），则返回原名称
    return name


def process_borehole_csv_for_feasibility(csv_file_path: str, bottom_coal_name: str, upper_coal_name: str,
                                        lamda: float = 4.95, C: float = -0.84) -> Dict[str, Any]:
    """
    根据CSV文件处理单个钻孔文件，计算上行开采可行度

    Args:
        csv_file_path: 钻孔CSV文件路径
        bottom_coal_name: 开采煤层名称
        upper_coal_name: 上煤层名称
        lamda: 影响因子λ
        C: 地质常数C

    Returns:
        包含计算结果的字典
    """
    try:
        # 读取CSV文件
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_file_path, encoding='gbk')
            except UnicodeDecodeError:
                df = pd.read_csv(csv_file_path, encoding='latin-1')

        # 删除完全空白的行
        df.dropna(how='all', inplace=True)
        if df.empty:
            return {"error": "文件为空或无有效数据"}

        # 标准化列名
        column_mapping = {
            '序号(从下到上)': '序号',
            '序号': '序号',
            '名称': '名称',
            '厚度/m': '厚度',
            '厚度': '厚度',
            '弹性模量/Gpa': '弹性模量',
            '弹性模量': '弹性模量',
            '容重/kN*m-3': '容重',
            '容重': '容重',
            '抗拉强度/MPa': '抗拉强度',
            '抗拉强度': '抗拉强度'
        }

        df.rename(columns=lambda c: column_mapping.get(str(c).strip(), str(c).strip()), inplace=True)

        # 检查必要的列
        required_columns = ['序号', '名称', '厚度', '抗拉强度']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {"error": f"缺少必要的列: {missing_columns}"}

        # 数值列类型转换
        numeric_columns = ['序号', '厚度', '弹性模量', '容重', '抗拉强度']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- 煤层查找逻辑 ---
        # 查找所有与基础名称匹配的煤层
        bottom_coal_candidates = df[df['名称'].str.contains(get_base_coal_name(bottom_coal_name).replace('煤', ''), na=False, case=False)]
        upper_coal_candidates = df[df['名称'].str.contains(get_base_coal_name(upper_coal_name).replace('煤', ''), na=False, case=False)]

        if bottom_coal_candidates.empty:
            return {"error": f"未找到任何与 '{bottom_coal_name}' 相关的开采煤层"}

        if upper_coal_candidates.empty:
            return {"error": f"未找到任何与 '{upper_coal_name}' 相关的上煤层"}

        # 在从下到上的文件中：
        # 行索引小的在下面（先出现的是下面的层）
        # 行索引大的在上面（后出现的是上面的层）
        # 因此，开采煤层（下层）应该有较小的行索引
        # 上煤层应该有较大的行索引

        # 从候选者中选择开采煤层（选择最下面的，即行索引最小的）
        bottom_coal_row = bottom_coal_candidates.loc[[bottom_coal_candidates.index.min()]]
        # 从候选者中选择上煤层（选择最上面的，即行索引最大的）
        upper_coal_row = upper_coal_candidates.loc[[upper_coal_candidates.index.max()]]

        # 获取煤层在文件中的行索引
        bottom_coal_index = bottom_coal_row.index[0]
        upper_coal_index = upper_coal_row.index[0]

        # 检查煤层顺序：上煤层的索引必须大于开采煤层
        if upper_coal_index <= bottom_coal_index:
            return {"error": f"选择错误: 上煤层({upper_coal_name})必须在开采煤层({bottom_coal_name})之上，请检查文件中煤层的位置。当前：开采煤层在行{bottom_coal_index}，上煤层在行{upper_coal_index}"}

        bottom_coal = bottom_coal_row.iloc[0]
        upper_coal = upper_coal_row.iloc[0]

        # 获取开采煤层厚度M
        mining_coal_thickness_M = float(bottom_coal['厚度']) if pd.notna(bottom_coal['厚度']) else 0
        if mining_coal_thickness_M <= 0:
            return {"error": "开采煤层厚度数据无效"}

        # 提取中间岩层
        # 在从下到上的文件中，上煤层在下面，开采煤层在上面
        # 中间岩层位于它们之���
        middle_layers = df.loc[upper_coal_index + 1 : bottom_coal_index - 1]

        if middle_layers.empty:
            return {"error": f"选择的两煤层之间无中间岩层。上煤层位置: {upper_coal_index}, 开采煤层位置: {bottom_coal_index}"}

        # 构建中间岩层数据列表
        intermediate_layers = []
        for idx, row in middle_layers.iterrows():
            thickness = float(row['厚度']) if pd.notna(row['厚度']) else 0
            if thickness <= 0:
                continue

            # 获取抗拉强度Ri
            tensile_strength = float(row['抗拉强度']) if pd.notna(row['抗拉强度']) else 3.0

            # 获取弹性模量（可以用来估算碎胀系数）
            elastic_modulus = float(row['弹性模量']) if pd.notna(row['弹性_modulus']) else 10.0

            # 根据弹性模量估算碎胀系数Kpi
            # 弹性模量越大，岩石越坚硬，碎胀系数越小
            bulking_factor = max(1.0, 1.5 - elastic_modulus / 50.0)  # 简化估算

            intermediate_layers.append({
                'name': str(row['名称']),
                'thickness': thickness,
                'tensile_strength': tensile_strength,
                'elastic_modulus': elastic_modulus,
                'bulking_factor': bulking_factor,
                'sequence': int(row['序号']) if pd.notna(row['序号']) else 0
            })

        if not intermediate_layers:
            return {"error": "无有效的中间岩层数据"}

        # 计算可行度
        analyzer = UpwardMiningFeasibility(lamda=lamda, C=C)
        omega, khd_value = analyzer.calculate_feasibility_from_data(
            mining_coal_thickness=mining_coal_thickness_M,
            intermediate_layers=intermediate_layers
        )

        evaluation = analyzer.evaluate_feasibility(omega)


        # 计算统计信息
        total_thickness_H = sum(layer['thickness'] for layer in intermediate_layers)
        total_thickness_D = total_thickness_H  # D和H相等
        avg_tensile = sum(layer['tensile_strength'] for layer in intermediate_layers) / len(intermediate_layers)
        avg_elastic = sum(layer['elastic_modulus'] for layer in intermediate_layers) / len(intermediate_layers)
        avg_bulking = sum(layer['bulking_factor'] for layer in intermediate_layers) / len(intermediate_layers)

        return {
            "filename": csv_file_path,
            "bottom_coal": bottom_coal['名称'],
            "target_coal": upper_coal['名称'],
            "mining_coal_thickness_M": round(mining_coal_thickness_M, 2),
            "middle_layer_count": len(intermediate_layers),
            "total_thickness_H": round(total_thickness_H, 2),
            "total_thickness_D": round(total_thickness_D, 2),
            "avg_tensile_strength": round(avg_tensile, 2),
            "avg_elastic_modulus": round(avg_elastic, 2),
            "avg_bulking_factor": round(avg_bulking, 3),
            "lambda": lamda,
            "C": C,
            "khd_value": khd_value,
            "feasibility_omega": evaluation['feasibility_degree'],
            "feasibility_level": evaluation['level'],
            "description": evaluation['description'],
            "layer_details": intermediate_layers
        }

    except Exception as e:
        return {"error": f"处理文件 {csv_file_path} 时出错: {str(e)}"}


def batch_process_borehole_files(file_paths: List[str], bottom_coal_name: str, upper_coal_name: str,
                                 lamda: float = 4.95, C: float = -0.84) -> Dict[str, Any]:
    """
    批量处理钻孔文件，计算上行开采可行度

    Args:
        file_paths: 钻孔CSV文件路径列表
        bottom_coal_name: 开采煤层名称
        upper_coal_name: 上煤层名称
        lamda: 影响因子λ
        C: 地质常数C

    Returns:
        批量处理结果
    """
    results = []
    errors = []

    for file_path in file_paths:
        result = process_borehole_csv_for_feasibility(file_path, bottom_coal_name, upper_coal_name, lamda, C)
        results.append(result)

        if "error" in result:
            errors.append({
                "file": file_path,
                "error": result["error"]
            })

    # 统计信息
    successful_results = [r for r in results if "error" not in r]
    feasibility_values = [r["feasibility_omega"] for r in successful_results if "feasibility_omega" in r]

    # 计算可行性等级分布
    level_counts = {}
    for result in successful_results:
        level = result.get("feasibility_level", "")
        if "I级" in level:
            level_counts["I级(不可行)"] = level_counts.get("I级(不可行)", 0) + 1
        elif "II级" in level:
            level_counts["II级(困难)"] = level_counts.get("II级(困难)", 0) + 1
        elif "III级" in level:
            level_counts["III级(可行)"] = level_counts.get("III级(可行)", 0) + 1
        elif "IV级" in level:
            level_counts["IV级(良好)"] = level_counts.get("IV级(良好)", 0) + 1
        elif "V级" in level:
            level_counts["V级(优良)"] = level_counts.get("V级(优良)", 0) + 1

    return {
        "total_files": len(file_paths),
        "successful_files": len(successful_results),
        "error_files": len(errors),
        "errors": errors,
        "feasibility_values": feasibility_values,
        "level_counts": level_counts,
        "results": results,
        "avg_feasibility": sum(feasibility_values) / len(feasibility_values) if feasibility_values else 0,
        "max_feasibility": max(feasibility_values) if feasibility_values else 0,
        "min_feasibility": min(feasibility_values) if feasibility_values else 0
    }


def auto_calibrate_coefficients(file_paths: List[str], bottom_coal_name: str, upper_coal_name: str,
                               initial_lamda: float = 4.95, initial_C: float = -0.84) -> Dict[str, Any]:
    """
    自动标定λ和C系数

    Args:
        file_paths: 钻孔CSV文件路径列表
        bottom_coal_name: 开采煤层名称
        upper_coal_name: 上煤层名称
        initial_lamda: 初始影响因子λ
        initial_C: 初始地质常数C

    Returns:
        标定结果
    """
    # 首先使用初始参数计算KHD值
    khd_values = []

    for file_path in file_paths:
        result = process_borehole_csv_for_feasibility(file_path, bottom_coal_name, upper_coal_name, initial_lamda, initial_C)
        if "error" not in result and "khd_value" in result:
            khd_values.append(result["khd_value"])

    if len(khd_values) < 2:
        return {
            "status": "error",
            "message": "至少需要两个或以上成功计算的钻孔才能进行标定。"
        }

    khd_min = min(khd_values)
    khd_max = max(khd_values)

    if khd_max <= khd_min:
        return {
            "status": "error",
            "message": f"计算出的KHD最大值({khd_max:.4f})不大于最小值({khd_min:.4f})，无法标定。可能是所有文件地质条件相似。"
        }

    try:
        new_lamda, new_C = UpwardMiningFeasibility.calculate_coefficients(khd_min, khd_max)

        return {
            "status": "success",
            "calibration_data": {
                "khd_range": f"{khd_min:.4f} ~ {khd_max:.4f}",
                "sample_count": len(khd_values),
                "initial_lambda": initial_lamda,
                "initial_C": initial_C,
                "calculated_lambda": new_lamda,
                "calculated_C": new_C
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"系数计算失败: {str(e)}"
        }