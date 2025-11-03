"""
tunnel_support.py
巷道支护计算模块
基于《巷道支护理论公式.docx》实现
"""

import math
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


class TunnelSupportCalculator:
    """巷道支护计算器"""
    
    # 默认常量（依据文档）
    DEFAULT_CONSTANTS = {
        'Sn': 313,  # mm² - 锚索截面积
        'Rm_anchor': 1860,  # MPa - 锚索抗拉强度
        'Rm_rod': 460,  # MPa - 锚杆抗拉强度
        'Q_anchor': 350,  # kN - 锚索设计荷载
        'Q_rod': 105,  # kN - 锚杆设计荷载
        'c0': 3.0,  # MPa - 树脂锚固力
        'tau_rod': 2.0,  # MPa - 锚杆锚固力
        'R_mm': 15,  # mm - 锚索半径
        'D_mm': 30,  # mm - 锚杆直径
        'safety_K': 2.0,  # 安全系数
        'm': 0.6,  # 锚杆(索)工作状态系数
        'n': 1,  # 根数
    }
    
    def __init__(self, constants: Optional[Dict[str, float]] = None):
        """
        初始化计算器
        
        Args:
            constants: 自定义常量字典，未提供则使用默认值
        """
        self.constants = {**self.DEFAULT_CONSTANTS, **(constants or {})}
    
    @staticmethod
    def compute_R_equivalent(a_half: float, b_half: float, gamma: float, 
                            depth_H: float, C_MPa: float, phi_deg: float, K: float) -> float:
        """
        式(5.1)：计算塑性区半径 R (m)
        
        R = r * [((K * γ * H + C * cotφ) * (1 - sinφ)) / (C * cotφ)]^((1 - sinφ) / (2 * sinφ))
        
        等效圆半径 r = √(a² + b²)
        
        ⚠️ 单位统一：gamma × H 需要从 kPa 转为 MPa
        
        Args:
            a_half: 巷道半宽 (m)
            b_half: 巷道半高 (m)
            gamma: 容重 (kN/m³)
            depth_H: 埋深 (m)
            C_MPa: 粘聚力 (MPa)
            phi_deg: 内摩擦角 (度)
            K: 应力集中系数
            
        Returns:
            塑性区半径 R (m)
        """
        # 🔧 修正：等效圆半径为 √(a² + b²)
        r_eq = math.sqrt(a_half**2 + b_half**2)
        
        phi = math.radians(phi_deg)
        sin_phi = math.sin(phi)
        
        if sin_phi == 0:
            raise ValueError("内摩擦角不能为0度")
        
        cot_phi = 1 / math.tan(phi)
        
        # 🔧 修复：将 gamma * depth_H 从 kPa 转换为 MPa
        gamma_H_MPa = gamma * depth_H / 1000.0  # kN/m² = kPa → MPa
        
        # 现在单位统一为 MPa
        numerator = (K * gamma_H_MPa + C_MPa * cot_phi) * (1 - sin_phi)
        denominator = C_MPa * cot_phi
        exponent = (1 - sin_phi) / (2 * sin_phi)
        
        R = r_eq * (numerator / denominator) ** exponent
        return R
    
    @staticmethod
    def compute_loosening_zones(R: float, a_half: float, b_half: float, B: float, H: float, 
                               phi_deg: float, f_top: float) -> Dict[str, float]:
        """
        式(5.2)-(5.4)：计算松动圈和压力拱高度
        
        Args:
            R: 塑性区半径 (m)
            a_half: 巷道半宽 (m)
            b_half: 巷道半高 (m)
            B: 巷道宽度 (m)
            H: 巷道高度 (m)
            phi_deg: 内摩擦角 (度)
            f_top: 顶板普氏系数
            
        Returns:
            包含 hct(顶板松动圈), hcs(两帮松动圈), hat(压力拱高度) 的字典
        """
        phi_rad = math.radians(phi_deg)
        
        # (5.4) 压力拱高度：hat = (B/2 + H * tan(45° - φ/2)) / f_top
        hat = (B / 2 + H * math.tan(math.radians(45) - phi_rad / 2)) / f_top
        
        return {
            'hct': R - b_half,  # (5.2) 顶板松动圈
            'hcs': R - a_half,  # (5.3) 两帮松动圈
            'hat': hat,         # (5.4) 压力拱高度
        }
    
    def compute_design_capacity(self, anchor_type: str = 'anchor') -> float:
        """
        式(5.6)/(5.11)：计算设计承载力 Nt = m * n * Sn * Rm
        
        Args:
            anchor_type: 'anchor' (锚索) 或 'rod' (锚杆)
            
        Returns:
            设计承载力 Nt (kN)
        """
        m = self.constants['m']
        n = self.constants['n']
        Sn = self.constants['Sn']
        
        if anchor_type == 'anchor':
            Rm = self.constants['Rm_anchor']
        else:
            Rm = self.constants['Rm_rod']
        
        Nt_N = m * n * Sn * Rm  # N
        return Nt_N / 1000.0  # 转 kN
    
    @staticmethod
    def compute_diameter(Q_kN: float, delta_MPa: float) -> float:
        """
        式(5.7)/(5.12)：根据荷载和强度计算直径
        
        d = 35.52 * sqrt(Q / δ)
        
        Args:
            Q_kN: 设计荷载 (kN)
            delta_MPa: 材料强度 (MPa)
            
        Returns:
            直径 (mm)
        """
        return 35.52 * math.sqrt(Q_kN / delta_MPa)
    
    @staticmethod
    def compute_anchor_resin_length(Q_kN: float, R_mm: float, c0_MPa: float) -> float:
        """
        式(5.8)：计算锚索锚固长度
        
        Lm = Q / (2 * π * R * c0)
        
        Args:
            Q_kN: 设计荷载 (kN)
            R_mm: 锚索半径 (mm)
            c0_MPa: 树脂锚固力 (MPa)
            
        Returns:
            锚固长度 Lm (m)
        """
        Q_N = Q_kN * 1000.0
        R_m = R_mm / 1000.0
        c0_Pa = c0_MPa * 1e6
        
        Lm = Q_N / (2.0 * math.pi * R_m * c0_Pa)
        return Lm
    
    @staticmethod
    def compute_total_anchor_length(Lm: float, Lb: float, 
                                    plate_thickness: float = 0.2, 
                                    exposed: float = 0.3) -> float:
        """
        式(5.10)：计算锚索总长度
        
        L = Lm + Lb + 托盘厚度 + 外露长度
        
        Args:
            Lm: 锚固长度 (m)
            Lb: 锚固深度 (m)
            plate_thickness: 托盘厚度 (m)，默认0.2
            exposed: 外露长度 (m)，默认0.3
            
        Returns:
            总长度 L (m)
        """
        return Lm + Lb + plate_thickness + exposed
    
    @staticmethod
    def compute_rod_anchor_length(N_kN: float, D_mm: float, tau_MPa: float) -> float:
        """
        式(5.13)：计算锚杆锚固长度
        
        La = N / (π * D * τ)
        
        Args:
            N_kN: 设计承载力 (kN)
            D_mm: 锚杆直径 (mm)
            tau_MPa: 锚固力 (MPa)
            
        Returns:
            锚固长度 La (m)
        """
        N_N = N_kN * 1000.0
        D_m = D_mm / 1000.0
        tau_Pa = tau_MPa * 1e6
        
        return N_N / (math.pi * D_m * tau_Pa)
    
    @staticmethod
    def compute_rod_length(L1: float = 0.1, L2: float = 0.0, L3: float = 0.67) -> float:
        """
        式(5.15)/(5.16)：计算锚杆长度
        
        L = L1 + L2 + L3
        
        Args:
            L1: 托盘厚度等 (m)
            L2: 松动圈或压力拱高度 (m)
            L3: 锚固长度 (m)
            
        Returns:
            锚杆总长度 (m)
        """
        return L1 + L2 + L3
    
    @staticmethod
    def compute_spacing_area(Nt_kN: float, safety_K: float, 
                            L_m: float, r_kN_m3: float) -> float:
        """
        式(5.17)：计算间排距面积
        
        a*b = Nt / (K * L * r)
        
        Args:
            Nt_kN: 设计承载力 (kN)
            safety_K: 安全系数
            L_m: 锚杆(索)长度 (m)
            r_kN_m3: 容重 (kN/m³)
            
        Returns:
            间排距面积 a*b (m²)
        """
        return Nt_kN / (safety_K * L_m * r_kN_m3)
    
    def calculate_complete(self, params: Dict[str, float]) -> Dict[str, Any]:
        """
        完整计算巷道支护参数
        
        Args:
            params: 输入参数字典，包含:
                - B: 巷道宽度 (m)
                - H: 巷道高度 (m)
                - K: 应力集中系数
                - depth: 埋深 (m)
                - gamma: 容重 (kN/m³)
                - C: 粘聚力 (MPa)
                - phi: 内摩擦角 (度)
                - f_top: 顶板普氏系数 (默认为2.0)
                
        Returns:
            完整的计算结果字典
        """
        # 提取输入参数
        B = params['B']
        H = params['H']
        a_half = B / 2
        b_half = H / 2
        gamma = params['gamma']
        depth = params['depth']
        C = params['C']
        phi = params['phi']
        K = params['K']
        f_top = params.get('f_top', 2.0)  # 默认值为2.0
        
        # (5.1) 计算等效圆塑性区半径
        R = self.compute_R_equivalent(a_half, b_half, gamma, depth, C, phi, K)
        
        # (5.2)-(5.4) 计算松动圈和压力拱
        loosening = self.compute_loosening_zones(R, a_half, b_half, B, H, phi, f_top)
        hct = loosening['hct']
        hcs = loosening['hcs']
        hat = loosening['hat']
        
        # 锚索计算
        Nt_anchor = self.compute_design_capacity('anchor')
        d_anchor = self.compute_diameter(
            self.constants['Q_anchor'], 
            self.constants['Rm_anchor']
        )
        Lm_anchor = self.compute_anchor_resin_length(
            self.constants['Q_anchor'],
            self.constants['R_mm'],
            self.constants['c0']
        )
        Lb = max(hct, hat)
        L_total_anchor = self.compute_total_anchor_length(Lm_anchor, Lb)
        
        # 锚杆计算
        Nt_rod = self.compute_design_capacity('rod')
        d_rod = self.compute_diameter(
            self.constants['Q_rod'],
            375  # 锚杆设计强度
        )
        La_rod = self.compute_rod_anchor_length(
            self.constants['Q_rod'],
            self.constants['D_mm'],
            self.constants['tau_rod']
        )
        
        # 锚杆长度计算
        L_top = self.compute_rod_length(L1=0.1, L2=hat, L3=0.67)
        L_side = self.compute_rod_length(L1=0.1, L2=hcs, L3=0.67)
        
        # 间排距计算
        safety_K = self.constants['safety_K']
        ab_anchor = self.compute_spacing_area(Nt_anchor, safety_K, L_total_anchor, gamma)
        ab_top = self.compute_spacing_area(Nt_rod, safety_K, L_top, gamma)
        ab_side = self.compute_spacing_area(Nt_rod, safety_K, L_side, gamma)
        
        return {
            # 输入参数
            'input': {
                'B': B,
                'H': H,
                'depth': depth,
                'gamma': gamma,
                'C': C,
                'phi': phi,
                'K': K
            },
            # 基础计算结果
            'basic': {
                'R': round(R, 3),
                'hct': round(hct, 3),
                'hcs': round(hcs, 3),
                'hat': round(hat, 3)
            },
            # 锚索设计
            'anchor': {
                'Nt': round(Nt_anchor, 2),
                'diameter': round(d_anchor, 2),
                'Lm': round(Lm_anchor, 3),
                'L_total': round(L_total_anchor, 3),
                'spacing_area': round(ab_anchor, 3)
            },
            # 锚杆设计
            'rod': {
                'Nt': round(Nt_rod, 2),
                'diameter': round(d_rod, 2),
                'La': round(La_rod, 3),
                'L_top': round(L_top, 3),
                'L_side': round(L_side, 3),
                'spacing_area_top': round(ab_top, 3),
                'spacing_area_side': round(ab_side, 3)
            }
        }


def batch_calculate_tunnel_support(data: List[Dict[str, float]], 
                                   constants: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """
    批量计算巷道支护参数
    
    Args:
        data: 输入参数列表
        constants: 自定义常量
        
    Returns:
        包含所有计算结果的DataFrame
    """
    calculator = TunnelSupportCalculator(constants)
    results = []
    
    for params in data:
        try:
            result = calculator.calculate_complete(params)
            
            # 展平结果
            flat_result = {
                'B': result['input']['B'],
                'H': result['input']['H'],
                '埋深': result['input']['depth'],
                '容重': result['input']['gamma'],
                '粘聚力': result['input']['C'],
                '内摩擦角': result['input']['phi'],
                '应力集中系数K': result['input']['K'],
                'R(m)': result['basic']['R'],
                'hct(m)': result['basic']['hct'],
                'hcs(m)': result['basic']['hcs'],
                'hat(m)': result['basic']['hat'],
                'Nt_anchor(kN)': result['anchor']['Nt'],
                'd_anchor(mm)': result['anchor']['diameter'],
                'Lm_anchor(m)': result['anchor']['Lm'],
                'L_total_anchor(m)': result['anchor']['L_total'],
                'a*b_anchor(m2)': result['anchor']['spacing_area'],
                'Nt_rod(kN)': result['rod']['Nt'],
                'd_rod(mm)': result['rod']['diameter'],
                'La_rod(m)': result['rod']['La'],
                'L_top(m)': result['rod']['L_top'],
                'L_side(m)': result['rod']['L_side'],
                'a*b_top(m2)': result['rod']['spacing_area_top'],
                'a*b_side(m2)': result['rod']['spacing_area_side']
            }
            results.append(flat_result)
            
        except Exception as e:
            # 记录错误但继续处理
            print(f"计算失败: {e}")
            continue
    
    return pd.DataFrame(results)
