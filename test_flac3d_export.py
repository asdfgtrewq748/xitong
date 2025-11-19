
import sys
import os
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from exporters.flac3d_exporter import FLAC3DExporter
    print("Successfully imported FLAC3DExporter")
except ImportError as e:
    print(f"Failed to import FLAC3DExporter: {e}")
    sys.exit(1)

def test_flac3d_export():
    exporter = FLAC3DExporter()
    
    # Create dummy data
    x = np.array([[0, 10], [0, 10]])
    y = np.array([[0, 0], [10, 10]])
    z_top = np.array([[10, 10], [10, 10]])
    z_bottom = np.array([[0, 0], [0, 0]])
    
    data = {
        "layers": [
            {
                "name": "TestLayer",
                "grid_x": x,
                "grid_y": y,
                "grid_z": z_top,
                "grid_z_bottom": z_bottom
            }
        ]
    }
    
    output_path = "test_output.f3grid"
    
    try:
        result_path = exporter.export(data, output_path)
        print(f"Export successful: {result_path}")
        if os.path.exists(result_path):
            print("File exists.")
            # Clean up
            os.remove(result_path)
        else:
            print("File does not exist!")
    except Exception as e:
        print(f"Export failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flac3d_export()
