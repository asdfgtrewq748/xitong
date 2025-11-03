#!/usr/bin/env python3
"""
debug_hat_specific.py
使用用户提供的具体参数调试 hat 计算
"""

import sys
sys.path.insert(0, 'd:\\xitong\\backend')

from tunnel_support import TunnelSupportCalculator
import math

print("=" * 80)
print("hat 计算问题调试 - 使用用户提供的参数")
print("=" * 80)

# 用户提供的参数
B = 4.8
H = 3.2
phi_deg = 32.47
f_top = 2.2

print("\n📋 用户提供的参数:")
print("-" * 80)
print(f"  B (巷道宽度)        = {B} m")
print(f"  H (巷道高度)        = {H} m")
print(f"  φ (内摩擦角)        = {phi_deg}°")
print(f"  f_top (顶板普氏系数) = {f_top}")
print()
print(f"  用户期望结果: hat = 1.889 m")
print(f"  程序计算结果: hat = 2.078 m (?)") 
print()

print("🔍 当前公式计算过程:")
print("=" * 80)
print("  公式: hat = (B/2 + H × tan(45° - φ/2)) / f_top")
print()

# 当前公式计算
phi_rad = math.radians(phi_deg)
angle_45_rad = math.radians(45)
angle_diff_rad = angle_45_rad - phi_rad / 2
angle_diff_deg = math.degrees(angle_diff_rad)

print("步骤 1: 计算角度")
print(f"  φ = {phi_deg}° = {phi_rad:.8f} rad")
print(f"  φ/2 = {phi_deg/2:.4f}° = {phi_rad/2:.8f} rad")
print(f"  45° - φ/2 = 45° - {phi_deg/2:.4f}° = {angle_diff_deg:.4f}°")
print()

tan_value = math.tan(angle_diff_rad)
print("步骤 2: 计算 tan 值")
print(f"  tan({angle_diff_deg:.4f}°) = {tan_value:.10f}")
print()

b_half = B / 2
print("步骤 3: 计算各部分")
print(f"  B/2 = {B}/2 = {b_half:.10f} m")

h_tan = H * tan_value
print(f"  H × tan(45° - φ/2) = {H} × {tan_value:.10f}")
print(f"                     = {h_tan:.10f} m")
print()

numerator = b_half + h_tan
print("步骤 4: 计算分子")
print(f"  分子 = B/2 + H × tan(45° - φ/2)")
print(f"       = {b_half:.10f} + {h_tan:.10f}")
print(f"       = {numerator:.10f} m")
print()

hat_current = numerator / f_top
print("步骤 5: 除以 f_top")
print(f"  hat = {numerator:.10f} / {f_top}")
print(f"      = {hat_current:.10f} m")
print(f"      ≈ {hat_current:.3f} m")
print()
print(f"  ❌ 当前计算结果: {hat_current:.3f} m")
print(f"  ✅ 用户期望结果: 1.889 m")
print(f"  📊 差异: {abs(hat_current - 1.889):.3f} m")
print()

print("=" * 80)
print("🔬 反推：如果期望 hat = 1.889 m，公式应该是什么？")
print("=" * 80)
print()

# 反推分析
expected_hat = 1.889

# 可能性1: 不除以2
print("可能性 1: 公式是 hat = (B + H × tan(45° - φ/2)) / f_top")
print("         (B 不除以 2)")
numerator_v1 = B + h_tan
hat_v1 = numerator_v1 / f_top
print(f"  分子 = B + H × tan(45° - φ/2)")
print(f"       = {B} + {h_tan:.6f} = {numerator_v1:.6f}")
print(f"  hat = {numerator_v1:.6f} / {f_top} = {hat_v1:.6f}")
if abs(hat_v1 - expected_hat) < 0.001:
    print(f"  ✅ 匹配！这可能是正确公式")
else:
    print(f"  ❌ 不匹配 (差异: {abs(hat_v1 - expected_hat):.3f})")
print()

# 可能性2: 不除以 f_top
print("可能性 2: 公式是 hat = B/2 + H × tan(45° - φ/2)")
print("         (不除以 f_top)")
hat_v2 = numerator
print(f"  hat = B/2 + H × tan(45° - φ/2)")
print(f"      = {numerator:.6f}")
if abs(hat_v2 - expected_hat) < 0.001:
    print(f"  ✅ 匹配！这可能是正确公式")
else:
    print(f"  ❌ 不匹配 (差异: {abs(hat_v2 - expected_hat):.3f})")
print()

# 可能性3: B + H，不除以 f_top
print("可能性 3: 公式是 hat = B + H × tan(45° - φ/2)")
print("         (B 不除以 2，且不除以 f_top)")
hat_v3 = B + h_tan
print(f"  hat = B + H × tan(45° - φ/2)")
print(f"      = {B} + {h_tan:.6f} = {hat_v3:.6f}")
if abs(hat_v3 - expected_hat) < 0.001:
    print(f"  ✅ 匹配！这可能是正确公式")
else:
    print(f"  ❌ 不匹配 (差异: {abs(hat_v3 - expected_hat):.3f})")
print()

# 可能性4: 45° - φ (不除以2)
print("可能性 4: 公式是 hat = (B/2 + H × tan(45° - φ)) / f_top")
print("         (φ 不除以 2)")
angle_diff_v4 = math.radians(45) - phi_rad  # φ 不除以2
tan_v4 = math.tan(angle_diff_v4)
h_tan_v4 = H * tan_v4
numerator_v4 = b_half + h_tan_v4
hat_v4 = numerator_v4 / f_top
print(f"  45° - φ = 45° - {phi_deg}° = {math.degrees(angle_diff_v4):.4f}°")
print(f"  tan({math.degrees(angle_diff_v4):.4f}°) = {tan_v4:.6f}")
print(f"  分子 = {b_half} + {H} × {tan_v4:.6f} = {numerator_v4:.6f}")
print(f"  hat = {numerator_v4:.6f} / {f_top} = {hat_v4:.6f}")
if abs(hat_v4 - expected_hat) < 0.001:
    print(f"  ✅ 匹配！这可能是正确公式")
else:
    print(f"  ❌ 不匹配 (差异: {abs(hat_v4 - expected_hat):.3f})")
print()

# 可能性5: 简单的 B/2 + H/2，然后除以某个系数
print("可能性 5: 公式是 hat = (B + H) / (2 × f_top)")
hat_v5 = (B + H) / (2 * f_top)
print(f"  hat = (B + H) / (2 × f_top)")
print(f"      = ({B} + {H}) / (2 × {f_top})")
print(f"      = {B + H} / {2 * f_top}")
print(f"      = {hat_v5:.6f}")
if abs(hat_v5 - expected_hat) < 0.001:
    print(f"  ✅ 匹配！这可能是正确公式")
else:
    print(f"  ❌ 不匹配 (差异: {abs(hat_v5 - expected_hat):.3f})")
print()

# 精确反推
print("=" * 80)
print("🎯 精确反推分析")
print("=" * 80)
print()
print("如果 hat = 1.889 m，让我们反推公式参数...")
print()

# 反推: 如果是当前公式，f_top 应该是多少
required_f_top = numerator / expected_hat
print(f"1. 如果公式是 (B/2 + H × tan(45° - φ/2)) / f_top:")
print(f"   则 f_top 应该 = {numerator:.6f} / {expected_hat}")
print(f"                 = {required_f_top:.6f}")
print(f"   (当前使用 f_top = {f_top})")
print()

# 反推: 如果不除以 f_top，分子应该是多少
required_numerator = expected_hat * f_top
print(f"2. 如果公式是 分子 / f_top，分子应该是:")
print(f"   分子 = hat × f_top = {expected_hat} × {f_top} = {required_numerator:.6f}")
print(f"   (当前分子 = {numerator:.6f})")
print()

# 检查是否是 B + H × tan(...)
if abs(required_numerator - (B + h_tan)) < 0.01:
    print(f"   ✅ 匹配！分子应该是 B + H × tan(45° - φ/2)")
    print(f"      即公式应该是: hat = (B + H × tan(45° - φ/2)) / f_top")
else:
    print(f"   差异: {abs(required_numerator - (B + h_tan)):.6f}")

print()
print("=" * 80)
print("💡 结论")
print("=" * 80)
print()

# 测试最可能的公式
print("最可能的正确公式是: hat = (B + H × tan(45° - φ/2)) / f_top")
print()
print("理由:")
print(f"  计算: ({B} + {H} × {tan_value:.6f}) / {f_top}")
print(f"       = ({B} + {h_tan:.6f}) / {f_top}")
print(f"       = {B + h_tan:.6f} / {f_top}")
print(f"       = {hat_v1:.6f}")
print()
if abs(hat_v1 - expected_hat) < 0.01:
    print(f"  ✅ 与期望值 {expected_hat} 非常接近！")
    print()
    print("🔧 需要修改的地方:")
    print("   将公式从: hat = (B/2 + H × tan(45° - φ/2)) / f_top")
    print("   改为:     hat = (B + H × tan(45° - φ/2)) / f_top")
    print()
    print("   即: 去掉 B 的除以 2")
else:
    print(f"  差异仍然较大，可能需要其他调整")

print()
print("=" * 80)
