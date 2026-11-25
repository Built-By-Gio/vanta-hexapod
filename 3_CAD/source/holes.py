import trimesh, numpy as np

def find_holes(m, rmin=2.05, rmax=2.4, step=0.3):
    found=[]
    for ax in range(3):
        n=np.zeros(3); n[ax]=1
        o=[i for i in range(3) if i!=ax]
        lo,hi=m.bounds[0,ax],m.bounds[1,ax]
        cands={}
        for lv in np.arange(lo+0.1,hi,step):
            s=m.section(plane_origin=n*lv,plane_normal=n)
            if s is None: continue
            p2,T=s.to_2D()
            for poly in p2.polygons_full:
                for ring in poly.interiors:
                    pts=np.array(ring.coords)[:-1]
                    if len(pts)<8: continue
                    c2=pts.mean(0); r=np.linalg.norm(pts-c2,axis=1)
                    if r.std()<0.08 and rmin<r.mean()<rmax:
                        c=trimesh.transform_points([[c2[0],c2[1],0]],T)[0]
                        key=(round(c[o[0]]),round(c[o[1]]))
                        cands.setdefault(key,[]).append((lv,c,r.mean()))
        for key,v in cands.items():
            c=np.mean([x[1] for x in v],0); r=np.mean([x[2] for x in v])
            lv=[x[0] for x in v]
            found.append(dict(ax=ax,c=c,r=r,z0=min(lv)-step,z1=max(lv)+step,n=len(v)))
    return found
