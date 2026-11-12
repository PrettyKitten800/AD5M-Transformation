"""
Render multi-view 3D assemblies and exact FreeCAD BRep cross-sections for
AD5M Dragon Burner Eddy Adapter R1.

Outputs in outputs/Dragon_Burner_AD5M_Eddy_Adapter_R1/:
  - adapter_remix_multiview.png    : 4-panel shaded views of the remixed adapter STL/BRep
  - toolhead_full_assembly.png     : 4-panel aligned toolhead + Dragon Burner + Hotend + Eddy Duo + steel carriage
  - engineering_sections.png       : Exact FreeCAD Shape.section() 1:1 slices with critical dimensions & clearances
"""

from __future__ import annotations

import json
from pathlib import Path

import FreeCAD as App
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import Part


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs/Dragon_Burner_AD5M_Eddy_Adapter_R1"
FCSTD_PATH = OUT_DIR / "AD5M_Dragon_Burner_Eddy_Adapter_R1.FCStd"
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


def add_mesh_to_ax(ax, verts_xyz: np.ndarray, faces: np.ndarray, rgba: tuple[float, float, float, float],
                   max_faces: int = 8000) -> None:
    """Transform (X_1406, Y_1406=UP, Z_1406=FWD) -> plot (X=right, Y=fwd, Z=up) and shade."""
    if len(faces) == 0:
        return
    if len(faces) > max_faces:
        step = max(1, len(faces) // max_faces)
        faces = faces[::step]
    # Printer-natural axes: plot_X = X_1406, plot_Y = Z_1406 (+fwd), plot_Z = Y_1406 (+up)
    pts = np.column_stack([verts_xyz[:, 0], verts_xyz[:, 2], verts_xyz[:, 1]])
    tris = pts[faces]
    poly = Poly3DCollection(tris, facecolors=rgba, edgecolors=(0.12, 0.12, 0.12, 0.08),
                            linewidths=0.15, shade=True)
    ax.add_collection3d(poly)


def render_adapter_multiview(parts: dict, val: dict) -> Path:
    ad = parts["adapter"]
    v = np.asarray(ad["v"], dtype=float)
    f = np.asarray(ad["f"], dtype=int)
    pts_plot = np.column_stack([v[:, 0], v[:, 2], v[:, 1]])

    views = [
        ("Rear-Bottom Iso (-Z Carriage / Mode-A Pocket Entry)", (18, -135)),
        ("Rear Orthographic (-Z Carriage Face & 5th Slot Clear)", (0, -90)),
        ("Front-Right Iso (+Z Hotend Baffle & Hall Magnets)", (18, 45)),
        ("Right Profile (+X -> Left; Baffle, Ears & USB Channel)", (0, 0)),
    ]

    fig = plt.figure(figsize=(14, 12), dpi=180)
    fig.patch.set_facecolor("#F7F8FA")
    for idx, (title, (elev, azim)) in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, idx, projection="3d")
        add_mesh_to_ax(ax, v, f, (0.20, 0.50, 0.88, 1.0), max_faces=12000)

        # Overlay Eddy coil center & Hall magnet pocket markers
        cx, cy, cz = val["datums_in_adapter_frame_mm"]["coil_center_nominal"]
        ax.scatter([cx], [cz], [cy], color="#D32F2F", s=45, zorder=10, label="Coil ctr (+2.5, 35.0 mm)")
        for ym in (-57.258, -62.248):
            ax.scatter([64.5], [29.40], [ym], color="#2E7D32", s=35, zorder=10)

        set_axes_equal(ax, pts_plot, pad=5.0)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("X width (mm)")
        ax.set_ylabel("Y_printer +Fwd (mm)")
        ax.set_zlabel("Z_printer +Up (mm)")
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_facecolor("#FFFFFF")

    fig.suptitle(
        "Printables #1406257 (v11) AD5M Dragon Burner Adapter — Mode A Rear Eddy Duo Remix (R1)\n"
        f"Watertight Single Solid | Vol: {val['volume_mm3']:,.1f} mm³ | Min Front Baffle: {val['collisions_and_clearances']['min_front_baffle_thickness_mm']} mm",
        fontsize=12, fontweight="bold", y=0.98
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out_path = OUT_DIR / "adapter_remix_multiview.png"
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def render_full_assembly(parts: dict, val: dict) -> Path:
    views = [
        ("Rear-Left Iso (Steel Carriage Side & Drop-Down Pocket)", (15, -140)),
        ("Right Side Profile (35.0 mm Offset, +2.5 mm Height & Baffle)", (0, 0)),
        ("Front-Right Iso (Dragon Burner + Bambu Hotend Stack)", (15, 40)),
        ("Bottom-Up View (-Z/+Z Alignment, Coil Centered at X=0)", (-75, -90)),
    ]

    palette = {
        "adapter": (0.20, 0.50, 0.88, 0.92),
        "db_bambu": (0.22, 0.65, 0.30, 0.78),
        "db_main": (0.96, 0.55, 0.15, 0.48),
        "hotend": (0.85, 0.18, 0.18, 0.92),
        "coil90": (0.58, 0.15, 0.72, 1.0),
        "usb4p": (0.00, 0.60, 0.52, 1.0),
    }

    all_pts = []
    for p in parts.values():
        vv = np.asarray(p["v"], dtype=float)
        all_pts.append(np.column_stack([vv[:, 0], vv[:, 2], vv[:, 1]]))
    all_pts_arr = np.vstack(all_pts)

    nx, ny, nz = val["datums_in_adapter_frame_mm"]["nozzle_tip"]
    cx, cy, cz = val["datums_in_adapter_frame_mm"]["coil_center_nominal"]
    car_y = val["datums_in_adapter_frame_mm"]["stock_steel_carriage_bottom"][1]

    fig = plt.figure(figsize=(15, 13), dpi=180)
    fig.patch.set_facecolor("#F7F8FA")
    for idx, (title, (elev, azim)) in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, idx, projection="3d")
        for key, rgba in palette.items():
            if key not in parts:
                continue
            v = np.asarray(parts[key]["v"], dtype=float)
            f = np.asarray(parts[key]["f"], dtype=int)
            add_mesh_to_ax(ax, v, f, rgba, max_faces=7000)

        # Draw translucent stock steel carriage envelope (Z <= 0, Y >= -124.801)
        xx, zz = np.meshgrid([0.0, 70.0], [car_y, -30.0])
        yy = np.zeros_like(xx)
        ax.plot_surface(xx, yy, zz, color=(0.35, 0.38, 0.42, 0.25), shade=False)

        ax.scatter([nx, cx], [nz, cz], [ny, cy], color=["#FF1744", "#AA00FF"], s=50, depthshade=False)
        ax.plot([cx, nx], [cz, cz], [cy, cy], "k--", linewidth=1.2)
        ax.plot([nx, nx], [cz, nz], [cy, ny], "r--", linewidth=1.2)

        set_axes_equal(ax, all_pts_arr, pad=4.0)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("X width (mm)")
        ax.set_ylabel("Y_printer +Fwd (mm)")
        ax.set_zlabel("Z_printer +Up (mm)")
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_facecolor("#FFFFFF")

    fig.suptitle(
        "Full Toolhead Stack: Remixed #1406257 + Dragon Burner v8 + Bambu X1/P1 Hotend + De-Shelled BTT Eddy Duo\n"
        "Nozzle Tip: (0.0, 0.0, 0.0) | Eddy Coil Center: (X=0.0, Y=35.0 mm behind, Z=+2.5 mm above, -11.1 mm below steel carriage)",
        fontsize=11.5, fontweight="bold", y=0.98
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out_path = OUT_DIR / "toolhead_full_assembly.png"
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_section_edges(ax, shape: Part.Shape, normal: App.Vector, d: float,
                       proj: str, color: str, lw: float = 1.6, ls: str = "-",
                       label: str | None = None, zorder: int = 4) -> None:
    """Intersect BRep shape with plane normal.dot(P) = d and draw discretized edges."""
    if abs(normal.x) > 0.5:
        p0 = App.Vector(d, 100.0, -50.0)     # spans Y=[-200,+100], Z=[-50,+250]
    elif abs(normal.y) > 0.5:
        p0 = App.Vector(-50.0, d, -50.0)     # spans X=[-50,+250], Z=[-50,+250]
    else:
        p0 = App.Vector(-50.0, -200.0, d)    # spans X=[-50,+250], Y=[-200,+100]
    sec = shape.section(Part.makePlane(300, 300, p0, normal))

    first = True
    for e in sec.Edges:
        pts = e.discretize(Deflection=0.05)
        if len(pts) < 2:
            continue
        if proj == "zy":      # horizontal=Z_1406 (Fwd), vertical=Y_1406 (Up)
            xs = [p.z for p in pts]
            ys = [p.y for p in pts]
        elif proj == "xz":    # horizontal=X_1406 (Right), vertical=Z_1406 (Fwd)
            xs = [p.x for p in pts]
            ys = [p.z for p in pts]
        elif proj == "xy":    # horizontal=X_1406 (Right), vertical=Y_1406 (Up)
            xs = [p.x for p in pts]
            ys = [p.y for p in pts]
        else:
            raise ValueError(proj)
        ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls,
                label=(label if first else None), zorder=zorder)
        first = False


def render_engineering_sections(val: dict) -> Path:
    doc = App.openDocument(str(FCSTD_PATH))
    shapes = {o.Name: o.Shape for o in doc.Objects}

    ad = shapes["PRINT_RemixedAdapterR1"]
    base = shapes["REF_Base1406257"]
    db_b = shapes["REF_DragonBurnerBambuMount"]
    db_m = shapes["REF_DragonBurnerMainBody"]
    hot = shapes["REF_BambuHotend"]
    coil = shapes["REF_EddyCoil90_Nom"]
    usb = shapes["REF_EddyUSB4p_Nom"]
    sw = shapes["REF_EddySwitch_Nom"]

    nx, ny, nz = val["datums_in_adapter_frame_mm"]["nozzle_tip"]
    cx, cy, cz = val["datums_in_adapter_frame_mm"]["coil_center_nominal"]
    car_y = val["datums_in_adapter_frame_mm"]["stock_steel_carriage_bottom"][1]

    fig = plt.figure(figsize=(16, 11.5), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0], width_ratios=[1.25, 1.0], hspace=0.28, wspace=0.22)

    # --- Panel A (Top-left wide): Centerline YZ slice at X = 34.924 mm ---
    axA = fig.add_subplot(gs[0, :])
    axA.add_patch(Rectangle((-20.0, car_y), 20.0, 95.0, facecolor="#90A4AE", alpha=0.35, edgecolor="#455A64", lw=1.2, label="Stock Steel Carriage (Z<=0, Y>=-124.80)"))
    plot_section_edges(axA, base, App.Vector(1, 0, 0), cx, "zy", "#9E9E9E", lw=1.1, ls="--", label="Original #1406257 Outline")
    plot_section_edges(axA, ad, App.Vector(1, 0, 0), cx, "zy", "#1565C0", lw=2.1, label="Remixed Adapter R1 (cut section)")
    plot_section_edges(axA, db_b, App.Vector(1, 0, 0), cx, "zy", "#2E7D32", lw=1.4, label="Dragon Burner Bambu Mount")
    plot_section_edges(axA, db_m, App.Vector(1, 0, 0), cx, "zy", "#EF6C00", lw=1.3, label="Dragon Burner MainBody / 3010 Exhaust Zone")
    plot_section_edges(axA, hot, App.Vector(1, 0, 0), cx, "zy", "#C62828", lw=1.8, label="Bambu X1/P1 Hotend & Nozzle")
    plot_section_edges(axA, coil, App.Vector(1, 0, 0), cx, "zy", "#6A1B9A", lw=2.0, label="EDDY Coil90 (90 deg PCB)")
    plot_section_edges(axA, usb, App.Vector(1, 0, 0), cx, "zy", "#00897B", lw=1.8, label="EDDY 4-pin 90 deg USB (inward)")
    plot_section_edges(axA, sw, App.Vector(1, 0, 0), cx, "zy", "#AD1457", lw=1.6, label="EDDY Switch")

    # Bed plane & Datums
    axA.axhline(ny, color="#D50000", lw=1.1, ls=":", label=f"Nozzle Tip Plane Y={ny:.2f}")
    axA.axhline(cy, color="#6A1B9A", lw=0.9, ls="-.")
    axA.axvline(cz, color="#6A1B9A", lw=0.9, ls="-.")
    axA.axvline(nz, color="#D50000", lw=0.9, ls=":")
    axA.annotate("", xy=(nz, ny + 0.6), xytext=(cz, ny + 0.6),
                 arrowprops=dict(arrowstyle="<->", color="k", lw=1.2))
    axA.text((cz + nz) / 2.0, ny + 1.8, "35.00 mm behind nozzle", ha="center", va="bottom", fontsize=8.3,
             fontweight="bold", bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85))
    axA.annotate("+2.5 mm above nozzle\n(-11.1 mm below carriage)", xy=(cz, cy), xytext=(-22.0, -142.5),
                 arrowprops=dict(arrowstyle="->", color="#6A1B9A", lw=1.1), fontsize=8, color="#6A1B9A", fontweight="bold")
    axA.annotate("Solid Front Thermal Baffle\n4.3 mm main / 2.7 mm over USB (>=2.4 mm)\n11.6 mm air gap to DB MainBody",
                 xy=(21.5, -124.0), xytext=(24.5, -132.5), zorder=10,
                 arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.1), fontsize=7.8, color="#0D47A1", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#1565C0", lw=0.6, alpha=0.92))
    axA.annotate("Upward USB Relief Channel\n(Z=13.5..20.6) exits into\n#1406257 20x23.4 central tunnel",
                 xy=(17.0, -88.0), xytext=(-14.0, -88.0), zorder=10,
                 arrowprops=dict(arrowstyle="->", color="#00695C", lw=1.1), fontsize=7.8, color="#004D40", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#00695C", lw=0.6, alpha=0.92))
    axA.annotate("5th Bolt Slot Corridor\nY=[-117.3, -108.3], Z=3.4..12.5 unobstructed",
                 xy=(7.5, -112.8), xytext=(-27.5, -114.5), zorder=10,
                 arrowprops=dict(arrowstyle="->", color="#37474F", lw=1.1), fontsize=7.8, color="#263238", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#455A64", lw=0.6, alpha=0.92))

    axA.set_xlim(-29.0, 62.0)
    axA.set_ylim(-144.5, -72.0)
    axA.set_aspect("equal")
    axA.grid(True, alpha=0.25)
    axA.set_xlabel("Z_adapter / Forward toward Hotend (mm)")
    axA.set_ylabel("Y_adapter / Vertical UP (mm)")
    axA.set_title("Section A-A: Centerline YZ Profile (X = 34.924 mm | Nozzle Centerline)", fontsize=10.5, fontweight="bold")
    axA.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7.4, ncol=1, framealpha=0.96)

    # --- Panel B (Bottom-left): XZ cross sections at Y=-128.5 (M3 ears) & Y=-116.45 (5th bolt) ---
    axB = fig.add_subplot(gs[1, 0])
    plot_section_edges(axB, ad, App.Vector(0, 1, 0), -128.5, "xz", "#1565C0", lw=2.0, label="Y=-128.5 mm: Mode-A Pocket, 26.61 mm M3 Ears & Nut Channels")
    plot_section_edges(axB, ad, App.Vector(0, 1, 0), -116.45, "xz", "#EF6C00", lw=1.4, ls="--", label="Y=-116.45 mm: Trunk Clear of 5th Bolt Candidates")
    # Show 18.10 x 6 mm lower housing + 18 x 11 mm coil zone
    axB.add_patch(Rectangle((cx - 9.05, 12.95), 18.10, 5.95, facecolor="#CE93D8", alpha=0.45, edgecolor="#6A1B9A", lw=1.2, label="Eddy Lower Housing Env (18.10 mm)"))
    axB.add_patch(Rectangle((cx - 9.00, cz - 5.50), 18.00, 11.00, facecolor="#B39DDB", alpha=0.35, edgecolor="#4527A0", lw=1.2, label="18x11 Bare Coil Env (Center Z=+9.70)"))
    # 5th bolt candidates X = cx +/- 14.0 mm (Z=0..11.5 head + tool access)
    for sx in (cx - 14.0, cx + 14.0):
        axB.add_patch(Rectangle((sx - 2.75, 0.0), 5.50, 11.50, facecolor="#FFAB91", alpha=0.45, edgecolor="#D84315", lw=1.1,
                                label=("5th Carriage Bolt Access (X=±14.0)" if sx < cx else None)))
    axB.annotate("", xy=(cx + 13.305, 13.0), xytext=(cx - 13.305, 13.0),
                 arrowprops=dict(arrowstyle="<->", color="b", lw=1.2))
    axB.text(cx, 10.7, "26.61 mm M3 pitch\n(±1.0 mm Z travel)", ha="center", va="bottom", fontsize=7.8, color="#0D47A1", fontweight="bold")
    axB.text(cx, 20.8, "4.3 mm Solid Baffle", ha="center", va="bottom", fontsize=7.8, color="#0D47A1", fontweight="bold")

    axB.set_xlim(10.0, 60.0)
    axB.set_ylim(-1.0, 26.0)
    axB.set_aspect("equal")
    axB.grid(True, alpha=0.25)
    axB.set_xlabel("X_adapter (mm)")
    axB.set_ylabel("Z_adapter / Forward (mm)")
    axB.set_title("Section B-B: Horizontal XZ Audit (M3 Ears @ Y=-128.5 & 5th Bolt @ Y=-116.45)", fontsize=10, fontweight="bold")
    axB.legend(loc="lower right", fontsize=6.8, framealpha=0.92)

    # --- Panel C (Bottom-right): XY section at Z=17.5 (USB channel) & Hall magnet check ---
    axC = fig.add_subplot(gs[1, 1])
    plot_section_edges(axC, base, App.Vector(0, 0, 1), 17.5, "xy", "#9E9E9E", lw=1.0, ls="--", label="Original #1406257 @ Z=17.5")
    plot_section_edges(axC, ad, App.Vector(0, 0, 1), 17.5, "xy", "#1565C0", lw=1.9, label="Remixed Adapter @ Z=17.5 (USB Channel + Nut Slots)")
    plot_section_edges(axC, usb, App.Vector(0, 0, 1), 17.5, "xy", "#00897B", lw=1.8, label="EDDY 4-pin 90 deg USB @ Z=17.5")
    # Annotate heatsets, Hall magnets (+X wall), and central tunnel
    for hx in (22.407, 47.406):
        axC.add_patch(plt.Circle((hx, -86.681), 2.30, facecolor="#FFF59D", edgecolor="#F57F17", lw=1.2,
                                 label=("DB Heatset M3x5x4 (X=22.4/47.4)" if hx < 30 else None)))
    for ym in (-57.258, -62.248):
        axC.add_patch(plt.Circle((63.9, ym), 1.55, facecolor="#A5D6A7", edgecolor="#1B5E20", lw=1.3,
                                 label=("Hall Magnet Pockets (X=62.9..64.9, Z=29.4)" if ym > -60 else None)))
    axC.annotate("20.0 mm Central\nCable Tunnel (open)", xy=(34.92, -74.0), xytext=(-2.0, -56.0),
                 arrowprops=dict(arrowstyle="->", color="#00695C", lw=1.1), fontsize=7.6, color="#004D40", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#00695C", lw=0.6, alpha=0.90))
    axC.annotate("Hall Magnet Pockets\n36.0 mm clear of remix", xy=(63.9, -62.25), xytext=(69.0, -74.0),
                 arrowprops=dict(arrowstyle="->", color="#1B5E20", lw=1.1), fontsize=7.6, color="#1B5E20", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#1B5E20", lw=0.6, alpha=0.90))

    axC.set_xlim(-4.0, 98.0)
    axC.set_ylim(-142.0, -45.0)
    axC.set_aspect("equal")
    axC.grid(True, alpha=0.25)
    axC.set_xlabel("X_adapter (mm)")
    axC.set_ylabel("Y_adapter / Vertical UP (mm)")
    axC.set_title("Section C-C: Frontal XY Slice @ Z=17.5 mm (USB Channel, Heatsets & Magnets)", fontsize=10, fontweight="bold")
    axC.legend(loc="lower right", fontsize=6.5, framealpha=0.94)

    App.closeDocument(doc.Name)

    fig.suptitle(
        "AD5M Dragon Burner #1406257 Mode-A Eddy Duo Remix (R1) — Exact BRep Cross-Section Verification",
        fontsize=12.5, fontweight="bold", y=0.985
    )
    out_path = OUT_DIR / "engineering_sections.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    parts = {p["name"]: p for p in json.loads(PREVIEW_JSON.read_text(encoding="utf-8"))}
    val = json.loads(VAL_JSON.read_text(encoding="utf-8"))
    p1 = render_adapter_multiview(parts, val)
    p2 = render_full_assembly(parts, val)
    p3 = render_engineering_sections(val)
    print(f"Rendered:\n  {p1}\n  {p2}\n  {p3}", flush=True)


if __name__ == "__main__":
    main()
