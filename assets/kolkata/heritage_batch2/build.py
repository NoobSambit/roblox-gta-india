"""Run this file in Blender to reproduce the four-building exterior batch."""
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import writers,metropolitan,gpo,town_hall

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    for module in [writers,metropolitan,gpo,town_hall]:
        if not args or module.__name__ in args:module.build()
