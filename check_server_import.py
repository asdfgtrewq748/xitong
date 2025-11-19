
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    import server
    print("Successfully imported server module")
except Exception as e:
    print(f"Failed to import server module: {e}")
    import traceback
    traceback.print_exc()
