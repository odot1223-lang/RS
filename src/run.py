import sys
from pathlib import Path

# Erebus copies this file into its controller directory before executing it.
# Prefer the current directory during local runs, then fall back to this project.
local_src = Path(__file__).resolve().parent
project_src = Path.home() / "Documents" / "Pj copy 3" / "src"
src_dir = local_src if (local_src / "main.py").is_file() else project_src

if not (src_dir / "main.py").is_file():
    raise ModuleNotFoundError(f"main.py was not found in {src_dir}")

sys.path.insert(0, str(src_dir))

import main
