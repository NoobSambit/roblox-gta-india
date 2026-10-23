"""Reproducible batch build. Blender --python-exit-code 1 --python build.py."""
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import rajbari,jorasanko
if __name__=='__main__':
    rajbari.build()
    jorasanko.build()
