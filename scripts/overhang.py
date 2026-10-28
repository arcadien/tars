# /// script
# requires-python = ">=3.10"
# dependencies = ["trimesh>=4", "numpy", "scipy", "networkx"]
# ///
"""Flag unsupported overhangs in print-oriented STLs.

usage: uv run scripts/overhang.py [--limit DEG] [--allow scripts/overhang_allow.json] [--report] stl/tars4_x.stl ...

A face overhangs when it faces down more than LIMIT degrees from vertical (a vertical wall is 0, a ceiling is 90).
Faces lying on the bed (z = 0) are ignored. Adjacent overhanging faces are merged into regions. A flat (ceiling)
region narrower than BRIDGE_W (mean width 2 * area / perimeter, e.g. the 0.8 mm decor grooves on the bed face) is a
bridge and passes. Any other region larger than MIN_AREA is a failure unless an entry of the allow file covers it:
same part, region centroid inside the entry's box (print coordinates, mm), with the reason it prints without support.
--report lists every region above MIN_AREA with its box, allowed or not, to write new allow entries.
Exit code 1 when an unallowed region is found.
"""
import json
import os
import sys

import numpy as np
import trimesh

LIMIT = 50.0     # degrees from vertical
MIN_AREA = 200.0 # mm^2 (2 cm^2)
BED_EPS = 0.05   # faces this close to z min sit on the bed
FLAT = 85.0      # a region steeper than this everywhere is a ceiling (bridge candidate)
BRIDGE_W = 3.0   # mm: ceilings narrower than this bridge between their side walls


def regions(mesh, limit=LIMIT):
    n = mesh.face_normals
    # angle from vertical of a down-facing face: asin(-nz)
    ang = np.degrees(np.arcsin(np.clip(-n[:, 2], -1, 1)))
    zmin = mesh.bounds[0][2]
    on_bed = np.all(mesh.vertices[mesh.faces][:, :, 2] < zmin + BED_EPS, axis=1)
    bad = (ang > limit) & ~on_bed
    idx = np.nonzero(bad)[0]
    if len(idx) == 0:
        return []
    keep = np.zeros(len(mesh.faces), bool)
    keep[idx] = True
    adj = mesh.face_adjacency
    adj = adj[keep[adj[:, 0]] & keep[adj[:, 1]]]
    groups = trimesh.graph.connected_components(adj, nodes=idx, min_len=1)
    out = []
    for g in groups:
        area = float(mesh.area_faces[g].sum())
        if area < MIN_AREA:
            continue
        pts = mesh.vertices[mesh.faces[g]].reshape(-1, 3)
        e = np.sort(mesh.faces[g][:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
        u, cnt = np.unique(e, axis=0, return_counts=True)
        rim = u[cnt == 1]
        perim = float(np.linalg.norm(mesh.vertices[rim[:, 0]] - mesh.vertices[rim[:, 1]], axis=1).sum())
        min_angle = float(np.degrees(np.arcsin(np.clip(-mesh.face_normals[g][:, 2], -1, 1))).min())
        width = 2 * area / perim if perim else 0.0
        c = (mesh.triangles_center[g] * mesh.area_faces[g][:, None]).sum(0) / area
        out.append({"area": area, "centroid": c.round(1).tolist(), "lo": pts.min(0).round(1).tolist(),
                    "hi": pts.max(0).round(1).tolist(), "width": width,
                    "bridge": min_angle >= FLAT and width <= BRIDGE_W, "max_angle": float(np.degrees(np.arcsin(
                        np.clip(-mesh.face_normals[g][:, 2], -1, 1))).max())})
    return out


def main():
    args = sys.argv[1:]
    allow_path = "scripts/overhang_allow.json"
    if "--allow" in args:
        i = args.index("--allow")
        allow_path = args[i + 1]
        del args[i:i + 2]
    limit = LIMIT
    if "--limit" in args:
        i = args.index("--limit")
        limit = float(args[i + 1])
        del args[i:i + 2]
    report = "--report" in args
    args = [a for a in args if a != "--report"]
    allow = json.load(open(allow_path)) if os.path.exists(allow_path) else []
    used = set()
    failed = 0
    for path in args:
        part = os.path.basename(path)[:-4]
        mesh = trimesh.load_mesh(path)
        for r in regions(mesh, limit):
            if r["bridge"]:
                if report:
                    print(f"bridge   {part}: {r['area'] / 100:.1f} cm², {r['width']:.1f} mm wide at {r['centroid']}")
                continue
            hit = next((k for k, a in enumerate(allow) if a["part"] == part and all(
                a["lo"][j] <= r["centroid"][j] <= a["hi"][j] for j in range(3))), None)
            tag = f"{part}: {r['area'] / 100:.1f} cm² up to {r['max_angle']:.0f}° at {r['centroid']} box {r['lo']}..{r['hi']}"
            if hit is None:
                failed += 1
                print("OVERHANG", tag)
            else:
                used.add(hit)
                if report:
                    print("allowed ", tag, "-", allow[hit]["why"])
    checked = {os.path.basename(p)[:-4] for p in args}
    for k, a in enumerate(allow):
        if a["part"] in checked and k not in used:
            print(f"NOTE: allow entry {k} ({a['part']}: {a['why']}) matches nothing any more")
    print(f"overhang: {len(args)} parts, {failed} unsupported region(s) over {MIN_AREA / 100:.0f} cm² at > {limit:.0f}°")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
