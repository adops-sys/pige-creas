from PIL import Image, ImageSequence
import io

def read_gif_all_frames(file_bytes: bytes):
    im = Image.open(io.BytesIO(file_bytes))
    frames, durations = [], []
    for frame in ImageSequence.Iterator(im):
        dur = frame.info.get("duration", 100)
        durations.append(int(dur))
        frames.append(frame.convert("RGBA"))
    width, height = im.size
    meta = {"width": width, "height": height, "n_frames": len(frames), "loop": im.info.get("loop", 0), "format": "GIF"}
    return frames, durations, meta

def save_gif(frames, durations_ms, loop=0):
    buf = io.BytesIO()
    first = frames[0].convert("P", palette=Image.ADAPTIVE)
    rest = [f.convert("P", palette=Image.ADAPTIVE) for f in frames[1:]]
    first.save(buf, format="GIF", save_all=True, append_images=rest, duration=durations_ms, loop=loop, disposal=2)
    return buf.getvalue()
