"""简易集成测试: 使用示例数据验证 FLAC3DExporter 与 TetraF3GridExporter"""
from __future__ import annotations

from pathlib import Path
import sys
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from exporters.flac3d_exporter import FLAC3DExporter
from exporters.tetra_f3grid_exporter import TetraF3GridExporter
from coal_seam_blocks.modeling import BlockModel


def _build_sample_dataset() -> tuple[dict, list[BlockModel], np.ndarray, np.ndarray]:
    """构造一个两层简单模型, 同时产出 BlockModel 栈。"""
    x = np.array([0.0, 20.0, 40.0])
    y = np.array([0.0, 15.0])
    grid_x, grid_y = np.meshgrid(x, y)

    first_bottom = np.zeros_like(grid_x)
    first_top = first_bottom + 6.0
    second_top = first_top + 8.0

    layers = [
        {
            "name": "L01_sample",
            "grid_x": grid_x,
            "grid_y": grid_y,
            "top_surface_z": first_top,
            "bottom_surface_z": first_bottom,
        },
        {
            "name": "L02_sample",
            "grid_x": grid_x,
            "grid_y": grid_y,
            "top_surface_z": second_top,
            "bottom_surface_z": first_top,
        },
    ]

    block_models = [
        BlockModel("L01_sample", points=grid_x.size, top_surface=first_top, bottom_surface=first_bottom),
        BlockModel("L02_sample", points=grid_x.size, top_surface=second_top, bottom_surface=first_top),
    ]

    return {"layers": layers}, block_models, grid_x, grid_y


def run_validation(output_dir: Path | None = None) -> None:
    data, block_models, grid_x, grid_y = _build_sample_dataset()
    out_dir = output_dir or Path(__file__).resolve().parent / "tmp_exports"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 测试 DAT 导出
    flac_exporter = FLAC3DExporter()
    dat_path = out_dir / "sample_model.dat"
    dat_result = flac_exporter.export(
        data,
        str(dat_path),
        options={"normalize_coords": True},
    )
    assert Path(dat_result).exists(), "DAT 导出文件不存在"

    # 测试 F3GRID 导出
    f3grid_exporter = TetraF3GridExporter()
    f3grid_path = out_dir / "sample_model.f3grid"
    f3grid_result = f3grid_exporter.export(
        {
            "block_models": block_models,
            "grid_x": grid_x,
            "grid_y": grid_y,
        },
        str(f3grid_path),
        options={"normalize_coords": True},
    )
    assert Path(f3grid_result).exists(), "F3GRID 导出文件不存在"

    print("FLAC3D DAT 导出: ", dat_result)
    print("T4 F3Grid 导出:", f3grid_result)


if __name__ == "__main__":
    run_validation()
