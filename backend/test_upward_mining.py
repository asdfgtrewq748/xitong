#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上行开采可行度计算功能测试脚本
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from upward_mining_feasibility import (
    process_borehole_csv_for_feasibility,
    batch_process_borehole_files,
    auto_calibrate_coefficients,
    UpwardMiningFeasibility
)

def test_single_calculation():
    """测试单个钻孔计算"""
    print("=== 测试单个钻孔计算 ===")

    # 测试文件路径
    test_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test', 'BK-1.csv')

    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False

    try:
        # 测试参数
        params = {
            'csv_file_path': test_file,
            'bottom_coal_name': '6煤',
            'upper_coal_name': '5煤',
            'lamda': 4.95,
            'C': -0.84
        }

        result = process_borehole_csv_for_feasibility(
            params['csv_file_path'],
            params['bottom_coal_name'],
            params['upper_coal_name'],
            params['lamda'],
            params['C']
        )

        if "error" in result:
            print(f"计算失败: {result['error']}")
            return False

        print("计算成功!")
        print(f"文件: {result['filename']}")
        print(f"开采煤层: {result['bottom_coal']}")
        print(f"上煤层: {result['target_coal']}")
        print(f"开采厚度: {result['mining_coal_thickness_M']} m")
        print(f"中间岩层厚度: {result['total_thickness_H']} m")
        print(f"中间层数: {result['middle_layer_count']}")
        print(f"可行度ω: {result['feasibility_omega']}")
        print(f"可行性等级: {result['feasibility_level']}")
        print(f"平均抗拉强度: {result['avg_tensile_strength']} MPa")

        return True

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_calculation():
    """测试批量计算"""
    print("\n=== 测试批量计算 ===")

    # 创建多个测试文件
    test_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'test')
    test_files = [
        os.path.join(test_dir, 'BK-3.csv'),
    ]

    # 过滤存在的文件
    existing_files = [f for f in test_files if os.path.exists(f)]

    if len(existing_files) < 1:
        print("没有找到足够的测试文件")
        return False

    try:
        params = {
            'csv_file_paths': existing_files,
            'bottom_coal_name': '6煤',
            'upper_coal_name': '5煤',
            'lamda': 4.95,
            'C': -0.84
        }

        result = batch_process_borehole_files(
            params['csv_file_paths'],
            params['bottom_coal_name'],
            params['upper_coal_name'],
            params['lamda'],
            params['C']
        )

        print("批量计算成功!")
        print(f"总文件数: {result['total_files']}")
        print(f"成功计算: {result['successful_files']}")
        print(f"失败文件: {result['error_files']}")
        print(f"平均可行度: {result['avg_feasibility']:.3f}")
        print(f"最高可行度: {result['max_feasibility']:.3f}")
        print(f"最低可行度: {result['min_feasibility']:.3f}")

        # 打印可行性等级分布
        print("\n可行性等级分布:")
        for level, count in result['level_counts'].items():
            print(f"  {level}: {count}")

        return True

    except Exception as e:
        print(f"批量测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_auto_calibration():
    """测试自动标定"""
    print("\n=== 测试自动标定 ===")

    test_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'test')
    test_file = os.path.join(test_dir, 'BK-1.csv')

    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False

    try:
        params = {
            'csv_file_paths': [test_file],
            'bottom_coal_name': '6煤',
            'upper_coal_name': '5煤',
            'initial_lamda': 4.95,
            'initial_C': -0.84
        }

        result = auto_calibrate_coefficients(
            params['csv_file_paths'],
            params['bottom_coal_name'],
            params['upper_coal_name'],
            params['initial_lamda'],
            params['initial_C']
        )

        if result['status'] == 'success':
            print("自动标定成功!")
            data = result['data']
            print(f"样本数量: {data['sample_count']}")
            print(f"KHD范围: {data['khd_range']}")
            print(f"初始λ: {data['initial_lambda']}")
            print(f"初始C: {data['initial_C']}")
            print(f"标定λ: {data['calculated_lambda']}")
            print(f"标定C: {data['calculated_C']}")
            return True
        else:
            print(f"自动标定失败: {result['message']}")
            return False

    except Exception as e:
        print(f"自动标定测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_coefficient_calculation():
    """测试系数计算"""
    print("\n=== 测试系数计算 ===")

    try:
        # 测试极限分区方法
        khd_min = 1.2
        khd_max = 8.5

        lamda, C = UpwardMiningFeasibility.calculate_coefficients(khd_min, khd_max)

        print(f"KHD范围: {khd_min} ~ {khd_max}")
        print(f"计算得到的λ: {lamda:.4f}")
        print(f"计算得到的C: {C:.4f}")

        # 验证计算结果
        omega_min = lamda * khd_min + C
        omega_max = lamda * khd_max + C

        print(f"对应ω范围: {omega_min:.3f} ~ {omega_max:.3f}")

        return True

    except Exception as e:
        print(f"系数计算测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试上行开采可行度计算功能...")

    # 检查测试文件
    test_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'test')
    os.makedirs(test_dir, exist_ok=True)

    test_file = os.path.join(test_dir, 'BK-1.csv')
    if not os.path.exists(test_file):
        print(f"请确保测试文件存在: {test_file}")
        return

    # 运行测试
    tests = [
        test_coefficient_calculation,
        test_single_calculation,
        test_batch_calculation,
        test_auto_calibration
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"测试异常: {str(e)}")
            failed += 1

    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")

    if failed == 0:
        print("所有测试通过!")
    else:
        print("存在测试失败，请检查代码")

if __name__ == '__main__':
    main()