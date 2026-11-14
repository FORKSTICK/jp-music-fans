# -*- coding: utf-8 -*-
"""压缩 public/walls 下已上传的壁纸：统一转 WebP（最长边 1920，q80），并更新 manifest。"""
import io, json, os, shutil, sys, time
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLS = os.path.join(ROOT, "public", "walls")
MAN = os.path.join(WALLS, "manifest.json")
MAX_SIDE = 1920
QUALITY = 80
RASTER = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

def main():
    m = json.load(io.open(MAN, encoding="utf-8"))
    backup = os.path.join(ROOT, "archive", "walls-original-%s" % time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(backup, exist_ok=True)
    total_before = total_after = 0
    for it in m.get("items", []):
        src = it.get("src", "")
        src = src.lstrip("/")
        if not src.startswith("walls/"):
            continue
        name = src[len("walls/"):]
        path = os.path.join(WALLS, name)
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in RASTER:
            continue
        before = os.path.getsize(path)
        total_before += before
        try:
            im = Image.open(path)
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            w, h = im.size
            scale = min(1.0, MAX_SIDE / float(max(w, h)))
            if scale < 1.0:
                im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
            out_name = os.path.splitext(name)[0] + ".webp"
            out_path = os.path.join(WALLS, out_name)
            im.save(out_path, "WEBP", quality=QUALITY, method=6)
            after = os.path.getsize(out_path)
            total_after += after
            if out_name != name:
                shutil.move(path, os.path.join(backup, name))
                it["src"] = "/walls/" + out_name
            print("%-28s %7.1fKB -> %6.1fKB" % (name, before / 1024.0, after / 1024.0))
        except Exception as e:
            print("skip", name, e)
    json.dump(m, io.open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("TOTAL %.1fMB -> %.1fMB (backup: %s)" % (total_before / 1048576.0, total_after / 1048576.0, backup))

if __name__ == "__main__":
    main()
