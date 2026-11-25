import os, time, zipfile
import adsk.core, adsk.fusion

BASE = os.path.join(os.path.expanduser("~"), "Documents", "Vanta Prototyping", "deck_refs")
SRC = os.path.join(BASE, "inplace")


def run(names):
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    F = root.features
    if not os.path.isdir(SRC):
        zipfile.ZipFile(os.path.join(BASE, "vanta_inplace.zip")).extractall(SRC)
    if names == "all":
        names = sorted(f[:-4] for f in os.listdir(SRC))
    G = adsk.fusion.MeshGenerateFaceGroupsMethodTypes
    C = adsk.fusion.MeshConvertMethodTypes
    t0 = time.time()
    for n in names:
        if root.bRepBodies.itemByName(n):
            continue
        bf = F.baseFeatures.add()
        bf.name = n + " mesh"
        bf.startEdit()
        root.meshBodies.add(os.path.join(SRC, n + ".stl"), adsk.fusion.MeshUnits.MillimeterMeshUnit, bf)
        bf.finishEdit()
        m = root.meshBodies.item(root.meshBodies.count - 1)
        m.name = n + "_mesh"
        how = None
        for gm, cm in ((G.AccurateGenerateFaceGroupsType, C.PrismaticMeshConvertMethodType),
                       (G.FastGenerateFaceGroupsType, C.PrismaticMeshConvertMethodType),
                       (None, C.FacetedMeshConvertMethodType)):
            try:
                if gm is not None:
                    gi = F.meshGenerateFaceGroupsFeatures.createInput(m)
                    gi.meshGenerateFaceGroupsMethodType = gm
                    F.meshGenerateFaceGroupsFeatures.add(gi)
                    m = root.meshBodies.item(root.meshBodies.count - 1)
                inp = F.meshConvertFeatures.createInput([m])
                inp.meshConvertMethodType = cm
                f = F.meshConvertFeatures.add(inp)
                how = "accurate" if gm == G.AccurateGenerateFaceGroupsType else "fast" if gm is not None else "FACETED"
                break
            except RuntimeError:
                continue
        if how is None:
            print(n, "FAILED")
            continue
        for i in range(f.bodies.count):
            f.bodies.item(i).name = n if i == 0 else f"{n}_{i}"
        b = f.bodies.item(0)
        for i in range(root.meshBodies.count):
            root.meshBodies.item(i).isLightBulbOn = False
        print(n, how, "faces", b.faces.count, "solid", b.isSolid, "bodies", f.bodies.count)
    print("secs", round(time.time() - t0, 1), "solids", root.bRepBodies.count)
