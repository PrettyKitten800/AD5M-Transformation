"""Headless Blender Workbench renderer for AD5M 3x MGN12H Gantry R1."""

from pathlib import Path
import math
import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[3]
PARTS_DIR = REPO / "outputs" / "AD5M_MGN12_Gantry_R1" / "parts"
REND_DIR = REPO / "outputs" / "AD5M_MGN12_Gantry_R1" / "renders"
REND_DIR.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

PALETTE = {
    "Ref_AD5M_Frame":       (0.20, 0.22, 0.25, 1.0),
    "Ref_Rails_Blocks":     (0.75, 0.78, 0.82, 1.0),
    "Ref_Motors_48mm":      (0.12, 0.12, 0.14, 1.0),
    "Ref_Pulleys_Bearings": (0.88, 0.72, 0.24, 1.0),
    "Ref_Dowel_Pins":       (0.90, 0.92, 0.95, 1.0),
    "Ref_Belt_A":           (0.95, 0.25, 0.15, 1.0),
    "Ref_Belt_B":           (0.15, 0.80, 0.40, 1.0),
    "Y_Rail_Spine_R":       (0.18, 0.45, 0.85, 1.0),
    "Y_Rail_Spine_L":       (0.18, 0.45, 0.85, 1.0),
    "Rear_Motor_Mount_R":   (0.22, 0.60, 0.95, 1.0),
    "Rear_Motor_Mount_L":   (0.22, 0.60, 0.95, 1.0),
    "Motor_DS_Cap_R":       (0.98, 0.56, 0.20, 1.0),
    "Motor_DS_Cap_L":       (0.98, 0.56, 0.20, 1.0),
    "Front_BFI_Housing_R":  (0.22, 0.60, 0.95, 1.0),
    "Front_BFI_Housing_L":  (0.22, 0.60, 0.95, 1.0),
    "Front_BFI_Carrier_R":  (0.95, 0.55, 0.12, 1.0),
    "Front_BFI_Carrier_L":  (0.95, 0.55, 0.12, 1.0),
    "XY_Joint_R_Upper":     (0.55, 0.30, 0.88, 1.0),
    "XY_Joint_R_Lower":     (0.22, 0.74, 0.97, 1.0),
    "XY_Joint_R_Bottom_Cap": (0.98, 0.56, 0.20, 1.0),
    "XY_Joint_L_Upper":     (0.55, 0.30, 0.88, 1.0),
    "XY_Joint_L_Lower":     (0.22, 0.74, 0.97, 1.0),
    "X_Carriage_MGN12_Base_R1": (0.10, 0.78, 0.82, 1.0),
}

for name, color in PALETTE.items():
    stl = PARTS_DIR / f"{name}.stl"
    if not stl.exists():
        continue
    bpy.ops.wm.stl_import(filepath=str(stl))
    obj = bpy.context.active_object
    obj.name = name
    obj.color = color

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.studio_light = "Default"
scene.display.shading.color_type = "OBJECT"
scene.display.shading.show_cavity = True
scene.display.shading.cavity_ridge_factor = 1.0
scene.display.shading.cavity_valley_factor = 1.4
scene.render.resolution_x = 1400
scene.render.resolution_y = 1050
scene.render.image_settings.file_format = "PNG"

world = bpy.data.worlds.new("World")
scene.world = world
world.color = (0.07, 0.08, 0.10)

cam_data = bpy.data.cameras.new("Cam")
cam_data.clip_start = 1.0
cam_data.clip_end = 5000.0
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj


def render_persp(fname: str, pos, target, lens: float = 45.0) -> None:
    cam_data.type = "PERSP"
    cam_data.lens = lens
    cam_obj.location = Vector(pos)
    direction = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(REND_DIR / fname)
    bpy.ops.render.render(write_still=True)


def render_ortho_top(fname: str) -> None:
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 400.0
    cam_obj.location = Vector((0.0, 0.0, 750.0))
    direction = Vector((0.0, 0.0, 385.0)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(REND_DIR / fname)
    bpy.ops.render.render(write_still=True)


# 1. Top orthographic view (without frame top-ring steel blocking inside? Keep frame, Z=406.8 top deck shows cavity clearly!)
render_ortho_top("01_top_ortho.png")

# 2. Isometric overview inside AD5M_Frame.STEP
render_persp("02_iso_overview.png", (-240.0, -340.0, 620.0), (0.0, 0.0, 375.0), lens=38.0)

# 3. Rear-right 48mm Motor Mount + Double-Shear Cap close-up (inboard-front-down angle)
render_persp("03_rear_motor_closeup.png", (55.0, 65.0, 325.0), (138.0, 156.0, 376.0), lens=42.0)

# 6. Rear-left Motor Mount + Double-Shear Cap close-up (front-inboard-slightly-above view)
render_persp("06_rear_ds_cap_closeup.png", (-60.0, 65.0, 415.0), (-136.0, 155.0, 378.0), lens=42.0)

# 4. Front-right BFI Compression Tensioner close-up (from open front door looking toward front-right corner)
render_persp("04_front_bfi_closeup.png", (55.0, -70.0, 345.0), (150.0, -155.0, 383.0), lens=45.0)

# 5. Right 3-piece split XY-Joint + Self-supporting 300mm X-Rail + X-Carriage
render_persp("05_xy_joint_R_closeup.png", (25.0, -78.0, 336.0), (142.0, 8.0, 382.0), lens=44.0)

# 7. Left 2-piece split XY-Joint close-up (inboard-front-down angle verifying Belt B bays & Belt A 20T)
render_persp("07_xy_joint_L_closeup.png", (-25.0, -78.0, 336.0), (-142.0, 8.0, 382.0), lens=44.0)

print("Rendered all 7 PNGs cleanly.")
