"""Pack several ASCII STL files into one 3MF (one named object per part), laid out on the bed.

usage: stl2_3mf.py [--angle=DEG | --long-x] out.3mf bed_w bed_d name=file.stl [name=file.stl+name=file.stl ...]

Each part is dropped onto z = 0 and turned so its long side runs along X; the parts are placed as parallel strips
side by side, then the whole layout is turned by DEG around Z and centred on the bed.
Parts joined with "+" share one strip, placed end to end (e.g. two short halves in the length of a long one).
  default      DEG = 90: long sides along Y (e.g. CR-10 300 x 300)
  --long-x     DEG = 0: long sides along X
  --angle=DEG  diagonal layout, e.g. --angle=18 to fit 248 mm parts on an Ender 3 (250 x 226)
Prints a WARNING when the layout does not fit the bed.
"""
import math
import re
import sys
import zipfile

SPACING = 4.0


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


def shift(verts, d):
    return [(v[0] + d[0], v[1] + d[1], v[2] + d[2]) for v in verts]


def rotate_z(verts, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(c * v[0] - s * v[1], s * v[0] + c * v[1], v[2]) for v in verts]


def main():
    args = sys.argv[1:]
    angle = 90.0
    rest = []
    for a in args:
        if a == "--long-x":
            angle = 0.0
        elif a.startswith("--angle="):
            angle = float(a.split("=", 1)[1])
        else:
            rest.append(a)
    out, bed_w, bed_d = rest[0], float(rest[1]), float(rest[2])
    strips = [[p.split("=", 1) for p in a.split("+")] for a in rest[3:]]

    # 1. each part: long side along X, min corner at the origin; strips stacked along Y, parts of a strip end to end
    placed, v_cursor = [], 0.0
    for strip in strips:
        # diagonal layouts: stagger each strip along its length so the strips line up across the bed
        u_cursor = v_cursor * math.tan(math.radians(angle)) if angle % 90 else 0.0
        strip_w = 0.0
        for name, path in strip:
            verts, tris = read_stl(path)
            lo, hi = bbox(verts)
            if hi[1] - lo[1] > hi[0] - lo[0]:
                verts = rotate_z(verts, -90)
                lo, hi = bbox(verts)
            verts = shift(verts, (-lo[0] + u_cursor, -lo[1] + v_cursor, -lo[2]))
            u_cursor += hi[0] - lo[0] + SPACING
            strip_w = max(strip_w, hi[1] - lo[1])
            placed.append((name, verts, tris, hi[0] - lo[0], hi[1] - lo[1]))
        v_cursor += strip_w + SPACING

    # 2. turn the whole layout, centre it on the bed
    placed = [(n, rotate_z(v, angle), t, L, w) for n, v, t, L, w in placed]
    all_lo, all_hi = bbox([p for _, v, _, _, _ in placed for p in v])
    off = (bed_w / 2 - (all_lo[0] + all_hi[0]) / 2, bed_d / 2 - (all_lo[1] + all_hi[1]) / 2, 0)
    size = (all_hi[0] - all_lo[0], all_hi[1] - all_lo[1])
    print(f"layout {size[0]:.1f} x {size[1]:.1f} mm at {angle:g} deg on a {bed_w:g} x {bed_d:g} bed")
    if size[0] > bed_w or size[1] > bed_d:
        print("WARNING: layout does not fit the bed")

    # 3. write: each object's mesh starts at its own bbox minimum, the item transform puts it in place
    objects, items = [], []
    for oid, (name, verts, tris, L, w) in enumerate(placed, start=1):
        lo, _ = bbox(verts)
        local = shift(verts, (-lo[0], -lo[1], -lo[2]))
        vx = "\n".join(f'<vertex x="{v[0]:.5f}" y="{v[1]:.5f}" z="{v[2]:.5f}"/>' for v in local)
        tx = "\n".join(f'<triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>' for t in tris)
        objects.append(f'<object id="{oid}" name="{name}" type="model"><mesh><vertices>\n{vx}\n</vertices><triangles>\n{tx}\n</triangles></mesh></object>')
        px, py = lo[0] + off[0], lo[1] + off[1]
        items.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {px:.3f} {py:.3f} 0"/>')
        print(f"  {name}: {L:.1f} x {w:.1f}")

    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
             '<resources>\n' + "\n".join(objects) + '\n</resources>\n<build>\n' + "\n".join(items) + '\n</build>\n</model>\n')
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


if __name__ == "__main__":
    main()
