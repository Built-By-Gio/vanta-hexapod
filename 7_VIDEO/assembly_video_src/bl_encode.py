"""blender -b --python bl_encode.py -- <frames dir> <out.mp4>"""
import bpy, os, sys
d, out = sys.argv[sys.argv.index("--") + 1:][:2]
files = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
sc = bpy.context.scene
if hasattr(sc.render.image_settings, "media_type"): sc.render.image_settings.media_type = "VIDEO"
sc.render.image_settings.file_format = "FFMPEG"
ff = sc.render.ffmpeg
ff.format = "MPEG4"; ff.codec = "H264"; ff.constant_rate_factor = "HIGH"; ff.ffmpeg_preset = "GOOD"; ff.gopsize = 24; ff.audio_codec = "NONE"
sc.render.fps = 24; sc.render.fps_base = 1.0
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
for o in list(sc.objects): bpy.data.objects.remove(o)
sc.sequence_editor_create(); se = sc.sequence_editor
coll = se.strips if hasattr(se, "strips") else se.sequences
strip = coll.new_image(name="film", filepath=os.path.join(d, files[0]), channel=1, frame_start=1)
for f in files[1:]: strip.elements.append(f)
sc.frame_start, sc.frame_end = 1, len(files)
sc.render.use_sequencer = True
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = 0.0; sc.view_settings.gamma = 1.0
sc.sequencer_colorspace_settings.name = "sRGB"
if hasattr(sc.render.image_settings, "color_management"): sc.render.image_settings.color_management = "FOLLOW_SCENE"
sc.render.filepath = out
bpy.ops.render.render(animation=True)
print("encoded", len(files), "frames ->", out)


