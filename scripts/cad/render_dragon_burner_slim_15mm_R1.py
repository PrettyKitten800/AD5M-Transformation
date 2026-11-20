"""
Render Regular vs. Reverse-Orbiter (-15.0 mm Slim AD5M Dragon Burner) comparison plots
and multi-view renders of the three printable STLs in outputs/Dragon_Burner_AD5M_Slim_15mm_R1/.

Outputs:
  - regular_vs_reverse_slim_comparison.png :
      Exact FreeCAD BRep sections + 3D envelope comparison (Regular Rear-Motor vs
      180 deg Reverse-Orbiter Front-Motor + Steel Carriage & Mirrored Heatsets)
  - slim_parts_multiview.png :
      Multi-view inspection of the 3 exported printable STLs + print orientations
"""

from __future__ import annotations

import json
from pathlib import Path

import FreeCAD as App
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import Mesh
import numpy as np
import Part


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs/Dragon_Burner_AD5M_Slim_15mm_R1"
FCSTD_PATH = OUT_DIR / "AD5M_Dragon_Burner_Slim_15mm_Comparison_R1.FCStd"
PREVIEW_JSON = OUT_DIR / "preview_parts.json"
VAL_JSON = OUT_DIR / "validation.json"


def set_axes_equal(ax, verts: np.ndarray, pad: float = 4.0) -> None:
    mins = verts.min(axis=0) - pad
    maxs = verts.max(axis=0) + pad
    spans = maxs - mins
    half = spans.max() / 2.0
    mid = (mins + maxs) / 2.0
    ax.set_xlim(mid[0] - half, mid[0] + half)
    ax.set_ylim(mid[1] - half, mid[1] + half)
    ax.set_zlim(mid[2] - half, mid[2] + half)


def add_mesh_to_ax(ax, verts_xyz: np.ndarray, faces: np.ndarray,
                   rgba: tuple[float, float, float, float],
                   max_faces: int = 7500, printer_axes: bool = True) -> None:
    """Shade triangle mesh. If printer_axes=True: (X, Y_up, Z_fwd) -> (X, Z_fwd, Y_up)."""
    if len(faces) == 0:
        return
    if len(faces) > max_faces:
        step = max(1, len(faces) // max_faces)
        faces = faces[::step]
    if printer_axes:
        pts = np.column_stack([verts_xyz[:, 0], verts_xyz[:, 2], verts_xyz[:, 1]])
    else:
        pts = verts_xyz
    tris = pts[faces]
    poly = Poly3DCollection(
        tris,
        facecolors=rgba,
        edgecolors=(0.12, 0.12, 0.12, 0.08),
        linewidths=0.14,
        shade=True,
    )
    ax.add_collection3d(poly)


def plot_section_edges(ax, shape: Part.Shape, normal: App.Vector, d: float,
                       proj: str, color: str, lw: float = 1.6, ls: str = "-",
                       label: str | None = None, zorder: int = 4) -> None:
    """Intersect BRep shape with plane normal.dot(P) = d and draw discretized edges."""
    if abs(normal.x) > 0.5:
        p0 = App.Vector(d, 100.0, -50.0)
    elif abs(normal.y) > 0.5:
        p0 = App.Vector(-50.0, d, -50.0)
    else:
        p0 = App.Vector(-50.0, -200.0, d)
    sec = shape.section(Part.makePlane(320, 320, p0, normal))

    first = True
    for e in sec.Edges:
        pts = e.discretize(Deflection=0.06)
        if len(pts) < 2:
            continue
        if proj == "zy":
            xs = [p.z for p in pts]
            ys = [p.y for p in pts]
        elif proj == "xz":
            xs = [p.x for p in pts]
            ys = [p.z for p in pts]
        elif proj == "xy":
            xs = [p.x for p in pts]
            ys = [p.y for p in pts]
        else:
            raise ValueError(proj)
        ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls,
                label=(label if first else None), zorder=zorder)
        first = False


def render_comparison(parts: dict, val: dict) -> Path:
    doc = App.openDocument(str(FCSTD_PATH))
    shapes = {o.Name: o.Shape for o in doc.Objects}

    slim = shapes["PRINT_Slim15mmAdapter_R1"]
    orig_base = shapes["REF_OrigBase1406257"]
    db_main = shapes["REF_DB_MainBody_Slim"]
    duct_r = shapes["REF_DB_DuctRight_Slim"]
    hotend = shapes["REF_BambuHotend_Slim"]
    bm_orig = shapes["REF_BambuMount_Orig_Slim"]
    om_orig = shapes["REF_OrbiterMount_Orig_Slim"]
    bm_rev = shapes["PRINT_BambuMount_RevOrb_Slim"]
    om_rev = shapes["PRINT_OrbiterMount_RevOrb_Slim"]
    orb_reg = shapes["ENV_Orbiter25_Regular_RearMotor"]
    orb_rev = shapes["ENV_Orbiter25_Reverse_FrontMotor"]

    nx, ny, nz = val["checks"]["nozzle_tip_slim_mm"]
    car_y = ny + 13.600
    reg_chk = val["checks"]["regular_orbiter_motor_envelope"]
    rev_chk = val["checks"]["reverse_orbiter_motor_envelope"]

    fig = plt.figure(figsize=(16.5, 11.5), dpi=180)
    fig.patch.set_facecolor("#F7F8FA")
    gs = fig.add_gridspec(2, 2, hspace=0.27, wspace=0.18)

    # --- Panel A: Centerline YZ Slice - REGULAR SLIM (Rear Motor) ---
    axA = fig.add_subplot(gs[0, 0])
    axA.add_patch(Rectangle((-20.0, car_y), 20.0, 96.0, facecolor="#90A4AE", alpha=0.35, edgecolor="#455A64", lw=1.2,
                            label="Stock Steel Carriage (Z<=0)"))
    plot_section_edges(axA, orig_base, App.Vector(1, 0, 0), nx, "zy", "#9E9E9E", lw=1.0, ls="--",
                       label="Orig #1406257 (Nozzle Z=44.70)")
    plot_section_edges(axA, slim, App.Vector(1, 0, 0), nx, "zy", "#1565C0", lw=2.0,
                       label="Slim Adapter -15mm (Mount Z=18.40)")
    plot_section_edges(axA, bm_orig, App.Vector(1, 0, 0), nx, "zy", "#2E7D32", lw=1.5, label="Stock Bambu_Mount")
    plot_section_edges(axA, om_orig, App.Vector(1, 0, 0), nx, "zy", "#66BB6A", lw=1.5, label="Stock Orbiter2_Mount")
    plot_section_edges(axA, db_main, App.Vector(1, 0, 0), nx, "zy", "#EF6C00", lw=1.3, label="Dragon Burner MainBody")
    plot_section_edges(axA, hotend, App.Vector(1, 0, 0), nx, "zy", "#C62828", lw=1.8, label="Bambu X1/P1 Hotend")
    plot_section_edges(axA, orb_reg, App.Vector(1, 0, 0), nx, "zy", "#8E24AA", lw=1.9, ls="-.",
                       label="Orbiter 2.5 Regular (Rear Motor Env)")
    axA.axvline(nz, color="#C62828", lw=0.9, ls=":")
    axA.axvline(44.697, color="#9E9E9E", lw=0.9, ls=":")
    axA.annotate(
        f"Rear LDO Ø36x20 Motor\nZ=[{reg_chk['motor_z_span_mm'][0]}, {reg_chk['motor_z_span_mm'][1]}]\n"
        f"{reg_chk['motor_rear_gap_to_steel_carriage_mm']:.1f} mm to steel carriage",
        xy=(22.0, -28.0), xytext=(34.0, -26.0), fontsize=7.5, fontweight="bold", color="#6A1B9A",
        arrowprops=dict(arrowstyle="->", color="#6A1B9A", lw=1.1),
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#8E24AA", lw=0.7, alpha=0.95),
    )
    axA.annotate("Nozzle shifted\n-15.0 mm (29.70 mm)", xy=(nz, ny + 4.0), xytext=(42.0, -72.0),
                 fontsize=7.5, fontweight="bold", color="#B71C1C",
                 arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=1.1, connectionstyle="arc3,rad=-0.15"),
                 bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#C62828", lw=0.6, alpha=0.92))
    axA.set_xlim(-22.0, 74.0)
    axA.set_ylim(-146.0, -14.0)
    axA.set_aspect("equal")
    axA.grid(True, alpha=0.25)
    axA.set_xlabel("Z_adapter / +Forward (mm)")
    axA.set_ylabel("Y_adapter / +Up (mm)")
    axA.set_title("Option 1: Regular Slim -15 mm (Rear-Motor Orbiter 2.5)", fontsize=10.5, fontweight="bold")
    axA.legend(loc="lower left", fontsize=6.4, framealpha=0.94)

    # --- Panel B: Centerline YZ Slice - REVERSE ORBITER SLIM (Front Motor) ---
    axB = fig.add_subplot(gs[0, 1])
    axB.add_patch(Rectangle((-20.0, car_y), 20.0, 96.0, facecolor="#90A4AE", alpha=0.35, edgecolor="#455A64", lw=1.2,
                            label="Stock Steel Carriage (Z<=0)"))
    plot_section_edges(axB, orig_base, App.Vector(1, 0, 0), nx, "zy", "#9E9E9E", lw=1.0, ls="--",
                       label="Orig #1406257 Outline")
    plot_section_edges(axB, slim, App.Vector(1, 0, 0), nx, "zy", "#1565C0", lw=2.0,
                       label="Slim Adapter -15mm (Mount Z=18.40)")
    plot_section_edges(axB, bm_rev, App.Vector(1, 0, 0), nx, "zy", "#00897B", lw=1.5, label="Remixed Bambu_Mount_RevOrb")
    plot_section_edges(axB, om_rev, App.Vector(1, 0, 0), nx, "zy", "#26A69A", lw=1.5, label="180° Orbiter2_Mount_RevOrb")
    plot_section_edges(axB, db_main, App.Vector(1, 0, 0), nx, "zy", "#EF6C00", lw=1.3, label="Dragon Burner MainBody")
    plot_section_edges(axB, hotend, App.Vector(1, 0, 0), nx, "zy", "#C62828", lw=1.8, label="Bambu X1/P1 Hotend")
    plot_section_edges(axB, orb_rev, App.Vector(1, 0, 0), nx, "zy", "#D81B60", lw=1.9, ls="-.",
                       label="Orbiter 2.5 Reversed (Front Motor Env)")
    axB.axvline(nz, color="#C62828", lw=0.9, ls=":")
    axB.annotate(
        f"Front LDO Ø36x20 Motor\nZ=[{rev_chk['motor_z_span_mm'][0]}, {rev_chk['motor_z_span_mm'][1]}]\n"
        f"({rev_chk['motor_front_vs_db_main_nose_mm']:+.1f} mm vs MainBody nose)",
        xy=(46.0, -32.0), xytext=(28.0, -25.0), fontsize=7.4, fontweight="bold", color="#AD1457",
        arrowprops=dict(arrowstyle="->", color="#AD1457", lw=1.1),
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#D81B60", lw=0.7, alpha=0.95),
    )
    axB.annotate("Rear roof open for\nCAN / Umbilical\n(Gearbox Z>=17.7)",
                 xy=(17.7, -56.0), xytext=(-19.5, -67.0), fontsize=7.4, fontweight="bold", color="#004D40",
                 arrowprops=dict(arrowstyle="->", color="#00695C", lw=1.1),
                 bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#00897B", lw=0.7, alpha=0.95))
    axB.set_xlim(-22.0, 74.0)
    axB.set_ylim(-146.0, -14.0)
    axB.set_aspect("equal")
    axB.grid(True, alpha=0.25)
    axB.set_xlabel("Z_adapter / +Forward (mm)")
    axB.set_ylabel("Y_adapter / +Up (mm)")
    axB.set_title("Option 2: Reverse-Orbiter Slim -15 mm (180° Front-Motor)", fontsize=10.5, fontweight="bold")
    axB.legend(loc="lower left", fontsize=6.4, framealpha=0.94)

    # --- Panel C: Top-Down XZ Section @ Bambu_Mount Top Seam (Mirrored Heatsets) ---
    axC = fig.add_subplot(gs[1, 0])
    plot_section_edges(axC, bm_orig, App.Vector(0, 1, 0), -80.2, "xz", "#9E9E9E", lw=1.2, ls="--",
                       label="Orig Bambu_Mount (-19.51 / +17.49)")
    plot_section_edges(axC, bm_rev, App.Vector(0, 1, 0), -80.2, "xz", "#00897B", lw=1.9,
                       label="Remixed Bambu_Mount_RevOrb (-17.49 / +19.51)")
    plot_section_edges(axC, slim, App.Vector(0, 1, 0), -80.2, "xz", "#1565C0", lw=1.7,
                       label="Slim Adapter @ Y=-80.2 (Mount Z=18.4)")
    plot_section_edges(axC, orb_reg, App.Vector(0, 1, 0), -47.8, "xz", "#8E24AA", lw=1.3, ls=":",
                       label="Regular Motor Plan @ Y=-47.8")
    plot_section_edges(axC, orb_rev, App.Vector(0, 1, 0), -47.8, "xz", "#D81B60", lw=1.3, ls="-.",
                       label="Reverse Motor Plan @ Y=-47.8")

    # Mark mirrored vs plugged heatset X centers (at Z = SLIM_NOZZLE[2] + 0.010)
    for xh, col, lbl in [
        (nx - 17.49, "#00897B", "Mirrored M3 Heatsets (-17.49 / +19.51)"),
        (nx + 19.51, "#00897B", None),
        (nx - 19.51, "#9E9E9E", "Plugged Orig (-19.51 / +17.49)"),
        (nx + 17.49, "#9E9E9E", None),
    ]:
        axC.add_patch(Circle((xh, nz + 0.010), 2.35, facecolor="none", edgecolor=col, lw=1.6, label=lbl))
    # Actual Z of heatset center is SLIM_NOZZLE[2] = nz!
    wm = val["checks"]["bambu_mount_rev_mirrored_heatset_wall_fraction"]
    axC.annotate(f"R=3.85 pad @ mirr_L\nwall={wm['mirr_L']*100:.1f}% solid\n(wire slot clear)",
                 xy=(nx - 17.49, nz), xytext=(1.0, 22.0), fontsize=7.5, fontweight="bold", color="#00695C",
                 arrowprops=dict(arrowstyle="->", color="#00695C", lw=1.0),
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#00897B", lw=0.6))
    axC.annotate(f"mirr_R wall={wm['mirr_R']*100:.1f}% solid",
                 xy=(nx + 19.51, nz), xytext=(52.0, 21.0), fontsize=7.5, fontweight="bold", color="#00695C",
                 arrowprops=dict(arrowstyle="->", color="#00695C", lw=1.0),
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#00897B", lw=0.6))
    axC.axhline(0.0, color="#455A64", lw=1.5, ls="--")
    axC.text(35.0, -2.5, "Steel Carriage Plane (Z=0)", ha="center", va="top", fontsize=7.8, color="#37474F", fontweight="bold")
    axC.set_xlim(-2.0, 72.0)
    axC.set_ylim(-6.0, 56.0)
    axC.set_aspect("equal")
    axC.grid(True, alpha=0.25)
    axC.set_xlabel("X_adapter Width (mm)")
    axC.set_ylabel("Z_adapter / +Forward (mm)")
    axC.set_title("Top-Down XZ Slice @ Y=-80.2 (Mirrored Heatsets) & Motor Footprint @ Y=-47.8",
                  fontsize=10, fontweight="bold")
    axC.legend(loc="upper right", fontsize=6.6, framealpha=0.94)

    # --- Panel D: 3D Iso Overlay (Slim Adapter + Reverse Orbiter Toolhead) ---
    axD = fig.add_subplot(gs[1, 1], projection="3d")
    draw_keys = [
        ("slim_adapter", (0.20, 0.50, 0.88, 0.90), 5000),
        ("bm_rev", (0.00, 0.54, 0.48, 0.85), 3500),
        ("om_rev", (0.20, 0.72, 0.65, 0.92), 3000),
        ("db_main", (0.96, 0.55, 0.15, 0.45), 4000),
        ("duct_r", (0.98, 0.55, 0.00, 0.60), 2500),
        ("hotend", (0.85, 0.18, 0.18, 0.95), 2500),
        ("orb_rev", (0.85, 0.11, 0.38, 0.42), 2000),
        ("orb_reg", (0.56, 0.14, 0.67, 0.18), 1500),
    ]
    all_pts = []
    for k, rgba, mf in draw_keys:
        v = np.asarray(parts[k]["v"], dtype=float)
        f = np.asarray(parts[k]["f"], dtype=int)
        all_pts.append(np.column_stack([v[:, 0], v[:, 2], v[:, 1]]))
        add_mesh_to_ax(axD, v, f, rgba, max_faces=mf, printer_axes=True)

    xx, zz = np.meshgrid([2.0, 68.0], [car_y, -35.0])
    yy = np.zeros_like(xx)
    axD.plot_surface(xx, yy, zz, color=(0.35, 0.38, 0.42, 0.20), shade=False)
    set_axes_equal(axD, np.vstack(all_pts), pad=3.0)
    axD.view_init(elev=14, azim=38)
    axD.set_xlabel("X (mm)")
    axD.set_ylabel("Y +Fwd (mm)")
    axD.set_zlabel("Z +Up (mm)")
    axD.set_title("3D Iso: Reverse-Orbiter Slim (Pink) vs Regular Motor Ghost (Purple)", fontsize=10, fontweight="bold")
    axD.set_facecolor("#FFFFFF")

    duct_clear = val["checks"]["duct_right_rear_clearance_to_carriage_mm"]
    fig.suptitle(
        "AD5M Dragon Burner -15.0 mm Slim Comparison: Regular (Rear Motor) vs Reverse-Orbiter (Front Motor)\n"
        f"Nozzle Z: 44.70 -> {nz:.2f} mm (+{val['checks']['nozzle_vs_custom_housing_r1_mm']:.2f} mm vs Custom Housing R1) | "
        f"Duct Carriage Gap: +{duct_clear:.2f} mm | Max Front Z: {rev_chk['total_toolhead_front_z_mm']:.1f} mm",
        fontsize=11.5, fontweight="bold", y=0.985,
    )
    out_path = OUT_DIR / "regular_vs_reverse_slim_comparison.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    App.closeDocument(doc.Name)
    return out_path


def _mesh_to_arrays(stl_path: Path) -> tuple[np.ndarray, np.ndarray]:
    m = Mesh.Mesh(str(stl_path))
    pts, tris = m.Topology
    v = np.array([[p.x, p.y, p.z] for p in pts], dtype=float)
    f = np.array(tris, dtype=int)
    return v, f


def render_printable_stls_multiview() -> Path:
    stls = [
        ("AD5M_Dragon_Burner_Slim_15mm_Adapter_R1.stl",
         "1. Slim 15mm Adapter (Print Back/Carriage Z=0 Down)\nUpper Arch Relieved, No Hall Magnets",
         (0.20, 0.50, 0.88, 1.0), (20, 45), True),
        ("AD5M_Dragon_Burner_Slim_15mm_Adapter_R1.stl",
         "1b. Slim 15mm Adapter — Rear Steel Carriage Face\nAll 5 M3 Bolt Holes & 42x9 Slot Unobstructed",
         (0.20, 0.50, 0.88, 1.0), (16, -135), True),
        ("Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1.stl",
         "2. Bambu_Mount_ReverseOrbiter (Print Rear Face Z=0 Down)\nMirrored (-17.49/+19.51) Heatsets + R=3.85 Boss",
         (0.00, 0.54, 0.48, 1.0), (28, -55), False),
        ("Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1.stl",
         "3. Orbiter2_Mount_ReverseOrbiter (Print Flat Base Z=0 Down)\n180° Rotated Around Filament Bore (4.75mm Fwd Shift)",
         (0.85, 0.11, 0.38, 1.0), (26, 40), False),
    ]

    fig = plt.figure(figsize=(14.5, 11.5), dpi=180)
    fig.patch.set_facecolor("#F7F8FA")
    for idx, (fname, title, rgba, (elev, azim), printer_axes) in enumerate(stls, 1):
        ax = fig.add_subplot(2, 2, idx, projection="3d")
        v, f = _mesh_to_arrays(OUT_DIR / fname)
        pts_plot = np.column_stack([v[:, 0], v[:, 2], v[:, 1]]) if printer_axes else v
        add_mesh_to_ax(ax, v, f, rgba, max_faces=9000, printer_axes=printer_axes)
        set_axes_equal(ax, pts_plot, pad=3.0)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        ax.set_title(title, fontsize=9.8, fontweight="bold")
        ax.set_facecolor("#FFFFFF")

    fig.suptitle(
        "Exported Manifold Printable STLs — AD5M Dragon Burner Slim -15 mm + Reverse Orbiter Pack (R1)",
        fontsize=12, fontweight="bold", y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out_path = OUT_DIR / "slim_parts_multiview.png"
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def main() -> None:
    parts = {p["name"]: p for p in json.loads(PREVIEW_JSON.read_text(encoding="utf-8"))}
    val = json.loads(VAL_JSON.read_text(encoding="utf-8"))
    p1 = render_comparison(parts, val)
    p2 = render_printable_stls_multiview()
    print(f"Rendered:\n  {p1}\n  {p2}", flush=True)


if __name__ == "__main__":
    main()
