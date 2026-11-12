import os
import pathlib

_root = str(pathlib.Path(__file__).parent)
os.environ["PYTHONPATH"] = _root + os.pathsep + os.environ.get("PYTHONPATH", "")
