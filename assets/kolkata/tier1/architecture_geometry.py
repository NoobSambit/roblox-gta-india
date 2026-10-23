"""Indexed primitives: shared edges within solids, separate touching solids."""
from geometry import Geometry as LegacyGeometry


class Geometry(LegacyGeometry):
    def __init__(self):
        super().__init__()
        self._vertices={}

    def polygon(self,vertices,mat='Pearl',smooth=False):
        face=[]
        for p in vertices:
            key=tuple(round(c,6) for c in p)
            if key not in self._vertices:
                self._vertices[key]=len(self.v);self.v.append(tuple(p))
            index=self._vertices[key]
            if not face or face[-1]!=index:face.append(index)
        if len(face)>1 and face[0]==face[-1]:face.pop()
        if len(set(face))>=3:
            self.f.append(tuple(face));self.mat.append(mat);self.smooth.append(smooth)

    def _primitive(self,method,*args,**kwargs):
        raw=LegacyGeometry();getattr(raw,method)(*args,**kwargs)
        part=Geometry()
        for face,mat,smooth in zip(raw.f,raw.mat,raw.smooth):
            part.polygon([raw.v[i] for i in face],mat,smooth)
        self.merge(part)

    def box(self,*args,**kwargs):self._primitive('box',*args,**kwargs)
    def lathe(self,*args,**kwargs):self._primitive('lathe',*args,**kwargs)
    def cylinder(self,*args,**kwargs):self._primitive('cylinder',*args,**kwargs)
    def beam(self,*args,**kwargs):self._primitive('beam',*args,**kwargs)
    def ellipsoid(self,*args,**kwargs):self._primitive('ellipsoid',*args,**kwargs)

    def arch(self,*args,**kwargs):
        outer=self._vertices;self._vertices={}
        LegacyGeometry.arch(self,*args,**kwargs)
        self._vertices=outer
