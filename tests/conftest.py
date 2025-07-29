import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the path utility
try:
    from shared.path_utils import require_shared_utilities

    require_shared_utilities()
except ImportError:
    # Fallback error if even path_utils can't be imported
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)
