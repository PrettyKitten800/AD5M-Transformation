"""Front removable cradle in upright housing coordinates. Print on the common bottom face."""
import FreeCAD as App
import Part

V = App.Vector
BOTTOM = 1.2
FRONT = 55.2
Z_HOLE = 11.8119
ANCHOR_HEIGHTS = (8.21775, 28.21775)

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0,y0,z0))

def build():
    # Two low beams flank the shroud. Pads widen only where they seat against the housing.
    pieces = [box(-35.8,35.8,50.8,FRONT,BOTTOM,7.0),
              box(-10.4,10.4,50.8,FRONT,BOTTOM,20.8)]
    for positive in (False,True):
        inn = 30.15  # 0.30 mm total slip clearance over the nominal 60 mm housing
        def rail(x0,x1,y0,y1,z0,z1):
            lo,hi=(x0,x1) if positive else (-x1,-x0)
            return box(lo,hi,y0,y1,z0,z1)
        pieces.extend([rail(32.0,35.8,-10.1,FRONT,BOTTOM,7.0),
                       rail(inn,35.8,-10.1,-1.9,BOTTOM,32.4)])
    rounded=[]
    for piece in pieces:
        upright=[e for e in piece.Edges if e.BoundBox.XLength<.001 and e.BoundBox.YLength<.001]
        piece=piece.makeFillet(1.0,upright)
        rims=[e for e in piece.Edges if e.BoundBox.ZLength<.001]
        rounded.append(piece.makeFillet(.45,rims))
    frame=rounded[0].multiFuse(rounded[1:]).removeSplitter()
    for side in (-1,1):
        for z in ANCHOR_HEIGHTS:
            frame=frame.cut(Part.makeCylinder(1.65,9,V(side*37,-6,z),V(-side,0,0)))
    for x in (-5.25,5.25):
        low,high=Z_HOLE-3,Z_HOLE+3
        slot=box(x-1.65,x+1.65,50,56,low,high)
        for z in (low,high):
            slot=slot.fuse(Part.makeCylinder(1.65,6,V(x,50,z),V(0,1,0)))
        frame=frame.cut(slot)
        frame=frame.cut(box(x-2.9,x+2.9,50.75,53.3,low-3.15,high+3.15))
    assert frame.isValid() and len(frame.Solids)==1
    return frame
