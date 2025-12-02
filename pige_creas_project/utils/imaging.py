from PIL import Image, ImageDraw, ImageFont

def resize_frames(frames, target_w, target_h):
    return [f.resize((target_w, target_h), Image.LANCZOS) for f in frames]

def overlay_text(frames, text, xy=(10,10), fill=(255,255,255,255), font_size=16):
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    out = []
    for f in frames:
        im = f.copy()
        d = ImageDraw.Draw(im)
        d.text(xy, text, fill=fill, font=font)
        out.append(im)
    return out
