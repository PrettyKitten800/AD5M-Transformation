import * as T from 'three';
import {OrbitControls} from '/orbit.js';
import {STLLoader} from '/stl.js';

const el = id => document.getElementById(id);
const canvas = document.querySelector('canvas');
const status = el('status');

async function openReview() {
  const renderer = new T.WebGLRenderer({canvas, antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  const scene = new T.Scene();
  scene.background = new T.Color(0x18202a);
  const camera = new T.PerspectiveCamera(38, 1, 0.1, 2000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, canvas);
  const [geometry, data] = await Promise.all([
    new STLLoader().loadAsync('/model.stl'), fetch('/marks').then(r=>r.json())
  ]);
  geometry.computeBoundingBox();
  const center = geometry.boundingBox.getCenter(new T.Vector3());
  const size = geometry.boundingBox.getSize(new T.Vector3()).length();
  const mesh = new T.Mesh(geometry, new T.MeshPhongMaterial({color:0xa1cdd2,
    specular:0x384751, shininess:24, side:T.DoubleSide, polygonOffset:true,
    polygonOffsetFactor:1, polygonOffsetUnits:1}));
  scene.add(mesh, new T.HemisphereLight(0xffffff,0x8b9bad,1.85));
  const lamp = new T.DirectionalLight(0xfff3e0,2.4);
  scene.add(lamp, lamp.target);
  lamp.target.position.copy(center);
  function reset() {
    controls.target.copy(center);
    camera.position.copy(center).addScaledVector(new T.Vector3(1,-1.6,1.2).normalize(),
      size * Math.max(1.55, 1.25/camera.aspect));
    controls.update();
  }
  const ray = new T.Raycaster();
  function hit(event) {
    const b = canvas.getBoundingClientRect();
    ray.setFromCamera(new T.Vector2(2*(event.clientX-b.left)/b.width-1,
      1-2*(event.clientY-b.top)/b.height),camera);
    return ray.intersectObject(mesh)[0]?.point;
  }
  let mode='rotate', selected=data.marks.length-1, pending=null, pointer=null;
  let version=0, written=0, saving=false, timer;
  function dirty() {
    version++; status.textContent='Saving…';
    clearTimeout(timer); timer=setTimeout(save,180);
  }
  async function save() {
    if(saving) return;
    saving=true;
    try {
      while(written!==version) {
        const target=version;
        const response=await fetch('/marks',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify(data)});
        if(!response.ok) throw Error(response.status===409?'Another view changed these marks. Reopen to load its edits.':'Save failed. Edit again to retry.');
        data.revision=(await response.json()).revision; written=target;
      }
      status.textContent='Saved to shared workspace';
    } catch(e) {status.textContent=e.message} finally {saving=false}
  }
  window.addEventListener('beforeunload',e=>{if(version!==written){e.preventDefault();e.returnValue=''}});
  const overlay=new T.Group(); scene.add(overlay);
  const tags=[];
  function refresh() {
    overlay.traverse(o=>{o.geometry?.dispose();o.material?.dispose()});
    overlay.clear(); tags.length=0; el('pins').replaceChildren();
    el('marks').replaceChildren();
    function paint(mark,i,active) {
      const points=mark.points.map(p=>new T.Vector3(...p));
      const color=active?0xffb738:0xffdf8c;
      const dot=new T.Mesh(new T.SphereGeometry(0.65,12,8),new T.MeshBasicMaterial({color}));
      dot.position.copy(points[0]);overlay.add(dot);
      if(points.length>1) {
        overlay.add(new T.Line(new T.BufferGeometry().setFromPoints(points),new T.LineBasicMaterial({color})));
      }
      if(i===null)return;
      el('marks').add(new Option('Mark '+(i+1),i));
      const tag=document.createElement('span');tag.className='tag';tag.textContent=i+1;
      el('pins').append(tag);tags.push([points[0],tag]);
    }
    data.marks.forEach((m,i)=>paint(m,i,i===selected));
    if(pending?.length)paint({points:pending},null,true);
    const empty=!data.marks.length;
    if(empty)el('marks').add(new Option('No marks yet',''));
    else el('marks').value=selected;
    el('marks').disabled=el('remove').disabled=el('note').disabled=empty;
    el('note').value=data.marks[selected]?.note??'';
  }
  function setMode(next) {
    mode=next;controls.enabled=mode==='rotate';
    for(const id of ['rotate','pin','draw'])el(id).setAttribute('aria-pressed',String(id===mode));
    canvas.style.cursor=controls.enabled?'grab':'crosshair';
    el('hint').textContent={rotate:'Drag to rotate. Scroll or pinch to zoom.',pin:'Click the surface to place a pin, then describe the change below.',draw:'Drag on the surface to mark it, then describe the change below.'}[mode];
  }
  for(const id of ['rotate','pin','draw'])el(id).onclick=()=>setMode(id);
  el('reset').onclick=reset;
  el('marks').onchange=()=>{selected=Number(el('marks').value);refresh()};
  el('note').oninput=()=>{data.marks[selected].note=el('note').value;dirty()};
  el('remove').onclick=()=>{data.marks.splice(selected,1);selected=Math.min(selected,data.marks.length-1);refresh();dirty()};
  function finish() {
    if(!pending?.length)return;
    data.marks.push({points:pending,note:''}); pending=null; selected=data.marks.length-1;refresh();dirty();
  }
  canvas.addEventListener('pointerdown',e=>{
    if(mode==='rotate'||e.button!==0||pointer!==null)return;
    const p=hit(e);if(!p)return;
    pending=[p.toArray()];
    if(mode==='pin'){finish();return}
    pointer=e.pointerId;canvas.setPointerCapture(pointer);refresh();
  });
  canvas.addEventListener('pointermove',e=>{
    if(e.pointerId!==pointer||!pending)return;
    const p=hit(e);
    if(!p||pending.length>=6000){finish();return}
    if(p.distanceTo(new T.Vector3(...pending.at(-1)))<0.3)return;
    pending.push(p.toArray());refresh();
  });
  for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,e=>{
    if(e.pointerId===pointer){pointer=null;finish()}
  });
  function resize() {
    const b=el('viewport').getBoundingClientRect();
    renderer.setSize(b.width,b.height,false);camera.aspect=b.width/b.height;camera.updateProjectionMatrix();
  }
  resize();reset();new ResizeObserver(resize).observe(el('viewport'));refresh();
  status.textContent=data.marks.length?'Saved marks loaded':'Ready to mark';
  const sight=new T.Raycaster();
  function frame() {
    lamp.position.copy(camera.position).add(new T.Vector3(-25,8,35));
    for(const [pt,tag] of tags){
      const delta=pt.clone().sub(camera.position);
      sight.set(camera.position,delta.clone().normalize());sight.far=delta.length()-0.3;
      const p=pt.clone().project(camera);
      tag.hidden=p.z>1||sight.intersectObject(mesh).length>0;
      tag.style.left=(p.x+1)*50+'%';tag.style.top=(1-p.y)*50+'%';
    }
    renderer.render(scene,camera);
  }
  // Redraw on interaction or edits, including resizes, without polling the mesh while idle.
  controls.addEventListener('change',frame);
  new MutationObserver(frame).observe(el('marks'),{childList:true});
  new ResizeObserver(frame).observe(el('viewport'));frame();
}
openReview().catch(error=>{status.textContent='Could not open the shroud: '+error.message;console.error(error)});
