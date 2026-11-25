# VANTA assembly film: how it was made

Pipeline (all paths inside the scripts point at a scratch folder; change `S` at the top of each file to this folder):

1. `vanta_steps.py`: the 23 segments (title, explode, rules, parts, steps 1-18, outro), their text, camera, fly-in groups, durations. 24 fps, 8486 frames, 5.9 min.
2. `bl_build.py`: run with Blender 5.2 headless. Imports `3_CAD/VANTA_standing.glb`, keyframes the assembly (hide/show, fly-ins from exploded offsets, red colour on new parts, procedural camera), writes `timeline.json` (with per-frame 2D anchors for the callout leader lines) and renders transparent Workbench PNG frames.
   `blender -b --python bl_build.py -- test` (sample frames)   `blender -b --python bl_build.py -- render` (all frames)
3. `post.py`: Python 3.13 + numpy + Pillow. Halftones each render onto paper and draws the poster overlays (tag, headline, GRAB panel, DO callouts, CHECK quote, numeral, red word, side text).
   `python post.py all`
4. `bl_encode.py`: Blender's sequencer encodes the JPEG frames to H.264 MP4.
   `blender -b --python bl_encode.py -- <out dir> VANTA_assembly_video.mp4`

Fonts (OFL): Playfair Display (variable), Old Standard TT, Space Mono, Anton.
