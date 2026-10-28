"""Slice the saved Orca projects headlessly to prove every plate fits its printer's bed.

usage: python3 -I scripts/orca_check.py [--orca path/to/OrcaSlicer.AppImage]

  tars4.3mf       Ender 3 (220 x 220), the hand-arranged 5-plate project, user presets
                  "Creality Ender-3 0.4" + "0.20mm PETG @Ender3"
  tars4_cr10.3mf  CR-10 V2 (300 x 300), the one-piece parts on one plate, user preset
                  "Creality CR-10 V2 0.4 nozzle - Default" + system "0.20mm Standard @Creality CR10V2"

The layouts are the saved projects, never re-arranged: their meshes are refreshed in place from stl/ by
tools/update_orca_project.py (positions, rotations and plates kept, a backup of the old file goes to backups/).
tars4_cr10.3mf is created once, from the stl2_3mf.py strip layout, if it does not exist yet; arrange it in Orca
and save, the layout then survives every regeneration. Orca's own auto-arrange is off (--arrange 0).
Fails when a project lists an object on no plate, when Orca refuses a plate (part off the bed, G-code in an
unprintable area, ...) or when a plate produces no G-code. Slicing output goes to build/orca/.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "orca")
PROJECTS = [
    {"file": "tars4.3mf", "printer": "Creality Ender-3 0.4", "process": "0.20mm PETG @Ender3", "filament": None},
    {"file": "tars4_cr10.3mf", "printer": "Creality CR-10 V2 0.4 nozzle - Default",
     "process": "0.20mm Standard @Creality CR10V2", "filament": "Amazon Basics PETG Red",
     "seed": ["cr10_leg_left=stl/tars4_cr10_col0.stl", "cr10_mid_left=stl/tars4_cr10_col1.stl",
              "cr10_mid_right=stl/tars4_cr10_col2.stl", "cr10_leg_right=stl/tars4_cr10_col3.stl",
              "cr10_lid_leg_left=stl/tars4_cr10_lid_leg_sd.stl", "cr10_lid_mid_left=stl/tars4_cr10_lid_mid_left.stl",
              "cr10_lid_mid_right=stl/tars4_cr10_lid_mid.stl", "cr10_lid_leg_right=stl/tars4_cr10_lid_leg.stl"]},
]


def find_orca():
    if "--orca" in sys.argv:
        return sys.argv[sys.argv.index("--orca") + 1]
    if os.environ.get("ORCA"):
        return os.environ["ORCA"]
    for pat in ["~/Bureau/OrcaSlicer*.AppImage", "~/Desktop/OrcaSlicer*.AppImage", "~/Téléchargements/OrcaSlicer*.AppImage",
                "~/Downloads/OrcaSlicer*.AppImage", "~/Applications/OrcaSlicer*.AppImage"]:
        hits = sorted(glob.glob(os.path.expanduser(pat)))
        if hits:
            return hits[-1]
    exe = shutil.which("orca-slicer")
    if exe:
        return exe
    sys.exit("orca_check: OrcaSlicer not found (set ORCA=/path/to/OrcaSlicer.AppImage)")


def run(cmd, log, cwd):
    with open(log, "w") as fh:
        return subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, timeout=1800).returncode


def profiles(p, d):
    files = []
    for kind in ("machine", "process", "filament"):
        name = p["printer" if kind == "machine" else kind]
        if name:
            f = os.path.join(d, kind + ".json")
            subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "orca_profile.py"), kind, name, f], check=True)
            files.append(f)
    return files


def plate_objects(path):
    z = zipfile.ZipFile(path)
    model = z.read("3D/3dmodel.model").decode()
    items = set(re.findall(r'<item objectid="(\d+)"', model))
    cfg = z.read("Metadata/model_settings.config").decode() if "Metadata/model_settings.config" in z.namelist() else ""
    plates = re.findall(r"<plate>(.*?)</plate>", cfg, re.S)
    on = [set(re.findall(r'key="object_id" value="(\d+)"', pl)) for pl in plates]
    names = dict(re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', cfg))
    return items, on, names


def main():
    orca = find_orca()
    failed = []
    for p in PROJECTS:
        d = os.path.join(OUT, p["file"][:-4])
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        files = profiles(p, d)
        proj = os.path.join(ROOT, p["file"])
        base = ["--arrange", "0", "--orient", "0", "--load-settings", ";".join(f for f in files if "filament" not in f)]
        if p["filament"]:
            base += ["--load-filaments", files[-1]]
        if not os.path.exists(proj):
            # first run: seed the saved layout from the strip packer, written as an Orca project
            seed = os.path.join(d, "seed.3mf")
            subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "stl2_3mf.py"), seed, "300", "300"] + p["seed"],
                           cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
            rc = run([orca] + base + ["--export-3mf", os.path.basename(proj), "--outputdir", d, seed], os.path.join(d, "seed.log"), d)
            if rc or not os.path.exists(os.path.join(d, os.path.basename(proj))):
                failed.append(f"{p['file']}: could not create the project (Orca exit {rc})")
                continue
            shutil.move(os.path.join(d, os.path.basename(proj)), proj)
            print(f"   {p['file']}: created from the strip layout (arrange it in Orca if you like, it is kept)")
        else:
            chk = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "update_orca_project.py"), proj, "--check"],
                                 cwd=ROOT, capture_output=True, text=True)
            if "UPDATED" in chk.stdout:
                subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "update_orca_project.py"), proj],
                               cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
                print(f"   {p['file']}: meshes refreshed from stl/ (layout kept): "
                      + ", ".join(l.split()[0] for l in chk.stdout.splitlines() if "UPDATED" in l))
            for l in chk.stdout.splitlines():
                if l.startswith("NOTE"):
                    failed.append(f"{p['file']}: {l}")

        items, on, names = plate_objects(proj)
        # a single-plate project may list no instance at all: everything is then on plate 1
        loose = items - set().union(*on) if any(on) else set()
        for oid in sorted(loose):
            failed.append(f"{p['file']}: object {names.get(oid, oid)} is on no plate")

        rc = run([orca] + base + ["--slice", "0", "--outputdir", d, proj], os.path.join(d, "slice.log"), d)
        res = os.path.join(d, "result.json")
        r = json.load(open(res)) if os.path.exists(res) else {"return_code": rc, "error_string": "no result.json"}
        n_plates = max(len(on), 1)
        gcodes = sorted(glob.glob(os.path.join(d, "plate_*.gcode")))
        warn = [f"plate {s['id']}: {s['warning_message']}" for s in r.get("sliced_plates", []) if s.get("warning_message")]
        if rc or r.get("return_code"):
            failed.append(f"{p['file']} ({p['printer']}): Orca exit {rc}, {r.get('return_code')} {r.get('error_string')}"
                          f" (plate {r.get('plate_index')}, log {os.path.relpath(d, ROOT)}/slice.log)")
        elif len(gcodes) != n_plates:
            failed.append(f"{p['file']}: {len(gcodes)} G-code files for {n_plates} plates")
        else:
            print(f"   {p['file']} on {p['printer']}: {n_plates} plate(s) sliced, all on the bed" + ("; " + "; ".join(warn) if warn else ""))
    for f in failed:
        print("ORCA", f)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
