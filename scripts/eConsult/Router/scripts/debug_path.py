import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

print("🔍 sys.path includes:")
for p in sys.path:
    print("  ", p)

try:
    from utils.config import Config
    print("✅ SUCCESS: utils.config is importable")
except Exception as e:
    print("❌ FAILED:", e)
