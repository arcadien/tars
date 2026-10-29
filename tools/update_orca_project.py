"""Refresh the meshes of an Orca/Bambu project 3MF from the current STLs, keeping plates, positions and settings.

usage: update_orca_project.py project.3mf [--check] [--out other.3mf]

Each object file 3D/Objects/<name>_<n>.model is matched to an STL through NAME_TO_STL. Orca stores each object's
mesh centred on its own bounding box (the plate position lives in the build item transform), so the new mesh is
oriented like stl2_3mf.py does (long side along the stored mesh's long axis), centred, and written in place; the item's z offset is set to
half the new height so the part still sits on the bed. The original file is copied to backups/ first.
--check only compares the current STLs with the meshes in the project (no write). When every mesh is up to date the
project is left untouched (no backup, no rewrite).
"""
import math
import os
import re
import shutil
import sys
import time
import zipfile

NAME_TO_STL = {
    "leg_left_bottom": "tars4_col0_bottom", "leg_left_top": "tars4_col0_top",
    "mid_left_bottom": "tars4_col1_bottom", "mid_left_top": "tars4_col1_top",
    "mid_right_bottom": "tars4_col2_bottom", "mid_right_top": "tars4_col2_top",
    "leg_right_bottom": "tars4_col3_bottom", "leg_right_top": "tars4_col3_top",
    "lid_leg_left_bottom": "tars4_lid_leg_sd_bottom", "lid_leg_right_bottom": "tars4_lid_leg_bottom",
    "lid_leg_left_top": "tars4_lid_leg_top", "lid_leg_right_top": "tars4_lid_leg_top",
    "lid_mid_left_bottom": "tars4_lid_mid_left_bottom", "lid_mid_right_bottom": "tars4_lid_mid_bottom",
    "lid_mid_left_top": "tars4_lid_mid_left_top", "lid_mid_right_top": "tars4_lid_mid_top",
    "splints": "tars4_splint", "tube_collars": "tars4_collar", "black_inserts": "tars4_inserts", "black_inserts_speaker": "tars4_inserts_speaker",
    # CR-10 project (tars4_cr10.3mf, one-piece parts)
    "cr10_leg_left": "tars4_cr10_col0", "cr10_mid_left": "tars4_cr10_col1", "cr10_mid_right": "tars4_cr10_col2",
    "cr10_leg_right": "tars4_cr10_col3", "cr10_lid_leg_left": "tars4_cr10_lid_leg_sd", "cr10_lid_mid_left": "tars4_cr10_lid_mid_left",
    "cr10_lid_mid_right": "tars4_cr10_lid_mid", "cr10_lid_leg_right": "tars4_cr10_lid_leg",
}


def read_stl(path):
    txt = open(path).read()
    pts = [tuple(map(float, m)) for m in re.findall(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", txt)]
    verts, index, tris = [], {}, []
    for i in range(0, len(pts), 3):
        tri = []
        for p in pts[i:i + 3]:
            key = tuple(round(c, 5) for c in p)
            if key not in index:
                index[key] = len(verts)
                verts.append(key)
            tri.append(index[key])
        if len(set(tri)) == 3:
            tris.append(tri)
    return verts, tris


def bbox(verts):
    return [min(v[i] for v in verts) for i in range(3)], [max(v[i] for v in verts) for i in range(3)]


def oriented_centred(verts, long_x=True):
    lo, hi = bbox(verts)
    if (hi[1] - lo[1] > hi[0] - lo[0]) == long_x:  # same turn as stl2_3mf.py: long side along X (or Y, see main)
        verts = [(v[1], -v[0], v[2]) for v in verts]
        lo, hi = bbox(verts)
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    return [(v[0] - c[0], v[1] - c[1], v[2] - c[2]) for v in verts], [hi[i] - lo[i] for i in range(3)]


def mesh_xml(verts, tris):
    vx = "\n".join(f'     <vertex x="{v[0]:.7g}" y="{v[1]:.7g}" z="{v[2]:.7g}"/>' for v in verts)
    tx = "\n".join(f'     <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>' for t in tris)
    return f"<mesh>\n    <vertices>\n{vx}\n    </vertices>\n    <triangles>\n{tx}\n    </triangles>\n   </mesh>"


def main():
    args = sys.argv[1:]
    check = "--check" in args
    out = None
    if "--out" in args:
        out = args[args.index("--out") + 1]
        args = [a for a in args if a not in ("--out", out)]
    args = [a for a in args if a != "--check"]
    proj = args[0]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repo root
    stl_dir = os.path.join(root, "mechanical", "stl")
    zin = zipfile.ZipFile(proj)
    model = zin.read("3D/3dmodel.model").decode()
    # object file -> its build item (through the wrapper object that references it)
    wrapper = {path: oid for oid, path in re.findall(r'<object id="(\d+)"[^>]*>\s*<components>\s*<component p:path="([^"]+)"', model)}

    new_files, z_of_item, problems = {}, {}, []
    for info in zin.infolist():
        m = re.match(r"3D/Objects/(.+)_(\d+)\.model$", info.filename)
        if not m:
            continue
        name = m.group(1)
        stl = NAME_TO_STL.get(name)
        if not stl or not os.path.exists(os.path.join(stl_dir, stl + ".stl")):
            problems.append(f"{name}: no STL mapped, left unchanged")
            continue
        old = zin.read(info.filename).decode()
        old_v = [tuple(map(float, t)) for t in re.findall(r'<vertex x="(\S+)" y="(\S+)" z="(\S+)"/>', old)]
        verts, tris = read_stl(os.path.join(stl_dir, stl + ".stl"))
        # keep the stored mesh's long axis: X in the Ender 3 project, Y in the CR-10 one (stl2_3mf at 90 deg)
        olo, ohi = bbox(old_v)
        long_x = ohi[0] - olo[0] >= ohi[1] - olo[1]
        verts, size = oriented_centred(verts, long_x)
        _, old_size = oriented_centred(old_v, long_x)
        same = len(old_v) == len(verts) and all(max(abs(a[k] - b[k]) for k in range(3)) < 0.01
                                                for a, b in zip(sorted(old_v), sorted(verts)))
        print(f"{name:22s} {stl:22s} old {old_size[0]:6.1f} x {old_size[1]:5.1f} x {old_size[2]:5.1f}  "
              f"new {size[0]:6.1f} x {size[1]:5.1f} x {size[2]:5.1f}  {'unchanged' if same else 'UPDATED'}")
        if abs(size[0] - old_size[0]) > 5 or abs(size[1] - old_size[1]) > 5:
            problems.append(f"{name}: size changed a lot, check its place on the plate")
        if same:
            continue
        new_files[info.filename] = re.sub(r"<mesh>.*?</mesh>", lambda _: mesh_xml(verts, tris), old, count=1, flags=re.S)
        z_of_item[wrapper.get("/" + info.filename)] = size[2] / 2

    for p in problems:
        print("NOTE:", p)
    if check:
        return
    if not new_files:   # nothing to refresh: no backup, no rewrite (the hooks would see a spurious change)
        print("up to date:", proj)
        return

    # build items: keep x/y and rotation, set z to half the new height
    def fix_item(mo):
        oid, tr = mo.group(1), mo.group(2).split()
        if oid in z_of_item and z_of_item[oid] is not None:
            tr[11] = f"{z_of_item[oid]:.6g}"
        return mo.group(0).replace(mo.group(2), " ".join(tr))
    model = re.sub(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"', fix_item, model)

    if out is None:
        os.makedirs(os.path.join(root, "backups"), exist_ok=True)
        bak = os.path.join(root, "backups", os.path.basename(proj) + time.strftime(".bak-%Y%m%d-%H%M%S"))
        shutil.copy2(proj, bak)
        print("backup:", bak)
        out = proj
    tmp = out + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            if info.filename == "3D/3dmodel.model":
                data = model.encode()
            elif info.filename in new_files:
                data = new_files[info.filename].encode()
            else:
                data = zin.read(info.filename)
            zout.writestr(info, data)
    zin.close()
    os.replace(tmp, out)
    print("written:", out)


if __name__ == "__main__":
    main()
