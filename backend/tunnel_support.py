"""
巷道支护计算模块
"""

import math
from typing import Any, Dict, List, Optional

import pandas as pd


class TunnelSupportCalculator:
    """按文档公式计算巷道支护参数。"""

    DEFAULT_CONSTANTS = {
        "Sn": 313.0,
        "Rm_anchor": 1860.0,
        "anchor_hole_radius_mm": 15.0,
        "anchor_resin_radius_mm": 12.5,
        "rod_diameter_mm": 20.0,
        "Rm_rod": 460.0,
        "rod_hole_radius_mm": 14.0,
        "rod_resin_radius_mm": 12.5,
        "c0": 3.0,
        "anchor_plate_thickness_m": 0.2,
        "anchor_exposed_length_m": 0.3,
        "rod_exposed_length_m": 0.1,
        "safety_K": 2.0,
        "m": 0.6,
        "n": 1.0,
    }

    def __init__(self, constants: Optional[Dict[str, float]] = None):
        self.constants = self._normalize_constants(constants or {})

    @classmethod
    def _normalize_constants(cls, constants: Dict[str, float]) -> Dict[str, float]:
        merged = {**cls.DEFAULT_CONSTANTS, **constants}

        if "R_mm" in constants and "anchor_hole_radius_mm" not in constants:
            merged["anchor_hole_radius_mm"] = float(constants["R_mm"])
        if "D_mm" in constants and "rod_diameter_mm" not in constants:
            merged["rod_diameter_mm"] = float(constants["D_mm"])

        return merged

    @staticmethod
    def compute_plastic_zone_radius(
        width_m: float,
        height_m: float,
        gamma_kN_m3: float,
        depth_m: float,
        cohesion_MPa: float,
        phi_deg: float,
        stress_factor: float,
    ) -> float:
        phi_rad = math.radians(phi_deg)
        sin_phi = math.sin(phi_rad)
        if math.isclose(sin_phi, 0.0):
            raise ValueError("内摩擦角不能为 0 度")

        cot_phi = 1.0 / math.tan(phi_rad)
        equivalent_radius = math.sqrt((width_m**2 + height_m**2) / 4.0)
        gamma_depth_MPa = gamma_kN_m3 * depth_m / 1000.0
        stress_term = ((stress_factor * gamma_depth_MPa + cohesion_MPa * cot_phi) * (1.0 - sin_phi)) / (
            cohesion_MPa * cot_phi
        )
        exponent = (1.0 - sin_phi) / (2.0 * sin_phi)
        return equivalent_radius * (stress_term**exponent)

    @staticmethod
    def compute_loosening_zones(
        plastic_radius_m: float,
        width_m: float,
        height_m: float,
        phi_deg: float,
        f_top: float,
    ) -> Dict[str, float]:
        phi_rad = math.radians(phi_deg)
        hat = (width_m / 2.0 + height_m * math.tan(math.radians(45.0) - phi_rad / 2.0)) / f_top
        hct = plastic_radius_m - height_m / 2.0
        hcs = plastic_radius_m - width_m / 2.0
        lb = max(hct, hat)
        return {"hct": hct, "hcs": hcs, "hat": hat, "Lb": lb}

    @staticmethod
    def compute_anchor_design_capacity(Sn_mm2: float, Rm_MPa: float, m: float, n: float) -> float:
        return m * n * Sn_mm2 * Rm_MPa / 1000.0

    @staticmethod
    def compute_round_bar_design_capacity(diameter_mm: float, yield_strength_MPa: float) -> float:
        return math.pi * diameter_mm**2 * yield_strength_MPa / 4000.0

    @staticmethod
    def compute_member_diameter(load_kN: float, strength_MPa: float) -> float:
        return 35.52 * math.sqrt(load_kN / strength_MPa)

    @staticmethod
    def compute_bond_length(load_kN: float, hole_radius_mm: float, c0_MPa: float) -> float:
        load_N = load_kN * 1000.0
        hole_radius_m = hole_radius_mm / 1000.0
        c0_Pa = c0_MPa * 1e6
        return load_N / (2.0 * math.pi * hole_radius_m * c0_Pa)

    @staticmethod
    def compute_resin_length(
        bond_length_m: float,
        hole_radius_mm: float,
        member_diameter_mm: float,
        resin_radius_mm: float,
    ) -> float:
        numerator = hole_radius_mm**2 - (member_diameter_mm**2) / 4.0
        denominator = resin_radius_mm**2
        if denominator <= 0:
            raise ValueError("树脂半径必须大于 0")
        if numerator <= 0:
            raise ValueError("钻孔半径与杆体直径不匹配，无法计算树脂长度")
        return bond_length_m * numerator / denominator

    @staticmethod
    def compute_spacing_area(load_kN: float, safety_K: float, support_length_m: float, gamma_kN_m3: float) -> float:
        if support_length_m <= 0:
            raise ValueError("支护长度必须大于 0")
        return load_kN / (safety_K * support_length_m * gamma_kN_m3)

    def calculate_complete(self, params: Dict[str, float]) -> Dict[str, Any]:
        width = float(params["B"])
        height = float(params["H"])
        depth = float(params["depth"])
        gamma = float(params["gamma"])
        cohesion = float(params["C"])
        phi = float(params["phi"])
        stress_factor = float(params["K"])
        f_top = float(params.get("f_top", 2.0))

        c0 = float(self.constants["c0"])
        safety_K = float(self.constants["safety_K"])

        plastic_radius = self.compute_plastic_zone_radius(width, height, gamma, depth, cohesion, phi, stress_factor)
        loosening = self.compute_loosening_zones(plastic_radius, width, height, phi, f_top)

        anchor_nt = self.compute_anchor_design_capacity(
            float(self.constants["Sn"]),
            float(self.constants["Rm_anchor"]),
            float(self.constants["m"]),
            float(self.constants["n"]),
        )
        anchor_diameter = self.compute_member_diameter(anchor_nt, float(self.constants["Rm_anchor"]))
        anchor_lm = self.compute_bond_length(
            anchor_nt,
            float(self.constants["anchor_hole_radius_mm"]),
            c0,
        )
        anchor_l_resin = self.compute_resin_length(
            anchor_lm,
            float(self.constants["anchor_hole_radius_mm"]),
            anchor_diameter,
            float(self.constants["anchor_resin_radius_mm"]),
        )
        anchor_total_length = (
            anchor_lm
            + loosening["Lb"]
            + float(self.constants["anchor_plate_thickness_m"])
            + float(self.constants["anchor_exposed_length_m"])
        )
        anchor_plate_capacity_min = 1.5 * anchor_nt

        rod_nt = self.compute_round_bar_design_capacity(
            float(self.constants["rod_diameter_mm"]),
            float(self.constants["Rm_rod"]),
        )
        rod_l3 = self.compute_bond_length(
            rod_nt,
            float(self.constants["rod_hole_radius_mm"]),
            c0,
        )
        rod_l_resin = self.compute_resin_length(
            rod_l3,
            float(self.constants["rod_hole_radius_mm"]),
            float(self.constants["rod_diameter_mm"]),
            float(self.constants["rod_resin_radius_mm"]),
        )
        rod_l_top = float(self.constants["rod_exposed_length_m"]) + loosening["hat"] + rod_l3
        rod_l_side = float(self.constants["rod_exposed_length_m"]) + loosening["hcs"] + rod_l3
        rod_plate_capacity_min = 1.3 * rod_nt

        anchor_spacing = self.compute_spacing_area(anchor_nt, safety_K, anchor_total_length, gamma)
        rod_top_spacing = self.compute_spacing_area(rod_nt, safety_K, rod_l_top, gamma)
        rod_side_spacing = self.compute_spacing_area(rod_nt, safety_K, rod_l_side, gamma)

        return {
            "input": {
                "B": width,
                "H": height,
                "depth": depth,
                "gamma": gamma,
                "C": cohesion,
                "phi": phi,
                "K": stress_factor,
                "f_top": f_top,
            },
            "basic": {
                "R": round(plastic_radius, 3),
                "hct": round(loosening["hct"], 3),
                "hcs": round(loosening["hcs"], 3),
                "hat": round(loosening["hat"], 3),
                "Lb": round(loosening["Lb"], 3),
            },
            "anchor": {
                "Nt": round(anchor_nt, 3),
                "diameter": round(anchor_diameter, 3),
                "Lm": round(anchor_lm, 3),
                "L_resin": round(anchor_l_resin, 3),
                "L_total": round(anchor_total_length, 3),
                "plate_capacity_min": round(anchor_plate_capacity_min, 3),
                "spacing_area": round(anchor_spacing, 3),
            },
            "rod": {
                "Nt": round(rod_nt, 3),
                "diameter": round(float(self.constants["rod_diameter_mm"]), 3),
                "La": round(rod_l3, 3),
                "L3": round(rod_l3, 3),
                "L_resin": round(rod_l_resin, 3),
                "L_top": round(rod_l_top, 3),
                "L_side": round(rod_l_side, 3),
                "plate_capacity_min": round(rod_plate_capacity_min, 3),
                "spacing_area_top": round(rod_top_spacing, 3),
                "spacing_area_side": round(rod_side_spacing, 3),
            },
        }


def batch_calculate_tunnel_support(
    data: List[Dict[str, float]],
    constants: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    calculator = TunnelSupportCalculator(constants)
    rows: List[Dict[str, Any]] = []

    for params in data:
        try:
            result = calculator.calculate_complete(params)
        except Exception as exc:
            print(f"计算失败: {exc}")
            continue

        row = {
            "B": result["input"]["B"],
            "H": result["input"]["H"],
            "埋深": result["input"]["depth"],
            "容重": result["input"]["gamma"],
            "粘聚力": result["input"]["C"],
            "内摩擦角": result["input"]["phi"],
            "应力集中系数K": result["input"]["K"],
            "f_top": result["input"]["f_top"],
            "R(m)": result["basic"]["R"],
            "hct(m)": result["basic"]["hct"],
            "hcs(m)": result["basic"]["hcs"],
            "hat(m)": result["basic"]["hat"],
            "Lb(m)": result["basic"]["Lb"],
            "Nt_anchor(kN)": result["anchor"]["Nt"],
            "diameter_anchor(mm)": result["anchor"]["diameter"],
            "d_anchor(mm)": result["anchor"]["diameter"],
            "Lm_anchor(m)": result["anchor"]["Lm"],
            "L_resin_anchor(m)": result["anchor"]["L_resin"],
            "L_total_anchor(m)": result["anchor"]["L_total"],
            "Tb_anchor(kN)": result["anchor"]["plate_capacity_min"],
            "a*b_anchor(m2)": result["anchor"]["spacing_area"],
            "Nt_rod(kN)": result["rod"]["Nt"],
            "diameter_rod(mm)": result["rod"]["diameter"],
            "d_rod(mm)": result["rod"]["diameter"],
            "L3_rod(m)": result["rod"]["L3"],
            "La_rod(m)": result["rod"]["La"],
            "L_resin_rod(m)": result["rod"]["L_resin"],
            "L_top(m)": result["rod"]["L_top"],
            "L_side(m)": result["rod"]["L_side"],
            "Q_tray_rod(kN)": result["rod"]["plate_capacity_min"],
            "a*b_top(m2)": result["rod"]["spacing_area_top"],
            "a*b_side(m2)": result["rod"]["spacing_area_side"],
        }
        rows.append(row)

    return pd.DataFrame(rows)
