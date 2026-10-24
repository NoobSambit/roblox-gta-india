"""Blender --background --python build.py -- new_market|indian_museum|st_pauls."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
if __name__=='__main__':
    keys=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['new_market','indian_museum','st_pauls']
    for key in keys:__import__(key).build()
