"""Local serializer compatibility repair; preserve all existing validation gates."""
import sys,runpy
from pathlib import Path
skill=Path('/home/nuo/.codex/skills/ppt-master/scripts')
sys.path.insert(0,str(skill))
import pptx_transitions
# The round-trip merger must know prefixes introduced by newly authored Office Math.
# Source pages without pre-existing equations have no original a14 namespace binding.
pptx_transitions.TRANSITION_NAMESPACES['a14']='http://schemas.microsoft.com/office/drawing/2010/main'
script=skill/'svg_to_pptx.py'
sys.argv=[str(script),*sys.argv[1:]]
runpy.run_path(str(script),run_name='__main__')
