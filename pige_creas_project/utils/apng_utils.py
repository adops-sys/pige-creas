import io
from apng import APNG
from PIL import Image

def read_apng_all_frames(file_bytes: bytes):
    bio = io.BytesIO(file_bytes)
    apng = APNG.open(bio)
    frames, durations = [], []
    width = height = None
    for png, control in apng.frames:
        img = Image.open(io.BytesIO(png.to_bytes())).convert("RGBA")
        if width is None:
            width, height = img.size
        frames.append(img)
        delay_ms = int((control.delay / control.delay_den) * 1000) if hasattr(control, "delay_den") else int(control.delay)
        durations.append(max(10, delay_ms))
    meta = {"width": width, "height": height, "n_frames": len(frames), "format": "APNG"}
    return frames, durations, meta

def save_apng(frames, durations_ms, loop=0):
    apng = APNG()
    for img, d in zip(frames, durations_ms):
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)
        apng.append_file(bio, delay=d)
    apng.num_plays = loop
    out = io.BytesIO()
    apng.save(out)
    return out.getvalue()
