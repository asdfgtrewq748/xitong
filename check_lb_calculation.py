#!/usr/bin/env python3
"""
check_lb_calculation.py
检查 Lb 的计算逻辑
"""

import sys
sys.path.insert(0, 'd:\\xitong\\backend')

from tunnel_support import TunnelSupportCalculator

print("=" * 80)
print("检查 Lb（锚固深度）的计算")
print("=" * 80)

test_params = {
    'B': 4.8,
    'H': 3.2,
    'K': 1.0,
    'depth': 200,
    'gamma': 18.0,
    'C': 0.5,
    'phi': 32.47,
    'f_top': 2.2
}

calc = TunnelSupportCalculator()
result = calc.calculate_complete(test_params)

print("\n📋 计算结果:")
print("-" * 80)
hct = result['basic']['hct']
hat = result['basic']['hat']

print(f"  hct (顶板松动圈) = {hct} m")
print(f"  hat (压力拱高度) = {hat} m")
print()

# 根据代码，Lb = max(hct, hat)
Lb = max(hct, hat)
print(f"  Lb = max(hct, hat)")
print(f"     = max({hct}, {hat})")
print(f"     = {Lb} m")
print()

# 验证总长度计算
Lm = result['anchor']['Lm']
L_total = result['anchor']['L_total']

print("锚索总长度计算:")
print("-" * 80)
print(f"  Lm (锚固长度)     = {Lm} m")
print(f"  Lb (锚固深度)     = {Lb} m")
print(f"  托盘厚度          = 0.2 m")
print(f"  外露长度          = 0.3 m")
print()
L_calc = Lm + Lb + 0.2 + 0.3
print(f"  L_total = Lm + Lb + 0.2 + 0.3")
print(f"          = {Lm} + {Lb} + 0.2 + 0.3")
print(f"          = {L_calc} m")
print()
print(f"  程序返回: L_total = {L_total} m")
print()

diff = abs(L_total - L_calc)
if diff < 0.001:
    print(f"  ✅ 一致！")
else:
    print(f"  ❌ 差异: {diff} m")

print("\n" + "=" * 80)
print("问题分析:")
print("=" * 80)
print()
print("Lb 的计算逻辑是：")
print(f"  Lb = max(hct, hat)")
print()
print("这意味着:")
print(f"  - 如果 hct > hat，使用 hct（顶板松动圈更大）")
print(f"  - 如果 hat > hct，使用 hat（压力拱更高）")
print()
print(f"当前情况:")
print(f"  hct = {hct:.3f} m")
print(f"  hat = {hat:.3f} m")
if hct > hat:
    print(f"  → 使用 hct = {hct:.3f} m")
    print(f"    锚索需要穿过整个顶板松动圈")
else:
    print(f"  → 使用 hat = {hat:.3f} m")
    print(f"    锚索需要达到压力拱高度")
print()

print("这个逻辑是否合理？")
print("  问题：Lb 应该是什么？")
print("    选项 1: Lb = hct（顶板松动圈）")
print("    选项 2: Lb = hat（压力拱高度）")
print("    选项 3: Lb = max(hct, hat)（当前实现）")
print("    选项 4: Lb = hcs（两帮松动圈）")
print()
print("  请告诉我理论上 Lb 应该使用哪个值？")
print("=" * 80)
