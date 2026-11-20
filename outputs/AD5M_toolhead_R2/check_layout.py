from pathlib import Path
import json,tempfile
import vtk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
out=Path(__file__).resolve().parent
parts=json.loads((Path(tempfile.gettempdir())/'ad5m_r2_preview.json').read_text())
def poly(p):
    v=np.array(p['v'],dtype=float)
    f=np.array(p['f'],dtype=np.int64)
    pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(v,deep=True))
    ca=vtk.vtkCellArray();ca.SetData(numpy_to_vtkIdTypeArray(np.arange(0,3*len(f)+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(f.ravel(),deep=True))
    pd=vtk.vtkPolyData();pd.SetPoints(pts);pd.SetPolys(ca);return pd
meshes=[poly(p) for p in parts]
def contacts(i,j):
    c=vtk.vtkCollisionDetectionFilter();c.SetInputData(0,meshes[i]);c.SetInputData(1,meshes[j]);c.SetMatrix(0,vtk.vtkMatrix4x4());c.SetMatrix(1,vtk.vtkMatrix4x4());c.SetCollisionModeToAllContacts();c.Update()
    return c.GetNumberOfContacts()
def contact_report(i,j):
    return {'triangle_contacts':contacts(i,j)}
report=json.loads((out/'checks.json').read_text())
for i,j,k in [(1,4,'front_cradle_vs_candidate_duct'),(3,4,'eddy_vs_candidate_duct'),(2,4,'hotend_vs_candidate_duct'),(1,5,'front_cradle_vs_blower_envelope')]:
    report[k]=contact_report(i,j)
# Region separation bound: the cradle is a union of the anchor pads, side rails and front bridge.
# Fillets and bores remove material. Each term is a separating-axis gap for that region.
duct_points=np.asarray(parts[4]['v'])
front_duct = duct_points.max(axis=0)
back_duct = duct_points.min(axis=0)
report['minimum_cradle_duct_gap_bound_mm']=round(min(32-max(front_duct[0],-back_duct[0]),
    50.8-front_duct[1],back_duct[1]-(-1.9)),3)
report['case_forward_of_shroud_mm']=round(np.max(np.array(parts[3]['v'])[:,1])-front_duct[1],2)
report['mesh_checks']={}
for filename in ('Housing_R2.stl','Front_cradle_R2.stl'):
    rd=vtk.vtkSTLReader();rd.SetFileName(str(out/filename));rd.Update()
    pd=rd.GetOutput()
    edges=vtk.vtkFeatureEdges();edges.SetInputData(pd);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.ManifoldEdgesOff();edges.FeatureEdgesOff();edges.Update()
    conn=vtk.vtkPolyDataConnectivityFilter();conn.SetInputData(pd);conn.SetExtractionModeToAllRegions();conn.Update()
    report['mesh_checks'][filename]=dict(boundary_or_nonmanifold_edges=edges.GetOutput().GetNumberOfCells(),components=conn.GetNumberOfExtractedRegions())
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
w,h=830,770
def drawmodel(ids,view,offsets={},scale=80,target=(0,14,44)):
    ren=vtk.vtkRenderer(); ren.SetBackground(.947,.957,.966)
    window=vtk.vtkRenderWindow(); window.SetOffScreenRendering(1);window.SetSize(w,h);window.AddRenderer(ren);window.SetMultiSamples(4)
    for i in ids:
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(meshes[i])
        a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*[c/255 for c in parts[i]['color']]);a.GetProperty().SetAmbient(.3);a.GetProperty().SetDiffuse(.7)
        a.SetPosition(*offsets.get(i,(0,0,0)));ren.AddActor(a)
    cam=ren.GetActiveCamera();cam.SetFocalPoint(*target);cam.SetPosition(*(np.array(target)+np.array(view)*220));cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(scale);ren.ResetCameraClippingRange();window.Render()
    buff=vtk.vtkWindowToImageFilter();buff.SetInput(window);buff.ReadFrontBufferOff();buff.Update();im=Image.fromarray(np.flipud(vtk_to_numpy(buff.GetOutput().GetPointData().GetScalars()).reshape((h,w,3))).copy());window.Finalize();return im
im=Image.new('RGB',(1660,940),'#f1f4f6')
im.paste(drawmodel(range(9),(-1.3,1,.52)),(0,86))
im.paste(drawmodel([0,1,2,3,6],(-1.1,.96,.65),{},68,(0,27,32)),(830,86))
d=ImageDraw.Draw(im)
def txt(x,y,t,size=22,bold=False):
    f=ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size);d.text((x,y),t,font=f,fill='#20313a')
txt(36,14,'AD5M   /   Inline Eddy toolhead R2',36,True);txt(36,62,'Assembly study with a candidate duct from the X1C Hotend folder',21)
txt(36,856,'Assembled',26,True);txt(36,894,'Teal duct, amber cradle and dark Eddy. The upper EBB42 carrier is provisional.',19)
txt(864,856,'Cradle and housing attachment',26,True);txt(864,894,'Cooling module hidden to show the two arms and the center probe mount.',19)
im.save(out/'Toolhead_preview.png')
