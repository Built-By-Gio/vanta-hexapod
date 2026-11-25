"""Reference models (boards, Pi, camera) from body2 as STLs for the rig export."""
import os, tempfile, trimesh
from build123d import export_stl
import body2 as B


def tm(shapes):
    out = []
    for s in (shapes if isinstance(shapes, list) else [shapes]):
        t = os.path.join(tempfile.gettempdir(), "_r.stl"); export_stl(s, t); out.append(trimesh.load(t))
    return trimesh.util.concatenate(out)


if __name__ == "__main__":
    for n, s in (("ref_pca", B.pca_dummy()), ("ref_mods", B.module_dummies()), ("ref_pi", B.pi_dummy()), ("ref_cam", B.cam_dummy())):
        tm(s).export(f"out/{n}.stl"); print(n)
