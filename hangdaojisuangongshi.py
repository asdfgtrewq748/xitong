"""
support_calc_all.py
巷道支护计算自动化程序
以《巷道支护理论公式.docx》为标准。
(5.1) 使用您提供的精确公式；
(5.4) 临时采用经验式 hat = R - a；
其余公式均严格按文档实现。

依赖: pip install pandas numpy openpyxl
"""

import math
import pandas as pd
import os

# -----------------------------
# (5.1) 等效圆塑性区半径 R
# -----------------------------
def compute_R_equivalent(a_half, b_half, gamma, depth_H, C_MPa, phi_deg, K):
    """
    式(5.1)：等效圆塑性区半径 R (m)
    R = r * [ ((K * γ * H + C * cotφ) * (1 - sinφ)) / (C * cotφ) ] ** ((1 - sinφ) / (2 * sinφ))
    """
    r_eq = a_half  # 等效圆半径取巷道半宽
    phi = math.radians(phi_deg)
    sin_phi = math.sin(phi)
    cot_phi = 1 / math.tan(phi)
    numerator = (K * gamma * depth_H + C_MPa * cot_phi) * (1 - sin_phi)
    denominator = C_MPa * cot_phi
    exponent = (1 - sin_phi) / (2 * sin_phi)
    R = r_eq * (numerator / denominator) ** exponent
    return R


# -----------------------------
# (5.2) 顶板松动圈 hct = R - b
# (5.3) 帮部松动圈 hcs = R - a
# (5.4) 临时普氏压力拱高度 hat = R - a
# -----------------------------
def compute_hct(R, b_half):
    return R - b_half

def compute_hcs(R, a_half):
    return R - a_half

def compute_hat_pressure_arch(R, a_half):
    return R - a_half  # 临时经验式，等待替换为正式(5.4)公式


# -----------------------------
# (5.6)/(5.11) 设计承载力 Nt = m n Sn Rm
# -----------------------------
def compute_Nt(m=0.6, n=1, Sn_mm2=313, Rm_MPa=1860):
    Nt_N = m * n * Sn_mm2 * Rm_MPa  # N
    return Nt_N / 1000.0  # 转 kN


# -----------------------------
# (5.7)/(5.12) 直径计算
# -----------------------------
def diameter_from_Q_delta(Q_kN, delta_MPa):
    return 35.52 * math.sqrt(Q_kN / delta_MPa)


# -----------------------------
# (5.8) 锚索锚固长度
# -----------------------------
def anchor_resin_length_Lm(Q_kN, R_mm, c0_MPa):
    Q_N = Q_kN * 1000.0
    R_m = R_mm / 1000.0
    c0_Pa = c0_MPa * 1e6
    Lm = Q_N / (math.pi * R_m * c0_Pa)
    return Lm


# -----------------------------
# (5.10) 锚索总长度 L = Lm + Lb + 0.2 + 0.3
# -----------------------------
def total_anchor_length(Lm, Lb, plate_thickness=0.2, exposed=0.3):
    return Lm + Lb + plate_thickness + exposed


# -----------------------------
# (5.13) 锚杆锚固长度
# -----------------------------
def anchor_length_La(N_kN, D_mm, tau_MPa):
    N_N = N_kN * 1000.0
    D_m = D_mm / 1000.0
    tau_Pa = tau_MPa * 1e6
    return N_N / (math.pi * D_m * tau_Pa)


# -----------------------------
# (5.15)/(5.16) 锚杆长度
# -----------------------------
def roof_bolt_length(L1=0.1, L2=0.0, L3=0.67):
    return L1 + L2 + L3


# -----------------------------
# (5.17) 间排距 a*b = Nt / (K * L * r)
# -----------------------------
def spacing_area_ab(Nt_kN, safety_K, L_m, r_kN_m3):
    return Nt_kN / (safety_K * L_m * r_kN_m3)


# -----------------------------
# Excel批处理主程序
# -----------------------------
def process_excel(input_excel="巷道支护计算8.21.xlsx",
                  output_excel="巷道支护计算结果_from_docx.xlsx"):
    df = pd.read_excel(input_excel)
    required = ['B', 'H', '应力集中系数K', '埋深', '容重', '粘聚力', 'f顶', 'w', '内摩擦角']
    for c in required:
        if c not in df.columns:
            raise KeyError(f"缺少列: {c}")

    # 常量（依据文档）
    Sn = 313  # mm²
    Rm_anchor = 1860
    Rm_rod = 460
    Q_anchor = 350
    Q_rod = 105
    c0 = 3.0
    tau_rod = 2.0
    R_mm = 15
    D_mm = 30
    safety_K = 2.0

    results = []
    for _, row in df.iterrows():
        B = row['B']; H = row['H']
        a = B / 2; b = H / 2
        gamma = row['容重']; depth = row['埋深']
        C = row['粘聚力']; phi = row['内摩擦角']
        K = row['应力集中系数K']

        # (5.1)
        R = compute_R_equivalent(a, b, gamma, depth, C, phi, K)

        # (5.2)-(5.4)
        hct = compute_hct(R, b)
        hcs = compute_hcs(R, a)
        hat = compute_hat_pressure_arch(R, a)

        # (5.6)
        Nt_anchor = compute_Nt(0.6, 1, Sn, Rm_anchor)
        Nt_rod = compute_Nt(0.6, 1, Sn, Rm_rod)

        # (5.7)/(5.12)
        d_anchor = diameter_from_Q_delta(Q_anchor, Rm_anchor)
        d_rod = diameter_from_Q_delta(Q_rod, 375)

        # (5.8)
        Lm_anchor = anchor_resin_length_Lm(Q_anchor, R_mm, c0)

        # (5.10)
        Lb = max(hct, hat)
        L_total_anchor = total_anchor_length(Lm_anchor, Lb)

        # (5.13)
        La_rod = anchor_length_La(Q_rod, D_mm, tau_rod)

        # (5.15)/(5.16)
        L_top = roof_bolt_length(L1=0.1, L2=hat, L3=0.67)
        L_side = roof_bolt_length(L1=0.1, L2=hcs, L3=0.67)

        # (5.17)
        r_val = gamma
        ab_anchor = spacing_area_ab(Nt_anchor, safety_K, L_total_anchor, r_val)
        ab_top = spacing_area_ab(Nt_rod, safety_K, L_top, r_val)
        ab_side = spacing_area_ab(Nt_rod, safety_K, L_side, r_val)

        results.append({
            "R(m)": R,
            "hct(m)": hct,
            "hcs(m)": hcs,
            "hat(m)": hat,
            "Nt_anchor(kN)": Nt_anchor,
            "d_anchor(mm)": d_anchor,
            "Lm_anchor(m)": Lm_anchor,
            "L_total_anchor(m)": L_total_anchor,
            "Nt_rod(kN)": Nt_rod,
            "d_rod(mm)": d_rod,
            "La_rod(m)": La_rod,
            "L_top(m)": L_top,
            "L_side(m)": L_side,
            "a*b_anchor(m2)": ab_anchor,
            "a*b_top(m2)": ab_top,
            "a*b_side(m2)": ab_side
        })

    result_df = pd.concat([df, pd.DataFrame(results)], axis=1)
    result_df.to_excel(output_excel, index=False)
    print(f"✅ 计算完成，结果已保存到: {os.path.abspath(output_excel)}")


if __name__ == "__main__":
    process_excel()
