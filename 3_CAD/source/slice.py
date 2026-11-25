import subprocess, re, sys, os, tempfile, shutil
PS = shutil.which('prusa-slicer-console') or shutil.which('prusa-slicer') or r'C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe'
def grams(stl, walls=3, infill=15, layer=0.2, support=False, top=4, bottom=3):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'o.gcode')
        cmd = [PS, '--export-gcode', stl, '-o', out, '--layer-height', str(layer), '--perimeters', str(walls),
               '--fill-density', f'{infill}%', '--fill-pattern', 'gyroid', '--top-solid-layers', str(top), '--bottom-solid-layers', str(bottom),
               '--nozzle-diameter', '0.4', '--filament-diameter', '1.75', '--bed-shape', '0x0,256x256x', '--center', '128,128',
               '--filament-density', '1.24', '--dont-arrange']
        if support: cmd += ['--support-material', '--support-material-style', 'organic']
        cmd[cmd.index('--bed-shape') + 1] = '0x0,256x0,256x256,0x256'
        r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'})
        if not os.path.exists(out): return r.stderr[-400:]
        g = open(out).read()
        mm = re.search(r'filament used \[g\] = ([\d.]+)', g)
        t = re.search(r'estimated printing time \(normal mode\) = (.*)', g)
        return float(mm.group(1)), t.group(1).strip()
if __name__ == '__main__':
    print(grams(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3))
