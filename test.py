import os

# 在这里改成你想保存的路径（也可以就用当前目录）
OUTPUT_DIR = "."

# 一个 10m×10m×10m 的小砖块
# 底：z = 0，顶：z = 10
# 1 底西南，2 底东南，3 底东北，4 底西北
# 5 顶西南，6 顶东南，7 顶东北，8 顶西北
gridpoints = {
    1: (0.0,  0.0,  0.0),   # bottom SW
    2: (10.0, 0.0,  0.0),   # bottom SE
    3: (10.0, 10.0, 0.0),   # bottom NE
    4: (0.0,  10.0, 0.0),   # bottom NW
    5: (0.0,  0.0,  10.0),  # top SW
    6: (10.0, 0.0,  10.0),  # top SE
    7: (10.0, 10.0, 10.0),  # top NE
    8: (0.0,  10.0, 10.0),  # top NW
}

# 几个候选的 B8 节点顺序（重点就是这几行）
# 说明：
#  - 每个列表是 8 个节点号，对应 Z B8 1 后面的 8 个数字
#  - 它们都代表同一个几何，只是节点顺序不同
orderings = {
    # A：我们现在习惯用的顺序
    "A": [1, 2, 3, 4, 5, 6, 7, 8],

    # B：底面顺时针 + 顶面顺时针
    "B": [1, 2, 4, 3, 5, 6, 8, 7],

    # C：底面逆时针 + 顶面逆时针
    "C": [1, 4, 3, 2, 5, 8, 7, 6],

    # D：换一个起点 + 顺时针
    "D": [2, 3, 4, 1, 6, 7, 8, 5],

    # E：再换一种常见有限元写法
    "E": [1, 2, 3, 4, 8, 7, 6, 5],

    # F：底面 (1,3,4,2)，顶面 (5,7,8,6)
    "F": [1, 3, 4, 2, 5, 7, 8, 6],
}

def write_f3grid(path, gp_order):
    """
    按 Itasca 官方 ASCII 网格格式写一个只有 1 个 B8 单元的 .f3grid 文件
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write("; Simple test grid for FLAC3D B8 node ordering\n")
        f.write("; One brick zone, 8 gridpoints\n\n")

        # GRIDPOINTS
        f.write("*GRIDPOINTS\n")
        for gid, (x, y, z) in gridpoints.items():
            # G <id> <x> <y> <z>
            f.write(f"G {gid} {x:.6f} {y:.6f} {z:.6f}\n")

        f.write("\n*ZONES\n")
        # Z B8 <zone_id> <gp0> <gp1> <gp2> <gp3> <gp4> <gp5> <gp6> <gp7>
        ids_str = " ".join(str(i) for i in gp_order)
        f.write(f"Z B8 1 {ids_str}\n")

    print(f"written: {path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for key, order in orderings.items():
        filename = os.path.join(OUTPUT_DIR, f"test_{key}.f3grid")
        write_f3grid(filename, order)

if __name__ == "__main__":
    main()
